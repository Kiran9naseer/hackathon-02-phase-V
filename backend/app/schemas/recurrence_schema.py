"""Recurrence schemas for request/response validation."""

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class RecurrenceRule(BaseModel):
    """Schema for recurrence rule configuration."""
    frequency: str = Field(..., max_length=10)
    interval: int = Field(default=1, ge=1, le=365)
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)

    @field_validator('frequency')
    @classmethod
    def validate_frequency(cls, v):
        """Validate recurrence frequency."""
        allowed_frequencies = ['daily', 'weekly', 'monthly']
        if v not in allowed_frequencies:
            raise ValueError(f'Frequency must be one of: {", ".join(allowed_frequencies)}')
        return v

    @model_validator(mode='after')
    def validate_recurrence_rule(self):
        """Validate recurrence rule consistency."""
        if self.frequency == 'weekly' and self.day_of_week is None:
            raise ValueError('day_of_week required for weekly recurrence')
        if self.frequency == 'monthly' and self.day_of_month is None:
            raise ValueError('day_of_month required for monthly recurrence')
        return self


class RecurringSeriesCreate(BaseModel):
    """Schema for creating a new recurring task series."""
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(default=None)
    priority: str = Field(default="medium", max_length=10)
    category_id: Optional[UUID] = Field(default=None)
    recurrence_rule: RecurrenceRule
    start_date: date
    end_date: Optional[date] = Field(default=None)
    timezone: str = Field(default="UTC", max_length=50)

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        """Validate priority value."""
        allowed_priorities = ['low', 'medium', 'high']
        if v not in allowed_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(allowed_priorities)}')
        return v

    @model_validator(mode='after')
    def validate_dates(self):
        """Validate date range."""
        if self.end_date and self.end_date < self.start_date:
            raise ValueError('end_date must be after start_date')
        return self


class RecurringSeriesUpdate(BaseModel):
    """Schema for updating a recurring task series."""
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None)
    priority: Optional[str] = Field(default=None, max_length=10)
    category_id: Optional[UUID] = Field(default=None)
    recurrence_rule: Optional[RecurrenceRule] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    timezone: Optional[str] = Field(default=None, max_length=50)
    paused: Optional[bool] = Field(default=None)


class RecurringSeriesResponse(BaseModel):
    """Schema for recurring task series response."""
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    priority: str
    category_id: Optional[UUID]
    recurrence_rule: dict
    start_date: date
    end_date: Optional[date]
    timezone: str
    paused: bool
    created_at: str
    updated_at: str
    next_instance_date: Optional[date] = None

    class Config:
        from_attributes = True


class RecurringSeriesListResponse(BaseModel):
    """Schema for paginated recurring series list response."""
    items: list[RecurringSeriesResponse]
    total: int
    limit: int
    offset: int
