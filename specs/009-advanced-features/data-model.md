# Data Model Design: Phase V Advanced Features

**Feature**: Phase V – Advanced Task Management Features
**Branch**: `009-advanced-features`
**Date**: 2026-02-17
**Source**: spec.md, research.md

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                           users                                  │
├─────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                   │
│ email: VARCHAR (UNIQUE)                                         │
│ hashed_password: VARCHAR                                        │
│ created_at: TIMESTAMP                                           │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ 1:N
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                           tasks                                  │
├─────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                   │
│ user_id: UUID (FK → users.id)                                   │
│ category_id: UUID (FK → categories.id, NULLABLE)                │
│ title: VARCHAR (NOT NULL)                                       │
│ description: TEXT                                               │
│ status: ENUM (pending/in_progress/completed/archived)           │
│ priority: ENUM (low/medium/high)                                │
│ due_date: DATE (NULLABLE)                                       │
│ reminder_config: JSONB (NULLABLE)                               │
│ recurrence_rule: JSONB (NULLABLE)                               │
│ recurrence_series_id: UUID (FK → recurring_task_series.id)      │
│ completed_at: TIMESTAMP (NULLABLE)                              │
│ created_at: TIMESTAMP                                           │
│ updated_at: TIMESTAMP                                           │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ N:M
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                         task_tags                                │
├─────────────────────────────────────────────────────────────────┤
│ task_id: UUID (FK → tasks.id, PK)                               │
│ tag_id: UUID (FK → tags.id, PK)                                 │
│ created_at: TIMESTAMP                                           │
└─────────────────────────────────────────────────────────────────┘
                                  ▲ N:M
                                  │
