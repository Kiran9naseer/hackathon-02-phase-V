"""Reminder schemas for request/response validation."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ReminderCreate(BaseModel):
    """Schema for creating a new reminder."""
    task_id: UUID
    offset_minutes: int = Field(default=-1440)  # Default: 1 day before
    reminder_type: str = Field(default="in_app", max_length=10)

    @field_validator('offset_minutes')
    @classmethod
    def validate_offset(cls, v):
        """Validate offset is reasonable."""
        if v < -10080:  # More than 7 days before
            raise ValueError('Reminder offset cannot be more than 7 days before due date')
        return v

    @field_validator('reminder_type')
    @classmethod
    def validate_reminder_type(cls, v):
        """Validate reminder type."""
        allowed_types = ['in_app', 'email', 'both']
        if v not in allowed_types:
            raise ValueError(f'Reminder type must be one of: {", ".join(allowed_types)}')
        return v


class ReminderUpdate(BaseModel):
    """Schema for updating a reminder."""
    offset_minutes: Optional[int] = Field(default=None)
    reminder_type: Optional[str] = Field(default=None, max_length=10)
    status: Optional[str] = Field(default=None, max_length=20)


class ReminderResponse(BaseModel):
    """Schema for reminder response."""
    id: UUID
    user_id: UUID
    task_id: UUID
    scheduled_time: datetime
    reminder_type: str
    offset_minutes: int
    status: str
    delivered_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReminderListResponse(BaseModel):
    """Schema for paginated reminder list response."""
    items: list[ReminderResponse]
    total: int
    limit: int
    offset: int


class ReminderConfig(BaseModel):
    """Schema for reminder configuration on task."""
    offsets: List[int] = Field(default=[-1440])  # Minutes before due date
    reminder_type: str = Field(default="in_app", max_length=10)

    @field_validator('offsets')
    @classmethod
    def validate_offsets(cls, v):
        """Validate reminder offsets."""
        if not v:
            raise ValueError('At least one reminder offset required')
        if len(v) > 5:
            raise ValueError('Maximum 5 reminders per task')
        return v

    @field_validator('reminder_type')
    @classmethod
    def validate_reminder_type(cls, v):
        """Validate reminder type."""
        allowed_types = ['in_app', 'email', 'both']
        if v not in allowed_types:
            raise ValueError(f'Reminder type must be one of: {", ".join(allowed_types)}')
        return v
