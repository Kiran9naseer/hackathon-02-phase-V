"""Category model definition with ownership and relationships."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task
    from app.models.recurring_series import RecurringTaskSeries


class Category(SQLModel, table=True):
    """Category model for organizing tasks.

    Attributes:
        id: Unique category identifier (UUID).
        user_id: Owning user's UUID (foreign key).
        name: Category name (required).
        description: Optional category description.
        created_at: Timestamp when category was created.
        updated_at: Timestamp when category was last updated.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    name: str = Field(max_length=100)
    description: str | None = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), default=datetime.utcnow),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), default=datetime.utcnow),
    )

    # Relationships
    user: "User" = Relationship(back_populates="categories")
    tasks: list["Task"] = Relationship(back_populates="category")
    recurring_series: list["RecurringTaskSeries"] = Relationship(back_populates="category")

    def __repr__(self) -> str:
        """String representation of the category."""
        return f"<Category(id={self.id}, name={self.name})>"