┌─────────────────────────────────┴───────────────────────────────┐
│                           tags                                   │
├─────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                   │
│ user_id: UUID (FK → users.id)                                   │
│ name: VARCHAR (NOT NULL)                                        │
│ color: VARCHAR (default: #8FBFB3)                               │
│ created_at: TIMESTAMP                                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    recurring_task_series                         │
├─────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                   │
│ user_id: UUID (FK → users.id)                                   │
│ title: VARCHAR (NOT NULL)                                       │
│ description: TEXT                                               │
│ priority: ENUM (low/medium/high)                                │
│ category_id: UUID (FK → categories.id, NULLABLE)                │
│ recurrence_rule: JSONB (NOT NULL)                               │
│ start_date: DATE (NOT NULL)                                     │
│ end_date: DATE (NULLABLE)                                       │
│ timezone: VARCHAR (default: UTC)                                │
│ paused: BOOLEAN (default: false)                                │
│ created_at: TIMESTAMP                                           │
│ updated_at: TIMESTAMP                                           │
└─────────────────────────────────────────────────────────────────┘
                                  │ 1:N
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      task_reminders                              │
├─────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                   │
│ user_id: UUID (FK → users.id)                                   │
│ task_id: UUID (FK → tasks.id)                                   │
│ scheduled_time: TIMESTAMP (NOT NULL)                            │
│ reminder_type: ENUM (email/in_app/both)                         │
│ offset_minutes: INTEGER (NOT NULL)                              │
│ status: ENUM (pending/sent/acknowledged/failed)                 │
│ delivered_at: TIMESTAMP (NULLABLE)                              │
│ acknowledged_at: TIMESTAMP (NULLABLE)                           │
│ error_message: TEXT (NULLABLE)                                  │
│ retry_count: INTEGER (default: 0)                               │
│ created_at: TIMESTAMP                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## SQLModel Definitions

### Tag Model

```python
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User


class Tag(SQLModel, table=True):
    """Tag model for flexible task organization.
    
    Attributes:
        id: Unique tag identifier (UUID).
        user_id: Owning user's UUID (foreign key).
        name: Tag name (required, max 50 chars).
        color: Display color (hex format, default #8FBFB3).
        created_at: Timestamp when tag was created.
    """
    __tablename__ = "tag"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    name: str = Field(max_length=50, index=True)
    color: str = Field(default="#8FBFB3", max_length=7)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), default=datetime.utcnow),
    )
    
    # Relationships
    user: "User" = Relationship(back_populates="tags")
    tasks: list["Task"] = Relationship(back_populates="tags", link_model="TaskTag")
    
    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name})>"
```

### Task-Tag Junction Model

```python
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
```

### Recurring Task Series Model

```python
from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Date, Boolean
from sqlmodel import Field, Relationship, SQLModel


class RecurrenceFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class RecurrenceRule(SQLModel):
    """Recurrence rule definition (embedded in RecurringTaskSeries).
    
    Attributes:
        frequency: How often task recurs (daily/weekly/monthly).
        interval: Every N days/weeks/months (default: 1).
        day_of_week: Day of week for weekly recurrence (0-6, optional).
        day_of_month: Day of month for monthly recurrence (1-31, optional).
    """
    frequency: RecurrenceFrequency
    interval: int = 1
    day_of_week: Optional[int] = None  # 0=Monday, 6=Sunday
    day_of_month: Optional[int] = None  # 1-31


class RecurringTaskSeries(SQLModel, table=True):
    """Recurring task series template.
    
    Attributes:
        id: Unique series identifier (UUID).
        user_id: Owning user's UUID (foreign key).
        title: Task title template (required).
        description: Task description template (optional).
        priority: Task priority (low/medium/high).
        category_id: Optional category UUID.
        recurrence_rule: JSONB-encoded recurrence rule.
        start_date: When recurrence starts (required).
        end_date: When recurrence ends (optional, None = indefinite).
        timezone: User's timezone for date calculations.
        paused: Whether recurrence is paused.
    """
    __tablename__ = "recurring_task_series"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = None
    priority: str = Field(default="medium", max_length=10)
    category_id: Optional[UUID] = Field(foreign_key="category.id", index=True)
    recurrence_rule: dict = Field(sa_column=Column(JSONB))
    start_date: date = Field(sa_column=Column(Date))
    end_date: Optional[date] = Field(default=None, sa_column=Column(Date))
    timezone: str = Field(default="UTC", max_length=50)
    paused: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: "User" = Relationship(back_populates="recurring_series")
    category: Optional["Category"] = Relationship(back_populates="recurring_series")
    
    def get_next_instance_date(self, after_date: date) -> date:
        """Calculate next instance date after given date."""
        # Implementation in service layer
        pass
```

### Task Reminder Model

```python
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Integer, Text, Enum as SQLEnum
from sqlmodel import Field, Relationship, SQLModel


class ReminderStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"


class ReminderType(str, Enum):
    EMAIL = "email"
    IN_APP = "in_app"
    BOTH = "both"


class TaskReminder(SQLModel, table=True):
    """Task reminder with scheduling and delivery tracking.
    
    Attributes:
        id: Unique reminder identifier (UUID).
        user_id: Owning user's UUID (foreign key).
        task_id: Associated task UUID (foreign key).
        scheduled_time: When reminder should trigger.
        reminder_type: Delivery method (email/in_app/both).
        offset_minutes: Minutes before due date (negative = after).
        status: Current delivery status.
        delivered_at: When reminder was sent.
        acknowledged_at: When user acknowledged reminder.
        error_message: Error details if delivery failed.
        retry_count: Number of delivery attempts.
    """
    __tablename__ = "task_reminder"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    task_id: UUID = Field(foreign_key="task.id", index=True)
    scheduled_time: datetime = Field()
    reminder_type: ReminderType = Field(default=ReminderType.IN_APP)
    offset_minutes: int = Field(default=-1440)  # Default: 1 day before
    status: ReminderStatus = Field(default=ReminderStatus.PENDING)
    delivered_at: Optional[datetime] = Field(default=None)
    acknowledged_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    retry_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: "User" = Relationship(back_populates="reminders")
    task: "Task" = Relationship(back_populates="reminders")
    
    def __repr__(self) -> str:
        return f"<TaskReminder(id={self.id}, task_id={self.task_id}, status={self.status})>"
```

### Updated Task Model

```python
# Additions to existing Task model
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import Column, DateTime, Date, JSON as SQLJSON
from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from app.models.tag import Tag
    from app.models.task_reminder import TaskReminder
    from app.models.recurring_series import RecurringTaskSeries


class Task(SQLModel, table=True):
    # ... existing fields ...
    
    # NEW: Reminder configuration (JSONB)
    reminder_config: Optional[dict] = Field(
        default=None,
        sa_column=Column("reminder_config", SQLJSON),
        description="Reminder settings: {offsets: [-1440, -60], type: 'in_app'}"
    )
    
    # NEW: Recurrence rule (JSONB)
    recurrence_rule: Optional[dict] = Field(
        default=None,
        sa_column=Column("recurrence_rule", SQLJSON),
        description="Recurrence rule for standalone recurring tasks"
    )
    
    # NEW: Recurrence series reference
    recurrence_series_id: Optional[UUID] = Field(
        default=None,
        foreign_key="recurring_task_series.id",
        index=True,
        description="Parent series ID if this is a generated instance"
    )
    
    # NEW: Many-to-many tags relationship
    tags: List["Tag"] = Relationship(
        back_populates="tasks",
        link_model="TaskTag"
    )
    
    # NEW: Reminders relationship
    reminders: List["TaskReminder"] = Relationship(
        back_populates="task"
    )
```

---

## Validation Rules

### Tag Validation

```python
from pydantic import field_validator, Field

class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#8FBFB3", pattern="^#[0-9A-Fa-f]{6}$")
    
    @field_validator('name')
    @classmethod
    def validate_tag_name(cls, v):
        # No special characters except hyphens and underscores
        if not re.match(r'^[\w\s-]+$', v):
            raise ValueError('Tag name can only contain letters, numbers, spaces, hyphens, and underscores')
        return v.strip()
```

### Recurrence Rule Validation

```python
class RecurrenceRuleCreate(BaseModel):
    frequency: RecurrenceFrequency
    interval: int = Field(default=1, ge=1, le=365)
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    end_date: Optional[date] = None
    
    @model_validator(mode='after')
    def validate_recurrence_rule(self):
        if self.frequency == RecurrenceFrequency.WEEKLY and self.day_of_week is None:
            raise ValueError('day_of_week required for weekly recurrence')
        if self.frequency == RecurrenceFrequency.MONTHLY and self.day_of_month is None:
            raise ValueError('day_of_month required for monthly recurrence')
        if self.end_date and self.end_date < self.start_date:
            raise ValueError('end_date must be after start_date')
        return self
```

### Reminder Validation

```python
class ReminderConfig(BaseModel):
    offsets: List[int] = Field(default=[-1440])  # Minutes before due date
    reminder_type: ReminderType = Field(default=ReminderType.IN_APP)
    
    @field_validator('offsets')
    @classmethod
    def validate_offsets(cls, v):
        if not v:
            raise ValueError('At least one reminder offset required')
        if len(v) > 5:
            raise ValueError('Maximum 5 reminders per task')
        return v
```

---

## State Transitions

### Task Reminder Status Flow

```
PENDING
  ├─→ SENT (on successful delivery)
  │    └─→ ACKNOWLEDGED (when user clicks)
  ├─→ FAILED (on delivery error)
  │    └─→ PENDING (after retry delay)
  └─→ FAILED (after max retries)
```

### Recurring Task Series Flow

```
ACTIVE
  ├─→ PAUSED (when user pauses)
  │    └─→ ACTIVE (when user resumes)
  └─→ COMPLETED (when end_date reached)
```

---

## Index Strategy

```sql
-- Tags
CREATE INDEX idx_tag_user_id ON tag(user_id);
CREATE INDEX idx_tag_name ON tag(name);

-- Task-Tag junction
CREATE UNIQUE INDEX idx_task_tags_unique ON task_tags(task_id, tag_id);
CREATE INDEX idx_task_tags_tag_id ON task_tags(tag_id, task_id);

-- Recurring series
CREATE INDEX idx_recurring_series_user_id ON recurring_task_series(user_id);
CREATE INDEX idx_recurring_series_start_date ON recurring_task_series(start_date);

-- Reminders
CREATE INDEX idx_reminder_scheduled_time ON task_reminder(scheduled_time);
CREATE INDEX idx_reminder_status ON task_reminder(status);
CREATE INDEX idx_reminder_user_status ON task_reminder(user_id, status);

-- Tasks (enhanced)
CREATE INDEX idx_tasks_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_due_date ON tasks(user_id, due_date);
CREATE INDEX idx_tasks_search ON tasks USING GIN (
    to_tsvector('english', title || ' ' || COALESCE(description, ''))
);
```

---

## Migration Order

1. **001_add_tag_tables.py**: Tag + task_tags tables
2. **002_add_reminder_tables.py**: TaskReminder table
3. **003_add_recurrence_tables.py**: RecurringTaskSeries table
4. **004_add_task_enhancements.py**: Add reminder_config, recurrence_rule to tasks
5. **005_add_search_indexes.py**: GIN indexes for full-text search

---

## Database Compatibility

- All migrations are additive (no drops)
- Default values provided for new columns
- Backward compatible with existing task queries
- Rollback scripts provided for each migration
