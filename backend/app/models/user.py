"""User model definition.

This module defines the User SQLModel for user ownership reference.
Users are managed externally (via Better Auth or similar), so this
model primarily exists to support foreign key relationships with
tasks and categories.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.category import Category
    from app.models.tag import Tag
    from app.models.recurring_series import RecurringTaskSeries
    from app.models.task_reminder import TaskReminder


class User(SQLModel, table=True):
    """User model for ownership reference.
    
    Using explicitly quoted tablename to avoid PostgreSQL reserved keyword issues.
    """
    __tablename__ = "user"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), default=datetime.utcnow),
    )

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="user")
    categories: list["Category"] = Relationship(back_populates="user")
    tags: list["Tag"] = Relationship(back_populates="user")
    recurring_series: list["RecurringTaskSeries"] = Relationship(back_populates="user")
    reminders: list["TaskReminder"] = Relationship(back_populates="user")

    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(id={self.id}, email={self.email})>"
