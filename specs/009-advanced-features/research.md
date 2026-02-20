# Phase 0 Research: Technical Decisions & Best Practices

**Feature**: Phase V – Advanced Task Management Features
**Branch**: `009-advanced-features`
**Date**: 2026-02-17
**Purpose**: Resolve all technical unknowns and establish best practices for implementation

---

## Research Topics

### 1. PostgreSQL Full-Text Search vs External Search Engine

**Decision**: Use PostgreSQL full-text search with tsvector/tsquery

**Rationale**:
- Existing application already uses PostgreSQL (Neon Serverless)
- No additional infrastructure complexity
- Sufficient for <100k tasks per user
- Sub-500ms performance achievable with proper indexing
- GIN indexes provide fast search performance

**Alternatives Considered**:
- **Elasticsearch**: Overkill for current scale, adds operational complexity
- **Meilisearch**: Good alternative but requires separate service
- **Algolia**: External dependency, cost concerns at scale

**Implementation**:
```sql
-- Index creation
CREATE INDEX idx_tasks_search ON tasks USING GIN (
    to_tsvector('english', title || ' ' || COALESCE(description, ''))
);

-- Search query
SELECT * FROM tasks
WHERE to_tsvector('english', title || ' ' || COALESCE(description, ''))
      @@ to_tsquery('english', :search_query);
```

---

### 2. Tag System: Many-to-Many Design Pattern

**Decision**: Junction table pattern with cascading deletes

**Rationale**:
- Standard relational pattern, well-understood
- SQLModel/SQLAlchemy handle joins automatically
- Efficient queries with proper indexes
- Easy to add metadata to tag-task relationship later

**Schema Design**:
```python
class Tag(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    name: str = Field(max_length=50, index=True)
    color: str = Field(default="#8FBFB3", max_length=7)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"
    task_id: UUID = Field(foreign_key="task.id", primary_key=True, ondelete="CASCADE")
    tag_id: UUID = Field(foreign_key="tag.id", primary_key=True, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Indexes**:
- `(task_id, tag_id)` - Unique constraint
- `(tag_id, task_id)` - Reverse lookup optimization

---

### 3. Recurring Task: RRULE vs Custom Format

**Decision**: Simplified custom recurrence format (not full iCalendar RRULE)

**Rationale**:
- Full RRULE overkill for daily/weekly/monthly only
- Easier to validate and explain to users
- Simpler UI implementation
- Can extend to RRULE later if needed

**Custom Format**:
```python
class RecurrenceRule(SQLModel):
    frequency: str  # "daily", "weekly", "monthly"
    interval: int = 1  # Every N days/weeks/months
    day_of_week: Optional[int] = None  # 0=Monday, 6=Sunday (for weekly)
    day_of_month: Optional[int] = None  # 1-31 (for monthly)
    end_date: Optional[date] = None
    timezone: str = "UTC"
```

**Next Instance Generation**:
```python
def generate_next_instance(rule: RecurrenceRule, last_date: date) -> date:
    if rule.frequency == "daily":
        return last_date + timedelta(days=rule.interval)
    elif rule.frequency == "weekly":
        # Find next occurrence of day_of_week
        ...
    elif rule.frequency == "monthly":
        # Handle month-end edge cases
        ...
```

---

### 4. Reminder Scheduling: Dapr vs Database Polling

**Decision**: Dapr reminders for production, database polling as fallback

**Rationale**:
- Dapr provides built-in retry, persistence, and scaling
- No custom cron infrastructure needed
- Decouples reminder logic from application
- Fallback to polling ensures reliability

**Dapr Reminder Configuration**:
```json
{
  "name": "task-reminder",
  "dueTime": "2026-02-18T10:00:00Z",
  "period": "PT0S",  # Fire once
  "callback": "/api/v1/reminders/trigger",
  "data": {
    "reminder_id": "uuid",
    "task_id": "uuid",
    "user_id": "uuid"
  }
}
```

**Fallback Polling** (if Dapr unavailable):
```python
# Run every 5 minutes
async def poll_due_reminders():
    now = datetime.utcnow()
    due_reminders = await db.query(TaskReminder).where(
        TaskReminder.scheduled_time <= now,
        TaskReminder.status == "pending"
    ).all()
    
    for reminder in due_reminders:
        await send_reminder_notification(reminder)
```

---

### 5. Kafka vs RabbitMQ for Event Streaming

**Decision**: Kafka for event sourcing capabilities and replay

**Rationale**:
- Event replay critical for recovery scenarios
- Better durability guarantees
- Scales to higher throughput
- Multiple consumers can process same events
- Already specified in requirements

**Topic Design**:
```
tasks.events  (partitioned by user_id)
  - TaskCreated
  - TaskUpdated
  - TaskCompleted
  - TaskDeleted
  - ReminderTriggered

notifications.events (partitioned by user_id)
  - NotificationSent
  - NotificationAcknowledged
```

**Event Schema** (using Pydantic):
```python
class TaskCreatedEvent(BaseModel):
    event_type: str = "TaskCreated"
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: UUID
    task_id: UUID
    correlation_id: Optional[UUID] = None
    payload: dict  # Full task data
