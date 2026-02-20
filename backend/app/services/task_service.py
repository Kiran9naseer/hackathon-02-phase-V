"""Task service implementing business logic with ownership enforcement.

This service handles all task-related operations with automatic
user ownership filtering on every query.
"""

import logging
from datetime import datetime, timedelta, date
from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.task import Task, TaskStatus
from app.models.task_tags import TaskTag
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.services.recurring_service import RecurringService
from app.services.reminder_service import ReminderService
from app.events.publisher import get_publisher

logger = logging.getLogger(__name__)


class TaskService:
    """Service class for task operations with ownership enforcement.

    All operations automatically filter by user_id to ensure
    users can only access their own tasks.
    """

    def __init__(self, db: Session, user_id: UUID):
        """Initialize the task service.

        Args:
            db: SQLAlchemy database session.
            user_id: The authenticated user's ID for ownership filtering.
        """
        self.db = db
        self.user_id = user_id

    def get(self, task_id: UUID) -> Task | None:
        """
        Get a task by ID with ownership check.

        Args:
            task_id: The task UUID to retrieve.

        Returns:
            Task if found and owned by user, None otherwise.
        """
        result = self.db.execute(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == self.user_id,
            )
        )
        task = result.scalar_one_or_none()
        if task:
            logger.info(f"Task {task_id} retrieved for user {self.user_id}")
        return task

    def list(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category_id: Optional[UUID] = None,
        tag_ids: Optional[List[UUID]] = None,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> dict:
        """
        List tasks with optional filtering and pagination.

        Args:
            status: Filter by task status.
            priority: Filter by priority level.
            category_id: Filter by category UUID.
            tag_ids: Filter by tag UUIDs (tasks must have ALL specified tags).
            limit: Maximum number of results.
            offset: Number of results to skip.
            sort_by: Field to sort by (created_at, updated_at, due_date, priority, title).
            sort_order: Sort order (asc or desc).

        Returns:
            dict with items, total, limit, and offset.
        """
        # Build base query with ownership filter
        base_query = select(Task).where(Task.user_id == self.user_id)

        # Apply optional filters
        if status:
            base_query = base_query.where(Task.status == status)

        if priority:
            base_query = base_query.where(Task.priority == priority)

        if category_id:
            base_query = base_query.where(Task.category_id == category_id)
        
        # Filter by tags (tasks must have ALL specified tags)
        if tag_ids:
            for tag_id in tag_ids:
                base_query = base_query.where(
                    Task.id.in_(
                        select(TaskTag.task_id).where(TaskTag.tag_id == tag_id)
                    )
                )

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total = self.db.execute(count_query).scalar() or 0

        # Apply sorting
        sort_column = getattr(Task, sort_by, Task.created_at)
        if sort_order.lower() == "desc":
            base_query = base_query.order_by(sort_column.desc())
        else:
            base_query = base_query.order_by(sort_column.asc())

        # Apply ordering and pagination
        query = (
            base_query
            .offset(offset)
            .limit(limit)
        )

        tasks = list(self.db.execute(query).scalars().all())

        logger.info(
            f"Listed {len(tasks)} tasks for user {self.user_id} "
            f"(total: {total}, offset: {offset}, limit: {limit})"
        )

        return {
            "tasks": tasks,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def create(self, task_data: TaskCreate, tag_ids: Optional[List[UUID]] = None) -> Task:
        """
        Create a new task with automatic user_id assignment.

        Args:
            task_data: Task creation data.
            tag_ids: Optional list of tag UUIDs to associate with the task.

        Returns:
            Created Task instance.
        """
        task = Task(
            user_id=self.user_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority.value if hasattr(task_data.priority, 'value') else task_data.priority,
            category_id=task_data.category_id,
            due_date=task_data.due_date,
            status=task_data.status.value if hasattr(task_data.status, 'value') else task_data.status,
        )

        self.db.add(task)
        # Apply additional fields from TaskCreate
        if task_data.reminder_config:
            task.reminder_config = task_data.reminder_config
        if task_data.recurrence_rule:
            task.recurrence_rule = task_data.recurrence_rule
        if task_data.recurrence_series_id:
            task.recurrence_series_id = task_data.recurrence_series_id

        self.db.commit()
        self.db.refresh(task)
        
        # Schedule reminders if provided
        if task.due_date and task.reminder_config:
            async_reminder_service = ReminderService(self.db, self.user_id)
            offsets = task.reminder_config.get("offsets", [])
            for offset in offsets:
                # offset is in minutes, usually negative (e.g. -1440 for 1 day before)
                remind_at = datetime.combine(task.due_date, datetime.min.time()) + timedelta(minutes=offset)
                if remind_at > datetime.utcnow():
                    import asyncio
                    # We can't easily use await in this sync service without restructuring
                    # For now we'll just create the DB records, background polling or Dapr will handle it
                    # In a production app, we'd use a background task or event bus
                    from app.models.task_reminder import TaskReminder
                    reminder = TaskReminder(
                        task_id=task.id,
                        user_id=self.user_id,
                        scheduled_time=remind_at,
                        reminder_type=task.reminder_config.get("type", "in_app"),
                        offset_minutes=offset,
                        status="pending"
                    )
                    self.db.add(reminder)
            self.db.commit()
            self.db.refresh(task)
        
        # Associate tags if provided
        if tag_ids:
            for tag_id in tag_ids:
                task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
                self.db.add(task_tag)
            self.db.commit()
            self.db.refresh(task)

        # Publish Event
        import asyncio
        asyncio.create_task(self._publish_task_event("TaskCreated", task))

        logger.info(f"Task {task.id} created for user {self.user_id} with {len(tag_ids or [])} tags")
        return task

    async def _publish_task_event(self, event_type: str, task: Task):
        """Helper to publish task events asynchronously."""
        try:
            publisher = await get_publisher()
            await publisher.publish("task_events", {
                "type": event_type,
                "user_id": str(self.user_id),
                "task_id": str(task.id),
                "title": task.title,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to publish {event_type} event: {e}")

    def update(self, task_id: UUID, task_data: TaskUpdate, tag_ids: Optional[List[UUID]] = None) -> Task | None:
        """
        Update a task with ownership check.

        Args:
            task_id: The task UUID to update.
            task_data: Update data (only provided fields are updated).
            tag_ids: Optional list of tag UUIDs to replace existing tags.

        Returns:
            Updated Task if found and owned, None otherwise.
        """
        task = self.get(task_id)
        if not task:
            return None

        # Update only provided fields
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "tag_ids":
                continue
            # Handle enum values
            if hasattr(value, 'value'):
                value = value.value
            setattr(task, field, value)

        task.updated_at = datetime.utcnow()
        
        # Update tags if provided
        if tag_ids is not None:
            # Remove existing tag associations
            self.db.query(TaskTag).filter(TaskTag.task_id == task_id).delete()
            
            # Add new tag associations
            for tag_id in tag_ids:
                task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
                self.db.add(task_tag)

        self.db.commit()
        self.db.refresh(task)

        # Publish Event
        import asyncio
        asyncio.create_task(self._publish_task_event("TaskUpdated", task))

        logger.info(f"Task {task_id} updated for user {self.user_id}")
        return task

    def delete(self, task_id: UUID) -> bool:
        """
        Delete a task with ownership check.

        Args:
            task_id: The task UUID to delete.

        Returns:
            True if task was deleted, False if not found or not owned.
        """
        task = self.get(task_id)
        if not task:
            return False

        self.db.delete(task)
        self.db.commit()

        # Publish Event
        import asyncio
        asyncio.create_task(self._publish_task_event("TaskDeleted", task))

        logger.info(f"Task {task_id} deleted for user {self.user_id}")
        return True

    def complete(self, task_id: UUID) -> Task | None:
        """
        Mark a task as complete with ownership check.

        Args:
            task_id: The task UUID to complete.

        Returns:
            Updated Task if found and owned, None otherwise.
        """
        task = self.get(task_id)
        if not task:
            return None

        task.complete()
        self.db.commit()
        self.db.refresh(task)

        # Trigger next instance for recurring tasks
        if task.recurrence_series_id:
            recurring_service = RecurringService(self.db, self.user_id)
            recurring_service.schedule_next_instance(task.recurrence_series_id, task.due_date or date.today())

        # Publish Event
        import asyncio
        asyncio.create_task(self._publish_task_event("TaskCompleted", task))

        logger.info(f"Task {task_id} marked complete for user {self.user_id}")
        return task
