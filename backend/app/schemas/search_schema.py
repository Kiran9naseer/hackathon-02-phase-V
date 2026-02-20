"""Search schemas for request/response validation."""

from datetime import date
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SearchFilters(BaseModel):
    """Schema for search filter criteria."""
    status: Optional[List[str]] = Field(default=None)
    priority: Optional[List[str]] = Field(default=None)
    tag_ids: Optional[List[UUID]] = Field(default=None)
    category_id: Optional[UUID] = Field(default=None)
    due_date_from: Optional[date] = Field(default=None)
    due_date_to: Optional[date] = Field(default=None)


class SearchSort(BaseModel):
    """Schema for search sorting options."""
    field: str = Field(default="created_at")
    order: str = Field(default="desc")

    @field_validator('field')
    @classmethod
    def validate_field(cls, v):
        """Validate sort field."""
        allowed_fields = ['created_at', 'updated_at', 'due_date', 'priority', 'title']
        if v not in allowed_fields:
            raise ValueError(f'Sort field must be one of: {", ".join(allowed_fields)}')
        return v

    @field_validator('order')
    @classmethod
    def validate_order(cls, v):
        """Validate sort order."""
        if v not in ['asc', 'desc']:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v


class SearchPagination(BaseModel):
    """Schema for search pagination options."""
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SearchRequest(BaseModel):
    """Schema for search request."""
    query: Optional[str] = Field(default=None, max_length=200)
    filters: Optional[SearchFilters] = Field(default=None)
    sort: Optional[SearchSort] = Field(default=None)
    pagination: Optional[SearchPagination] = Field(default=None)


class TaskSearchResult(BaseModel):
    """Schema for a single task search result."""
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    status: str
    priority: str
    category_id: Optional[UUID]
    due_date: Optional[date]
    created_at: str
    updated_at: str
    tags: Optional[list] = None
    highlight: Optional[dict] = None  # For search result highlighting


class TaskSearchResponse(BaseModel):
    """Schema for task search response."""
    items: list[TaskSearchResult]
    total: int
    limit: int
    offset: int
    query: Optional[str] = None
