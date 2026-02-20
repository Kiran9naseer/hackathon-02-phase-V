"""Recurring service for managing task series and instances."""

import logging
from datetime import date, datetime, timedelta
from typing import List, Optional, Any
from uuid import UUID
from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.models.recurring_series import RecurringTaskSeries

logger = logging.getLogger(__name__)

class RecurringService:
    """Service for managing recurring task series."""

    def __init__(self, db: Session, user_id: UUID):
        """Initialize with DB session and user context."""
        self.db = db
        self.user_id = user_id

    def create_series(
        self,
        title: str,
        frequency: str,
        interval: int = 1,
        description: Optional[str] = None,
        priority: str = "medium",
        category_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> RecurringTaskSeries:
        """
        Create a new recurring task series and schedule the first instance.
        """
        try:
            if not start_date:
                start_date = date.today()
    
            recurrence_rule = {
                "frequency": frequency,
                "interval": interval
            }
    
            series = RecurringTaskSeries(
                user_id=self.user_id,
                title=title,
                description=description,
                priority=priority,
                category_id=category_id,
                recurrence_rule=recurrence_rule,
                start_date=start_date,
                end_date=end_date,
            )
    
            self.db.add(series)
            self.db.commit()
            self.db.refresh(series)
    
            # Create the first instance on the start date
            self._create_task_instance(series, start_date)
            
            logger.info(f"Recurring series {series.id} created for user {self.user_id}")
            return series
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating recurring series: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    def _create_task_instance(self, series: RecurringTaskSeries, due_date: date) -> Task:
        """Helper to create a task instance from a series."""
        next_task = Task(
            user_id=self.user_id,
            title=series.title,
            description=series.description,
            priority=series.priority,
            category_id=series.category_id,
            due_date=due_date,
            recurrence_series_id=series.id
        )
        self.db.add(next_task)
        self.db.commit()
        self.db.refresh(next_task)
        return next_task

    def schedule_next_instance(self, series_id: UUID, last_date: date) -> Optional[Task]:
        """
        Calculate and create the next task instance in the series.
        """
        series = self.db.execute(
            select(RecurringTaskSeries).where(
                RecurringTaskSeries.id == series_id,
                RecurringTaskSeries.user_id == self.user_id
            )
        ).scalar_one_or_none()

        if not series or series.paused:
            return None

        rule = series.recurrence_rule
        freq = rule.get("frequency", "daily").lower()
        interval = rule.get("interval", 1)

        next_date = self._calculate_next_date(last_date, freq, interval)

        # Check if next date exceeds end_date
        if series.end_date and next_date > series.end_date:
            logger.info(f"Series {series_id} has reached its end date.")
            return None

        # Create the task instance
        next_task = self._create_task_instance(series, next_date)

        logger.info(f"Scheduled next instance for series {series_id} on {next_date}")
        return next_task

    def _calculate_next_date(self, current: date, freq: str, interval: int) -> date:
        """Helper to calculate the next date based on frequency."""
        if freq == "daily":
            return current + timedelta(days=interval)
        elif freq == "weekly":
            return current + timedelta(weeks=interval)
        elif freq == "monthly":
            # Rough estimation for monthly (add ~30 days * interval)
            # A more robust solution would handle month boundaries
            year = current.year + (current.month + interval - 1) // 12
            month = (current.month + interval - 1) % 12 + 1
            day = min(current.day, 28) # Safety for February/shorter months
            return date(year, month, day)
        elif freq == "yearly":
            return date(current.year + interval, current.month, min(current.day, 28))
        else:
            return current + timedelta(days=interval)
            
    def list_series(self) -> List[RecurringTaskSeries]:
        """List all recurring series for the user."""
        return list(self.db.execute(
            select(RecurringTaskSeries).where(RecurringTaskSeries.user_id == self.user_id)
        ).scalars().all())

    def toggle_pause(self, series_id: UUID, paused: bool) -> bool:
        """Pause or resume a recurring series."""
        series = self.db.execute(
            select(RecurringTaskSeries).where(
                RecurringTaskSeries.id == series_id,
                RecurringTaskSeries.user_id == self.user_id
            )
        ).scalar_one_or_none()
        
        if not series:
            return False
            
        series.paused = paused
        self.db.commit()
        logger.info(f"Series {series_id} {'paused' if paused else 'resumed'}.")
        return True

    def delete_series(self, series_id: UUID, delete_future_instances: bool = False) -> bool:
        """Delete a series and optionally clean up future task instances."""
        series = self.db.execute(
            select(RecurringTaskSeries).where(
                RecurringTaskSeries.id == series_id,
                RecurringTaskSeries.user_id == self.user_id
            )
        ).scalar_one_or_none()
        
        if not series:
            return False
            
        if delete_future_instances:
            # Delete pending tasks belonging to this series
            # We use a filter on status and recurrence_series_id
            self.db.execute(
                select(Task).where(
                    Task.recurrence_series_id == series_id,
                    Task.status == TaskStatus.PENDING.value
                )
            ).delete()
            
        self.db.delete(series)
        self.db.commit()
        logger.info(f"Series {series_id} deleted (future_instances={delete_future_instances}).")
        return True
