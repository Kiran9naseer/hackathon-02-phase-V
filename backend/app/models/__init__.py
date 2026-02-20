"""Models module initialization."""

from sqlmodel import SQLModel

from app.models.user import User
from app.models.task import Task
from app.models.category import Category
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole

# Phase V - Advanced Features
from app.models.tag import Tag
from app.models.task_tags import TaskTag
from app.models.recurring_series import RecurringTaskSeries
from app.models.task_reminder import TaskReminder

# Export Base for use in database initialization
Base = SQLModel

__all__ = [
    "User",
    "Task",
    "Category",
    "Conversation",
    "Message",
    "MessageRole",
    # Phase V - Advanced Features
    "Tag",
    "TaskTag",
    "RecurringTaskSeries",
    "TaskReminder",
    "Base",
]
