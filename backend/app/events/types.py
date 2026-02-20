"""Domain event type definitions for event-driven architecture.

This module defines all event types published by the application
for task management, reminders, and notifications.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Enumeration of all event types."""
    
    # Task Events
    TASK_CREATED = "TaskCreated"
    TASK_UPDATED = "TaskUpdated"
    TASK_COMPLETED = "TaskCompleted"
    TASK_DELETED = "TaskDeleted"
    
    # Reminder Events
    REMINDER_TRIGGERED = "ReminderTriggered"
    REMINDER_ACKNOWLEDGED = "ReminderAcknowledged"
    REMINDER_FAILED = "ReminderFailed"
    
    # Recurrence Events
    RECURRENCE_INSTANCE_GENERATED = "RecurrenceInstanceGenerated"
    RECURRENCE_PAUSED = "RecurrencePaused"
    RECURRENCE_RESUMED = "RecurrenceResumed"
    
    # Tag Events
    TAG_CREATED = "TagCreated"
    TAG_UPDATED = "TagUpdated"
    TAG_DELETED = "TagDeleted"


class DomainEvent(BaseModel):
    """Base class for all domain events.
    
    Attributes:
        event_id: Unique event identifier
        event_type: Type of event
        timestamp: When the event occurred
        user_id: User who triggered the event
        correlation_id: ID for tracing related events
        payload: Event-specific data
    """
    
    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: UUID
    correlation_id: Optional[UUID] = Field(default=None)
    payload: dict = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


# ==================== Task Events ====================

class TaskCreatedEvent(DomainEvent):
    """Event published when a task is created."""
    event_type: EventType = EventType.TASK_CREATED
    payload: dict = Field(..., description="Task data including id, title, status, priority")


class TaskUpdatedEvent(DomainEvent):
    """Event published when a task is updated."""
    event_type: EventType = EventType.TASK_UPDATED
    payload: dict = Field(..., description="Task data including id and updated fields")


class TaskCompletedEvent(DomainEvent):
    """Event published when a task is completed."""
    event_type: EventType = EventType.TASK_COMPLETED
    payload: dict = Field(..., description="Task data including id, completed_at timestamp")


class TaskDeletedEvent(DomainEvent):
    """Event published when a task is deleted."""
    event_type: EventType = EventType.TASK_DELETED
    payload: dict = Field(..., description="Task id and deletion metadata")


# ==================== Reminder Events ====================

class ReminderTriggeredEvent(DomainEvent):
    """Event published when a reminder is triggered."""
    event_type: EventType = EventType.REMINDER_TRIGGERED
    payload: dict = Field(..., description="Reminder data including id, task_id, scheduled_time")


class ReminderAcknowledgedEvent(DomainEvent):
    """Event published when a reminder is acknowledged."""
    event_type: EventType = EventType.REMINDER_ACKNOWLEDGED
    payload: dict = Field(..., description="Reminder id and acknowledgment timestamp")


class ReminderFailedEvent(DomainEvent):
    """Event published when reminder delivery fails."""
    event_type: EventType = EventType.REMINDER_FAILED
    payload: dict = Field(..., description="Reminder id, error message, retry count")


# ==================== Recurrence Events ====================

class RecurrenceInstanceGeneratedEvent(DomainEvent):
    """Event published when a recurring task instance is generated."""
    event_type: EventType = EventType.RECURRENCE_INSTANCE_GENERATED
    payload: dict = Field(..., description="Series id, new instance id, scheduled date")


class RecurrencePausedEvent(DomainEvent):
    """Event published when a recurring series is paused."""
    event_type: EventType = EventType.RECURRENCE_PAUSED
    payload: dict = Field(..., description="Series id and pause timestamp")


class RecurrenceResumedEvent(DomainEvent):
    """Event published when a recurring series is resumed."""
    event_type: EventType = EventType.RECURRENCE_RESUMED
    payload: dict = Field(..., description="Series id and resume timestamp")


# ==================== Tag Events ====================

class TagCreatedEvent(DomainEvent):
    """Event published when a tag is created."""
    event_type: EventType = EventType.TAG_CREATED
    payload: dict = Field(..., description="Tag data including id, name, color")


class TagUpdatedEvent(DomainEvent):
    """Event published when a tag is updated."""
    event_type: EventType = EventType.TAG_UPDATED
    payload: dict = Field(..., description="Tag data including id and updated fields")


class TagDeletedEvent(DomainEvent):
    """Event published when a tag is deleted."""
    event_type: EventType = EventType.TAG_DELETED
    payload: dict = Field(..., description="Tag id and deletion metadata")


# ==================== Event Factory ====================

def create_event(
    event_type: EventType,
    user_id: UUID,
    payload: dict,
    correlation_id: Optional[UUID] = None
) -> DomainEvent:
    """Factory function to create the appropriate event type.
    
    Args:
        event_type: Type of event to create
        user_id: User who triggered the event
        payload: Event-specific data
        correlation_id: Optional correlation ID for tracing
        
    Returns:
        DomainEvent instance of the appropriate type
        
    Raises:
        ValueError: If event_type is not recognized
    """
    event_classes = {
        EventType.TASK_CREATED: TaskCreatedEvent,
        EventType.TASK_UPDATED: TaskUpdatedEvent,
        EventType.TASK_COMPLETED: TaskCompletedEvent,
        EventType.TASK_DELETED: TaskDeletedEvent,
        EventType.REMINDER_TRIGGERED: ReminderTriggeredEvent,
        EventType.REMINDER_ACKNOWLEDGED: ReminderAcknowledgedEvent,
        EventType.REMINDER_FAILED: ReminderFailedEvent,
        EventType.RECURRENCE_INSTANCE_GENERATED: RecurrenceInstanceGeneratedEvent,
        EventType.RECURRENCE_PAUSED: RecurrencePausedEvent,
        EventType.RECURRENCE_RESUMED: RecurrenceResumedEvent,
        EventType.TAG_CREATED: TagCreatedEvent,
        EventType.TAG_UPDATED: TagUpdatedEvent,
        EventType.TAG_DELETED: TagDeletedEvent,
    }
    
    event_class = event_classes.get(event_type)
    if not event_class:
        raise ValueError(f"Unknown event type: {event_type}")
    
    return event_class(
        user_id=user_id,
        payload=payload,
        correlation_id=correlation_id
    )
