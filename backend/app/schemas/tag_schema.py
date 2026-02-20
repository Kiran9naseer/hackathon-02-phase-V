"""Tag schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
import re


class TagCreate(BaseModel):
    """Schema for creating a new tag."""
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#8FBFB3", pattern=r"^#[0-9A-Fa-f]{6}$")

    @field_validator('name')
    @classmethod
    def validate_tag_name(cls, v):
        """Validate tag name format."""
        if not re.match(r'^[\w\s-]+$', v.strip()):
            raise ValueError('Tag name can only contain letters, numbers, spaces, hyphens, and underscores')
        return v.strip()


class TagUpdate(BaseModel):
    """Schema for updating an existing tag."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")

    @field_validator('name')
    @classmethod
    def validate_tag_name(cls, v):
        """Validate tag name format."""
        if v is not None and not re.match(r'^[\w\s-]+$', v.strip()):
            raise ValueError('Tag name can only contain letters, numbers, spaces, hyphens, and underscores')
        return v.strip() if v else v


class TagResponse(BaseModel):
    """Schema for tag response."""
    id: UUID
    user_id: UUID
    name: str
    color: str
    created_at: datetime
    task_count: Optional[int] = None

    class Config:
        from_attributes = True


class TagListResponse(BaseModel):
    """Schema for paginated tag list response."""
    items: list[TagResponse]
    total: int
    limit: int
    offset: int
