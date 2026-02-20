"""RecurringTaskSeries model for automating routine task generation."""

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional, List
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Date, Boolean, Text, JSON as SQLJSON
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category
    from app.models.task import Task


class RecurringTaskSeries(SQLModel, table=True):
    """Recurring task series template for generating task instances.

    Attributes:
        id: Unique series identifier (UUID).
        user_id: Owning user's UUID (foreign key).
        title: Task title template (required).
        description: Task description template (optional).
        priority: Task priority (low/medium/high).
        category_id: Optional category UUID.
        recurrence_rule: JSONB-encoded recurrence rule.
        start_date: When recurrence starts (required).
        end_date: When recurrence ends (optional, None = indefinite).
        timezone: User's timezone for date calculations.
        paused: Whether recurrence is paused.
        created_at: Timestamp when series was created.
        updated_at: Timestamp when series was last updated.
    """
    __tablename__ = "recurring_task_series"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    priority: str = Field(default="medium", max_length=10)
    category_id: Optional[UUID] = Field(default=None, foreign_key="category.id", index=True)
    recurrence_rule: dict = Field(sa_column=Column("recurrence_rule", SQLJSON))
    start_date: date = Field(sa_column=Column(Date))
    end_date: Optional[date] = Field(default=None, sa_column=Column(Date))
    timezone: str = Field(default="UTC", max_length=50)
    paused: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), default=datetime.utcnow),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), default=datetime.utcnow),
    )

    # Relationships
    user: "User" = Relationship(back_populates="recurring_series")
    category: Optional["Category"] = Relationship(back_populates="recurring_series")
    tasks: List["Task"] = Relationship(back_populates="recurrence_series")

    def __repr__(self) -> str:
        """String representation of the recurring task series."""
        return f"<RecurringTaskSeries(id={self.id}, title={self.title})>"
