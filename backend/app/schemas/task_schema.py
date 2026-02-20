"""Task Pydantic schemas for request/response validation."""

from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Import enums directly from sqlmodel for consistency
from sqlmodel import Enum

from app.models.task import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    """Base task schema with common fields."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    category_id: Optional[UUID] = None
    due_date: Optional[date] = None
    reminder_config: Optional[dict] = None
    recurrence_rule: Optional[dict] = None
    recurrence_series_id: Optional[UUID] = None


class TaskCreate(TaskBase):
    """Schema for creating a new task."""

    model_config = ConfigDict(from_attributes=True)
    status: TaskStatus = TaskStatus.PENDING
    tag_ids: Optional[List[UUID]] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task.

    All fields are optional - only provided fields will be updated.
    """

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    category_id: Optional[UUID] = None
    due_date: Optional[date] = None
    status: Optional[TaskStatus] = None
    reminder_config: Optional[dict] = None
    recurrence_rule: Optional[dict] = None
    tag_ids: Optional[List[UUID]] = None

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(TaskBase):
    """Schema for task data in responses."""

    id: UUID
    user_id: UUID
    status: TaskStatus
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    category_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """Schema for paginated task list responses."""

    tasks: list[TaskResponse]
    total: int
    limit: int
    offset: int


class SearchRequest(BaseModel):
    """Schema for advanced search request."""

    query: str = ""
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    category_id: Optional[UUID] = None
    tag_ids: Optional[List[UUID]] = None
    limit: int = 50
    offset: int = 0


class SearchResponse(BaseModel):
    """Schema for search results."""

    items: List[TaskResponse]
    total: int
    query: str
    limit: int
    offset: int
