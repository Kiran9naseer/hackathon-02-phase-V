"""TaskReminder model for scheduled task reminders."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Text, Integer, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task


class TaskReminder(SQLModel, table=True):
    """Task reminder with scheduling and delivery tracking.

    Attributes:
        id: Unique reminder identifier (UUID).
        user_id: Owning user's UUID (foreign key).
        task_id: Associated task UUID (foreign key).
        scheduled_time: When reminder should trigger.
        reminder_type: Delivery method (email/in_app/both).
        offset_minutes: Minutes before due date (negative = before).
        status: Current delivery status (pending/sent/acknowledged/failed).
        delivered_at: When reminder was sent.
        acknowledged_at: When user acknowledged reminder.
        error_message: Error details if delivery failed.
        retry_count: Number of delivery attempts.
        created_at: Timestamp when reminder was created.
    """
    __tablename__ = "task_reminder"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    task_id: UUID = Field(foreign_key="task.id", index=True)
    scheduled_time: datetime = Field()
    reminder_type: str = Field(default="in_app", max_length=10)
    offset_minutes: int = Field(default=-1440)  # Default: 1 day before
    status: str = Field(default="pending", max_length=20)
    delivered_at: Optional[datetime] = Field(default=None)
    acknowledged_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    retry_count: int = Field(default=0)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), default=datetime.utcnow),
    )

    # Relationships
    user: "User" = Relationship(back_populates="reminders")
    task: "Task" = Relationship(back_populates="reminders")

    def __repr__(self) -> str:
        """String representation of the task reminder."""
        return f"<TaskReminder(id={self.id}, task_id={self.task_id}, status={self.status})>"
