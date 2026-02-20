"""Schemas for recurring task series."""

from datetime import date, datetime
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class RecurringSeriesBase(BaseModel):
    """Base schema for recurring series."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: str = "medium"
    category_id: Optional[UUID] = None
    frequency: str = "daily"
    interval: int = 1
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    timezone: str = "UTC"

class RecurringSeriesCreate(RecurringSeriesBase):
    """Schema for creating a series."""
    pass

class RecurringSeriesUpdate(BaseModel):
    """Schema for updating a series."""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category_id: Optional[UUID] = None
    frequency: Optional[str] = None
    interval: Optional[int] = None
    end_date: Optional[date] = None
    paused: Optional[bool] = None

class RecurringSeriesResponse(RecurringSeriesBase):
    """Response schema for a series."""
    id: UUID
    user_id: UUID
    paused: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
