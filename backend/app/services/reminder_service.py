"""Reminder service for managing task reminders using Dapr."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, and_
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.models.task_reminder import TaskReminder
from app.dapr_client import get_dapr_client
from app.events.publisher import get_publisher

logger = logging.getLogger(__name__)

class ReminderService:
    """Service for managing task reminders."""

    def __init__(self, db: Session, user_id: UUID):
        self.db = db
        self.user_id = user_id
        self.dapr = get_dapr_client()

    async def schedule_reminder(self, task_id: UUID, remind_at: datetime) -> TaskReminder:
        """Schedule a new reminder for a task."""
        # Create database record
        reminder = TaskReminder(
            task_id=task_id,
            user_id=self.user_id,
            scheduled_time=remind_at,
            status="pending"
        )
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)

        # Schedule with Dapr
        # Dapr reminders require an actor or a specific API. 
        # Here we use the generic reminder API if available.
        # Note: Dapr reminders typically target Actors. For simple scheduling, 
        # we might need an endpoint that Dapr calls back.
        
        # We'll use the reminder ID as the name for Dapr
        success = await self.dapr.schedule_reminder(
            name=f"reminder-{reminder.id}",
            due_time=remind_at,
            period="PT0S", # Trigger once
            callback=f"/api/v1/reminders/{reminder.id}/trigger",
            data={"task_id": str(task_id), "user_id": str(self.user_id)}
        )

        if not success:
            logger.error(f"Failed to schedule Dapr reminder for {reminder.id}")
            # We still have it in DB, fallback polling will pick it up
            
        return reminder

    async def cancel_reminder(self, reminder_id: UUID) -> bool:
        """Cancel an existing reminder."""
        reminder = self.db.execute(
            select(TaskReminder).where(
                TaskReminder.id == reminder_id,
                TaskReminder.user_id == self.user_id
            )
        ).scalar_one_or_none()

        if not reminder:
            return False

        # Cancel in Dapr
        await self.dapr.cancel_reminder(f"reminder-{reminder.id}")

        # Update DB
        self.db.delete(reminder)
        self.db.commit()
        return True

    async def acknowledge_reminder(self, reminder_id: UUID) -> bool:
        """Mark a reminder as acknowledged."""
        reminder = self.db.execute(
            select(TaskReminder).where(
                TaskReminder.id == reminder_id,
                TaskReminder.user_id == self.user_id
            )
        ).scalar_one_or_none()

        if not reminder:
            return False

        reminder.status = "acknowledged"
        reminder.acknowledged_at = datetime.utcnow()
        self.db.commit()
        return True

    def list_pending_reminders(self) -> List[TaskReminder]:
        """List all pending reminders for the user."""
        return list(self.db.execute(
            select(TaskReminder).where(
                TaskReminder.user_id == self.user_id,
                TaskReminder.status == "pending"
            )
        ).scalars().all())

    async def check_overdue_tasks(self):
        """Find tasks that are past their due date and mark them as overdue."""
        now = datetime.utcnow().date()
        
        # This belongs more to task service or a general background job
        # But per T078 we put it here
        stmt = (
            update(Task)
            .where(
                and_(
                    Task.user_id == self.user_id,
                    Task.due_date < now,
                    Task.status != TaskStatus.COMPLETED.value,
                    Task.status != TaskStatus.ARCHIVED.value
                )
            )
            .values(updated_at=datetime.utcnow())
        )
        self.db.execute(stmt)
        self.db.commit()

    async def process_due_reminders(self):
        """Fallback polling: Find and process reminders that should have fired."""
        now = datetime.utcnow()
        overdue_reminders = self.db.execute(
            select(TaskReminder).where(
                TaskReminder.status == "pending",
                TaskReminder.scheduled_time <= now
            )
        ).scalars().all()

        for reminder in overdue_reminders:
            logger.info(f"Processing overdue reminder {reminder.id} via fallback polling")
            await self.trigger_reminder(reminder.id)

    async def trigger_reminder(self, reminder_id: UUID):
        """Logic to deliver the reminder (in-app, email, etc)."""
        reminder = self.db.get(TaskReminder, reminder_id)
        if not reminder or reminder.status != "pending":
            return

        # Delivery logic (e.g., publish event for frontend to show toast)
        # For now, just mark as sent
        reminder.status = "sent"
        reminder.delivered_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Reminder {reminder_id} triggered and delivered.")
        # In a real app, we'd publish to Kafka or use SSE to notify frontend
        try:
            publisher = await get_publisher()
            await publisher.publish("notification_events", {
                "type": "Reminder",
                "user_id": str(reminder.user_id),
                "task_id": str(reminder.task_id),
                "title": f"Reminder for Task",
                "message": f"Your task is due soon.",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to publish reminder event: {e}")
