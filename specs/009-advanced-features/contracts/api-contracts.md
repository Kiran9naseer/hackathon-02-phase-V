# API Contracts: Phase V Advanced Features

**Feature**: Phase V – Advanced Task Management Features
**Branch**: `009-advanced-features`
**Date**: 2026-02-17
**Format**: OpenAPI 3.0

---

## Tags API

### Create Tag

```yaml
post:
  summary: Create a new tag
  operationId: createTag
  tags: [Tags]
  security:
    - bearerAuth: []
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/TagCreate'
  responses:
    '201':
      description: Tag created successfully
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/TagResponse'
    '400':
      description: Invalid input
    '401':
      description: Not authenticated
    '409':
      description: Tag with same name already exists
```

### List Tags

```yaml
get:
  summary: List all tags for authenticated user
  operationId: listTags
  tags: [Tags]
  security:
    - bearerAuth: []
  parameters:
    - name: limit
      in: query
      schema:
        type: integer
        default: 100
    - name: offset
      in: query
      schema:
        type: integer
        default: 0
  responses:
    '200':
      description: List of tags
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/TagListResponse'
```

### Update Tag

```yaml
put:
  summary: Update an existing tag
  operationId: updateTag
  tags: [Tags]
  security:
    - bearerAuth: []
  path:
    - tag_id
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/TagUpdate'
  responses:
    '200':
      description: Tag updated successfully
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/TagResponse'
    '404':
      description: Tag not found
```

### Delete Tag

```yaml
delete:
  summary: Delete a tag
  operationId: deleteTag
  tags: [Tags]
  security:
    - bearerAuth: []
  path:
    - tag_id
  responses:
    '204':
      description: Tag deleted successfully
    '404':
      description: Tag not found
```

---

## Task Tags API

### Add Tag to Task

```yaml
post:
  summary: Add a tag to a task
  operationId: addTagToTask
  tags: [TaskTags]
  security:
    - bearerAuth: []
  path:
    - task_id
  requestBody:
    required: true
    content:
      application/json:
        schema:
          type: object
          properties:
            tag_id:
              type: string
              format: uuid
  responses:
    '201':
      description: Tag added successfully
    '400':
      description: Tag already attached
    '404':
      description: Task or tag not found
```

### Remove Tag from Task

```yaml
delete:
  summary: Remove a tag from a task
  operationId: removeTagFromTask
  tags: [TaskTags]
  security:
    - bearerAuth: []
  path:
    - task_id
    - tag_id
  responses:
    '204':
      description: Tag removed successfully
    '404':
      description: Task-tag association not found
```

### List Task Tags

```yaml
get:
  summary: List all tags for a task
  operationId: listTaskTags
  tags: [TaskTags]
  security:
    - bearerAuth: []
  path:
    - task_id
  responses:
    '200':
      description: List of tags
      content:
        application/json:
          schema:
            type: array
            items:
              $ref: '#/components/schemas/TagResponse'
```

---

## Search API

### Search Tasks

```yaml
post:
  summary: Search tasks with full-text search and filters
  operationId: searchTasks
  tags: [Search]
  security:
    - bearerAuth: []
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/SearchRequest'
  responses:
    '200':
      description: Search results
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/TaskSearchResponse'
    '400':
      description: Invalid search query
```

---

## Recurring Tasks API

### Create Recurring Series

```yaml
post:
  summary: Create a new recurring task series
  operationId: createRecurringSeries
  tags: [RecurringTasks]
  security:
    - bearerAuth: []
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/RecurringSeriesCreate'
  responses:
    '201':
      description: Series created successfully
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/RecurringSeriesResponse'
```

### Pause Recurring Series

```yaml
post:
  summary: Pause a recurring task series
  operationId: pauseRecurringSeries
  tags: [RecurringTasks]
  security:
    - bearerAuth: []
  path:
    - series_id
  requestBody:
    content:
      application/json:
        schema:
          type: object
          properties:
            paused:
              type: boolean
              default: true
  responses:
    '200':
      description: Series paused successfully
    '404':
      description: Series not found
```

### Delete Recurring Series

```yaml
delete:
  summary: Delete a recurring task series
  operationId: deleteRecurringSeries
  tags: [RecurringTasks]
  security:
    - bearerAuth: []
  path:
    - series_id
  parameters:
    - name: delete_future_instances
      in: query
      schema:
        type: boolean
        default: true
  responses:
    '204':
      description: Series deleted successfully
    '404':
      description: Series not found
```

---

## Reminders API

### Create Reminder

```yaml
post:
  summary: Create a reminder for a task
  operationId: createReminder
  tags: [Reminders]
  security:
    - bearerAuth: []
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ReminderCreate'
  responses:
    '201':
      description: Reminder created successfully
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ReminderResponse'
    '400':
      description: Invalid reminder configuration
```

### Acknowledge Reminder

```yaml
post:
  summary: Acknowledge a received reminder
  operationId: acknowledgeReminder
  tags: [Reminders]
  security:
    - bearerAuth: []
  path:
    - reminder_id
  responses:
    '200':
      description: Reminder acknowledged
    '404':
      description: Reminder not found
```

### List Pending Reminders

```yaml
get:
  summary: List pending reminders
  operationId: listPendingReminders
  tags: [Reminders]
  security:
    - bearerAuth: []
  parameters:
    - name: limit
      in: query
      schema:
        type: integer
        default: 50
  responses:
    '200':
      description: List of pending reminders
      content:
        application/json:
          schema:
            type: array
            items:
              $ref: '#/components/schemas/ReminderResponse'
```

