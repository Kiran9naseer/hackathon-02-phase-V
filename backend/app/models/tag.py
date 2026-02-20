"""Tag model definition for flexible task organization."""

from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User

# Import for link_model - must be at module level
from app.models.task_tags import TaskTag


class Tag(SQLModel, table=True):
    """Tag model for flexible task organization.

    Attributes:
        id: Unique tag identifier (UUID).
        user_id: Owning user's UUID (foreign key).
        name: Tag name (required, max 50 chars).
        color: Display color (hex format, default #8FBFB3).
        created_at: Timestamp when tag was created.
    """
    __tablename__ = "tag"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    name: str = Field(max_length=50, index=True)
    color: str = Field(default="#8FBFB3", max_length=7)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), default=datetime.utcnow),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=False), 
            default=datetime.utcnow, 
            onupdate=datetime.utcnow
        ),
    )

    # Relationships
    user: "User" = Relationship(back_populates="tags")
    tasks: List["Task"] = Relationship(back_populates="tags", link_model=TaskTag)

    def __repr__(self) -> str:
        """String representation of the tag."""
        return f"<Tag(id={self.id}, name={self.name})>"