```

**Producer Configuration**:
```python
from aiokafka import AIOKafkaProducer

producer = AIOKafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',  # Wait for all replicas
    retries=3,
    enable_idempotence=True  # Prevent duplicates
)
```

---

### 6. Real-Time Notifications: WebSocket vs Server-Sent Events

**Decision**: Server-Sent Events (SSE) for simplicity, WebSocket for bidirectional

**Rationale**:
- SSE sufficient for one-way server→client notifications
- Simpler implementation than WebSocket
- Automatic reconnection
- HTTP-based (no protocol upgrade issues)
- Use WebSocket only if bidirectional needed later

**SSE Implementation**:
```python
@router.get("/api/v1/notifications/stream")
async def notification_stream(user_id: UUID = Depends(get_current_user)):
    async def event_generator():
        async with EventSubscriber(user_id) as subscriber:
            async for event in subscriber.listen():
                yield f"data: {json.dumps(event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
```

**Frontend Hook**:
```typescript
function useNotificationStream() {
  useEffect(() => {
    const eventSource = new EventSource('/api/v1/notifications/stream');
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Add to notification center
    };
    return () => eventSource.close();
  }, []);
}
```

---

### 7. Database Migration Strategy

**Decision**: Alembic migrations with backward-compatible changes

**Best Practices**:
1. **Additive changes only** (no column drops in production)
2. **Default values** for new columns (prevent NULL issues)
3. **Backfill data** in separate migration step
4. **Test rollback** before deploying forward

**Migration Example**:
```python
# 001_add_tag_tables.py
def upgrade():
    op.create_table('tag',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=False, default='#8FBFB3'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tag_user_id', 'tag', ['user_id'])
    
    op.create_table('task_tags',
        sa.Column('task_id', sa.UUID(), nullable=False),
        sa.Column('tag_id', sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint('task_id', 'tag_id'),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ondelete='CASCADE')
    )

def downgrade():
    op.drop_table('task_tags')
    op.drop_table('tag')
```

---

### 8. Performance Optimization Strategies

**Search Performance**:
- GIN indexes on tsvector columns
- Limit search results (max 100 per page)
- Cache frequent searches (Redis, 5-minute TTL)
- Debounce search input (300ms delay)

**Event Throughput**:
- Batch event publishing (10 events per batch)
- Async event publishing (non-blocking)
- Partition Kafka topics by user_id
- Consumer groups for parallel processing

**Reminder Delivery**:
- Dapr handles scheduling (no app load)
- Batch notification sending (100 per batch)
- Retry with exponential backoff (1s, 5s, 30s, 5m)
- Dead letter queue for failed deliveries

**Database Query Optimization**:
```python
# Use eager loading for relationships
query = select(Task).options(
    selectinload(Task.tags),
    selectinload(Task.category)
).where(Task.user_id == user_id)

# Use composite indexes for filtering
# CREATE INDEX idx_tasks_filter ON tasks (user_id, status, priority, created_at DESC);
```

---

### 9. Security Considerations

**Tag Security**:
- Users can only access their own tags
- Tag names validated (no XSS, max 50 chars)
- Rate limit tag creation (50 tags/user)

**Search Security**:
- Sanitize search input (prevent SQL injection)
- Limit search query length (max 200 chars)
- Rate limit search requests (100/minute)

**Event Security**:
- Sign Kafka messages (HMAC)
- Encrypt sensitive payloads
- Validate event schemas
- Audit log for all events

**Reminder Security**:
- Users can only set reminders for their own tasks
- Limit reminders per task (max 5)
- Rate limit reminder creation

---

### 10. Monitoring & Observability

**Metrics to Track**:
- Search latency (p50, p95, p99)
- Event publishing latency
- Reminder delivery success rate
- Kafka consumer lag
- Dapr reminder trigger accuracy
- Database query performance

**Logging**:
```python
logger.info(f"Search executed: query={query}, results={count}, latency_ms={latency}")
logger.info(f"Event published: event_type={event_type}, event_id={event_id}")
logger.info(f"Reminder sent: reminder_id={id}, task_id={task_id}, status={status}")
```

**Alerting Thresholds**:
- Search latency > 1s (page)
- Reminder delivery failure > 5% (page)
- Kafka consumer lag > 1000 messages (alert)
- Event delivery failure > 1% (alert)

---

## Technology Summary Table

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Search | PostgreSQL tsvector | Built-in | Full-text search |
| Tags | Junction table pattern | N/A | Many-to-many relationships |
| Recurrence | Custom format | N/A | Simple recurrence rules |
| Reminders | Dapr + DB polling | 1.12+ | Scheduled notifications |
| Events | Apache Kafka | 3.6+ | Event streaming |
| Real-time | Server-Sent Events | N/A | Push notifications |
| Caching | Redis (optional) | 7.2+ | Search result caching |
| Migration | Alembic | 1.13+ | Database versioning |

---

## Next Steps

1. ✅ All technical decisions documented
2. ✅ Best practices established
3. ✅ Implementation patterns defined
4. ✅ Security considerations addressed
5. ✅ Monitoring strategy outlined

**Ready for Phase 1**: Data model design and API contracts
