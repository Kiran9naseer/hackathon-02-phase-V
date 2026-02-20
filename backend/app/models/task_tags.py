"""Task-Tag junction model for many-to-many relationship."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class TaskTag(SQLModel, table=True):
    """Junction table for many-to-many task-tag relationship.

    Attributes:
        task_id: Task UUID (foreign key, primary key).
        tag_id: Tag UUID (foreign key, primary key).
        created_at: Timestamp when association was created.
    """
    __tablename__ = "task_tags"

    task_id: UUID = Field(
        foreign_key="task.id",
        primary_key=True,
        ondelete="CASCADE"
    )
    tag_id: UUID = Field(
        foreign_key="tag.id",
        primary_key=True,
        ondelete="CASCADE"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), default=datetime.utcnow),
    )