---

## Events API

### Subscribe to Events (SSE)

```yaml
get:
  summary: Subscribe to real-time event stream
  operationId: subscribeToEvents
  tags: [Events]
  security:
    - bearerAuth: []
  responses:
    '200':
      description: Event stream (Server-Sent Events)
      content:
        text/event-stream:
          schema:
            type: string
            example: |
              data: {"event_type": "TaskCreated", "task_id": "...", "timestamp": "..."}
              
              data: {"event_type": "TaskCompleted", "task_id": "...", "timestamp": "..."}
```

### Get Event History

```yaml
get:
  summary: Get event history for replay
  operationId: getEventHistory
  tags: [Events]
  security:
    - bearerAuth: []
  parameters:
    - name: since
      in: query
      schema:
        type: string
        format: date-time
    - name: limit
      in: query
      schema:
        type: integer
        default: 100
  responses:
    '200':
      description: Event history
      content:
        application/json:
          schema:
            type: array
            items:
              $ref: '#/components/schemas/DomainEvent'
```

---

## Schemas

### TagCreate

```yaml
TagCreate:
  type: object
  required:
    - name
  properties:
    name:
      type: string
      minLength: 1
      maxLength: 50
      example: "urgent"
    color:
      type: string
      pattern: "^#[0-9A-Fa-f]{6}$"
      default: "#8FBFB3"
      example: "#FF6B6B"
```

### TagResponse

```yaml
TagResponse:
  type: object
  properties:
    id:
      type: string
      format: uuid
    user_id:
      type: string
      format: uuid
    name:
      type: string
    color:
      type: string
    created_at:
      type: string
      format: date-time
    task_count:
      type: integer
      description: Number of tasks with this tag
```

### SearchRequest

```yaml
SearchRequest:
  type: object
  properties:
    query:
      type: string
      maxLength: 200
      example: "quarterly review"
    filters:
      type: object
      properties:
        status:
          type: array
          items:
            type: string
            enum: [pending, in_progress, completed, archived]
        priority:
          type: array
          items:
            type: string
            enum: [low, medium, high]
        tag_ids:
          type: array
          items:
            type: string
            format: uuid
        category_id:
          type: string
          format: uuid
        due_date_from:
          type: string
          format: date
        due_date_to:
          type: string
          format: date
    sort:
      type: object
      properties:
        field:
          type: string
          enum: [created_at, due_date, priority, updated_at]
        order:
          type: string
          enum: [asc, desc]
          default: desc
    pagination:
      type: object
      properties:
        limit:
          type: integer
          default: 20
          maximum: 100
        offset:
          type: integer
          default: 0
```

### RecurringSeriesCreate

```yaml
RecurringSeriesCreate:
  type: object
  required:
    - title
    - recurrence_rule
    - start_date
  properties:
    title:
      type: string
      maxLength: 255
    description:
      type: string
    priority:
      type: string
      enum: [low, medium, high]
      default: medium
    category_id:
      type: string
      format: uuid
    recurrence_rule:
      type: object
      required:
        - frequency
      properties:
        frequency:
          type: string
          enum: [daily, weekly, monthly]
        interval:
          type: integer
          minimum: 1
          maximum: 365
          default: 1
        day_of_week:
          type: integer
          minimum: 0
          maximum: 6
        day_of_month:
          type: integer
          minimum: 1
          maximum: 31
    start_date:
      type: string
      format: date
    end_date:
      type: string
      format: date
    timezone:
      type: string
      default: UTC
```

### ReminderCreate

```yaml
ReminderCreate:
  type: object
  required:
    - task_id
    - offset_minutes
  properties:
    task_id:
      type: string
      format: uuid
    offset_minutes:
      type: integer
      description: Minutes before due date (negative = before, positive = after)
      example: -1440
    reminder_type:
      type: string
      enum: [email, in_app, both]
      default: in_app
```

### DomainEvent

```yaml
DomainEvent:
  type: object
  properties:
    event_id:
      type: string
      format: uuid
    event_type:
      type: string
      enum:
        - TaskCreated
        - TaskUpdated
        - TaskCompleted
        - TaskDeleted
        - ReminderTriggered
        - ReminderAcknowledged
    timestamp:
      type: string
      format: date-time
    user_id:
      type: string
      format: uuid
    correlation_id:
      type: string
      format: uuid
    payload:
      type: object
      description: Event-specific data
```

---

## Error Responses

### Common Error Schema

```yaml
Error:
  type: object
  properties:
    detail:
      type: string
    error_code:
      type: string
      description: Machine-readable error code
    field_errors:
      type: array
      items:
        type: object
        properties:
          field:
            type: string
          message:
            type: string
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `TAG_ALREADY_EXISTS` | 409 | Tag with same name exists for user |
| `INVALID_RECURRENCE` | 400 | Recurrence rule validation failed |
| `REMINDER_LIMIT_EXCEEDED` | 400 | More than 5 reminders per task |
| `TAG_LIMIT_EXCEEDED` | 400 | More than 10 tags per task |
| `SEARCH_QUERY_TOO_LONG` | 400 | Search query exceeds 200 characters |
| `EVENT_NOT_FOUND` | 404 | Event ID not found in history |

---

## Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /api/v1/tags | 50 | per minute |
| POST /api/v1/tasks/{id}/tags | 100 | per minute |
| POST /api/v1/search | 100 | per minute |
| POST /api/v1/recurring | 20 | per minute |
| POST /api/v1/reminders | 50 | per minute |
| GET /api/v1/events/stream | 10 | concurrent connections |
