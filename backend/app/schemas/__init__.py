"""Schemas module initialization."""

from app.schemas.user_schema import UserCreate, UserResponse
from app.schemas.task_schema import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)
from app.schemas.category_schema import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
)

from app.schemas.chat_request import ChatRequest
from app.schemas.chat_response import ChatResponse, ToolCall

# Phase V - Advanced Features
from app.schemas.tag_schema import (
    TagCreate,
    TagUpdate,
    TagResponse,
    TagListResponse,
)
from app.schemas.search_schema import (
    SearchRequest,
    TaskSearchResponse,
)
from app.schemas.reminder_schema import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    ReminderListResponse,
    ReminderConfig,
)
from app.schemas.recurrence_schema import (
    RecurringSeriesCreate,
    RecurringSeriesUpdate,
    RecurringSeriesResponse,
    RecurringSeriesListResponse,
)

__all__ = [
    "UserCreate",
    "UserResponse",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryListResponse",
    "ChatRequest",
    "ChatResponse",
    "ToolCall",
    # Phase V - Advanced Features
    "TagCreate",
    "TagUpdate",
    "TagResponse",
    "TagListResponse",
    "SearchRequest",
    "SearchResponse",
    "TaskSearchResponse",
    "ReminderCreate",
    "ReminderUpdate",
    "ReminderResponse",
    "ReminderListResponse",
    "ReminderConfig",
    "RecurringSeriesCreate",
    "RecurringSeriesUpdate",
    "RecurringSeriesResponse",
    "RecurringSeriesListResponse",
]
