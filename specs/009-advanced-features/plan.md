# Implementation Plan: Phase V – Advanced Task Management Features

**Branch**: `009-advanced-features` | **Date**: 2026-02-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-advanced-features/spec.md`

## Summary

Implement advanced task management features incrementally: task priorities (already partially implemented), tags system with many-to-many relationships, advanced search/filter/sort capabilities, recurring task automation, due date reminders with Dapr-based scheduling, and Kafka-driven event publishing for real-time notifications. All features maintain backward compatibility with existing 85% complete application.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/React (frontend)
**Primary Dependencies**: FastAPI, SQLModel, SQLAlchemy (backend); Next.js 14, React 18 (frontend); Kafka, Dapr (infrastructure)
**Storage**: Neon Serverless PostgreSQL (existing); Redis for caching (for search); Kafka for event streaming; Dapr for pub/sub
**Testing**: pytest, pytest-asyncio (backend); Jest, React Testing Library (frontend)
**Target Platform**: Web application (Docker containers on Kubernetes)
**Performance Goals**: Search <500ms p95, reminders delivered within 2 minutes, events delivered within 3 seconds
**Constraints**: Maintain backward compatibility with existing task schema; zero downtime migrations; incremental deployment
**Scale/Scope**: Support 10,000 tasks per user, 1000 concurrent users, event throughput 100 events/second

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Gate 1 - No Refactoring**: ✅ PASS
- All features are additive (new tables, new endpoints, new components)
- Existing task CRUD, auth, and category logic unchanged
- Priority field already exists in Task model (needs enum validation only)

**Gate 2 - Database Compatibility**: ⚠️ CONDITIONAL PASS
- New tables required: `tag`, `task_tags` (junction), `recurring_task_series`, `task_reminder`, `domain_event`
- Existing `task` table needs columns: `due_date` (exists), `reminder_config` (new), `recurrence_rule` (new)
- All migrations are additive with backward-compatible defaults
- Rollback scripts provided per phase

**Gate 3 - API Backward Compatibility**: ✅ PASS
- All existing endpoints unchanged
- New endpoints use versioned paths (`/api/v1/tasks/{id}/tags`, `/api/v1/search`, etc.)
- Query parameters additive (filter, sort params don't break existing clients)

**Gate 4 - Incremental Deployment**: ✅ PASS
- Each phase independently deployable
- Feature flags not required (new functionality hidden until UI wired)
- Kafka/Dapr can be deployed separately from application code

## Project Structure

### Documentation (this feature)

```text
specs/009-advanced-features/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── task.py          # ADD: priority enum validation, due_date, reminder_config, recurrence_rule
│   │   ├── tag.py           # NEW: Tag model
│   │   ├── recurring_series.py # NEW: RecurringTaskSeries model
│   │   └── task_reminder.py # NEW: TaskReminder model
│   ├── schemas/
│   │   ├── task_schema.py   # ADD: priority enums, tag schemas
│   │   ├── tag_schema.py    # NEW: Tag CRUD schemas
│   │   ├── search_schema.py # NEW: Search request/response schemas
│   │   └── reminder_schema.py # NEW: Reminder schemas
│   ├── services/
│   │   ├── task_service.py  # ADD: search, filter, sort methods
│   │   ├── tag_service.py   # NEW: Tag CRUD service
│   │   ├── reminder_service.py # NEW: Reminder scheduling service
│   │   └── recurrence_service.py # NEW: Recurrence generation service
│   ├── api/
│   │   ├── tasks.py         # ADD: /{id}/tags, /{id}/complete endpoints
│   │   ├── tags.py          # NEW: Tag CRUD endpoints
│   │   ├── search.py        # NEW: Search endpoint
│   │   └── events.py        # NEW: Event publishing endpoints
│   └── events/
│       ├── publisher.py     # NEW: Kafka event publisher
│       └── types.py         # NEW: Event type definitions
├── alembic/
│   └── versions/
│       ├── 001_add_tag_tables.py
│       ├── 002_add_reminder_tables.py
│       └── 003_add_recurrence_fields.py
└── tests/
    ├── integration/
    │   ├── test_tags.py
    │   ├── test_search.py
    │   └── test_reminders.py
    └── unit/
        ├── test_recurrence.py
        └── test_events.py

frontend/
├── app/
│   └── (protected)/
│       ├── tasks/
│       │   └── page.tsx     # MODIFY: Add priority indicators, tag UI
│       └── search/
│           └── page.tsx     # NEW: Search page
├── components/
│   └── tasks/
│       ├── TaskCard.tsx     # MODIFY: Add priority badges, tag display
│       ├── TaskFilter.tsx   # MODIFY: Add tag filter, priority filter
│       ├── PriorityBadge.tsx # NEW: Priority indicator component
│       └── TagInput.tsx     # NEW: Tag autocomplete component
└── hooks/
    └── useTasks.ts          # MODIFY: Add search, filter, sort logic

docker-compose.yml           # MODIFY: Add Kafka, Dapr services
k8s/
├── kafka-deployment.yaml    # NEW: Kafka deployment
└── dapr-deployment.yaml     # NEW: Dapr runtime
```

**Structure Decision**: Web application structure (backend + frontend) with infrastructure additions (Kafka, Dapr services). All changes are additive to existing directories.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Kafka introduction | Event-driven architecture required for real-time notifications and decoupled reminder processing | Database polling would add latency and load; websockets alone don't provide persistence |
| Dapr runtime | Provides built-in reminder scheduling with retry logic and state management | Custom cron job solution would require significant infrastructure code |
| New tables (tag, reminders, recurrence) | Core feature requirements cannot be met with existing schema | No simpler alternative - these are fundamental data requirements |

## Implementation Phases Overview

| Phase | Features | Duration | Risk | Dependencies |
|-------|----------|----------|------|--------------|
| **Phase 1** | Task Priority Enhancement | 2-3 hours | Low | None |
| **Phase 2** | Tags System | 6-8 hours | Low | Phase 1 |
| **Phase 3** | Search/Filter/Sort | 8-10 hours | Medium | Phase 1, Phase 2 |
| **Phase 4** | Recurring Tasks | 10-12 hours | Medium | Phase 1 |
| **Phase 5** | Reminders (Dapr) | 12-16 hours | High | Phase 4 |
| **Phase 6** | Event Publishing (Kafka) | 10-14 hours | High | Phase 1-5 |
| **Phase 7** | Integration & Testing | 8-10 hours | Low | Phase 1-6 |

**Total Estimated Duration**: 66-83 hours (approximately 8-10 working days)

---

## Phase 1: Task Priority Enhancement (P1)

**Goal**: Complete existing priority implementation with proper enum validation and UI indicators

**Tasks**:
- T001: Add priority enum validation to Task model
- T002: Add priority filter/sort to task list endpoint
- T003: Create PriorityBadge component
- T004: Update TaskCard with priority indicators

**Files Modified**:
- `backend/app/models/task.py` (enum validation)
- `backend/app/api/tasks.py` (filter/sort params)
- `backend/app/services/task_service.py` (query logic)
- `frontend/components/tasks/TaskCard.tsx` (UI)
- `frontend/components/tasks/PriorityBadge.tsx` (new)

**Testing**:
- Create tasks with different priorities
- Filter by priority level
- Sort by priority (high-to-low, low-to-high)
- Verify visual indicators display correctly

**Rollback**: Revert commits; no database changes required

---

## Phase 2: Tags System (P1)

**Goal**: Implement many-to-many tag system for flexible task organization

**Tasks**:
- T005: Create Tag model and task_tags junction table
- T006: Create Tag CRUD service and endpoints
- T007: Add tag assignment to task create/update
- T008: Create tag filter for task list
- T009: Build TagInput component with autocomplete
- T010: Display tags on TaskCard

**Files Modified**:
- `backend/app/models/tag.py` (new)
- `backend/app/models/task.py` (add tags relationship)
- `backend/app/schemas/tag_schema.py` (new)
- `backend/app/services/tag_service.py` (new)
- `backend/app/api/tags.py` (new)
- `backend/alembic/versions/001_add_tag_tables.py` (new)
- `frontend/components/tasks/TagInput.tsx` (new)
- `frontend/components/tasks/TaskCard.tsx` (tag display)
- `frontend/hooks/useTasks.ts` (tag filtering)

**Testing**:
- Create/delete tags
- Assign multiple tags to tasks
- Filter tasks by tag
- Verify tag autocomplete works
- Test tag deletion cascades correctly

**Rollback**: Run migration rollback `001_add_tag_tables.py`

---

## Phase 3: Search/Filter/Sort (P1)

**Goal**: Implement advanced search and multi-criteria filtering

**Tasks**:
- T011: Add full-text search endpoint
- T012: Implement search service with PostgreSQL tsvector
- T013: Add composite filter support (priority + status + tags)
- T014: Add multi-field sorting
- T015: Build SearchPage component
- T016: Enhance TaskFilter with all filter options

**Files Modified**:
- `backend/app/api/search.py` (new)
- `backend/app/services/search_service.py` (new)
- `backend/app/schemas/search_schema.py` (new)
- `backend/app/services/task_service.py` (enhance filters)
- `frontend/app/(protected)/search/page.tsx` (new)
- `frontend/components/tasks/TaskFilter.tsx` (enhance)

**Testing**:
- Search by keyword (title, description, tags)
- Apply multiple filters simultaneously
- Sort by different fields
- Verify pagination works with filters
- Test empty result handling

**Rollback**: Revert search endpoint commits; no DB changes (uses existing tables)

---

## Phase 4: Recurring Tasks (P2)

**Goal**: Automate routine task generation with recurrence rules

**Tasks**:
- T017: Create RecurringTaskSeries model
- T018: Add recurrence fields to Task model
- T019: Implement recurrence generation service
- T020: Add recurrence CRUD endpoints
- T021: Auto-generate next instance on completion
- T022: Build recurring task UI (create/edit)
- T023: Show recurrence indicator on task instances

**Files Modified**:
- `backend/app/models/recurring_series.py` (new)
- `backend/app/models/task.py` (add recurrence_rule)
- `backend/app/services/recurrence_service.py` (new)
- `backend/app/api/recurring.py` (new)
- `backend/alembic/versions/002_add_recurrence_fields.py` (new)
- `frontend/components/tasks/TaskModal.tsx` (recurrence options)
- `frontend/components/tasks/RecurrenceBadge.tsx` (new)

**Testing**:
- Create daily/weekly/monthly recurring tasks
- Complete task and verify next instance created
- Pause/resume recurrence
- Delete series vs individual instance
- Verify timezone handling

**Rollback**: Run migration rollback `002_add_recurrence_fields.py`

---

## Phase 5: Reminders with Dapr (P2)

**Goal**: Implement scheduled reminders using Dapr runtime

**Tasks**:
- T024: Deploy Dapr to Kubernetes
- T025: Create TaskReminder model
- T026: Implement reminder service with Dapr scheduling
- T027: Add reminder CRUD endpoints
- T028: Send reminder notifications
- T029: Track delivery status and retries
- T030: Build reminder configuration UI
- T031: Display overdue indicators

**Files Modified**:
- `backend/app/models/task_reminder.py` (new)
- `backend/app/services/reminder_service.py` (new)
- `backend/app/api/reminders.py` (new)
- `backend/alembic/versions/003_add_reminder_tables.py` (new)
- `k8s/dapr-deployment.yaml` (new)
- `backend/app/dapr_client.py` (new)
- `frontend/components/tasks/ReminderConfig.tsx` (new)
- `frontend/components/tasks/TaskCard.tsx` (overdue indicator)

**Testing**:
- Set reminder for future date
- Verify reminder triggers at correct time
- Test retry logic on delivery failure
- Acknowledge reminders
- Test overdue detection

**Rollback**: Run migration rollback `003_add_reminder_tables.py`; remove Dapr deployment

---

## Phase 6: Event Publishing with Kafka (P3)

**Goal**: Implement event-driven architecture for real-time notifications

**Tasks**:
- T032: Deploy Kafka to Kubernetes
- T033: Define event types (TaskCreated, TaskCompleted, etc.)
- T034: Implement Kafka publisher service
- T035: Publish events on task CRUD operations
- T036: Publish events on reminder triggers
- T037: Implement WebSocket subscriber for frontend
- T038: Build real-time notification center UI
- T039: Add event replay capability

**Files Modified**:
- `backend/app/events/publisher.py` (new)
- `backend/app/events/types.py` (new)
- `backend/app/events/consumer.py` (new)
- `k8s/kafka-deployment.yaml` (new)
- `docker-compose.yml` (add Kafka service)
- `backend/app/services/task_service.py` (add event publishing)
- `frontend/components/notifications/NotificationCenter.tsx` (new)
- `frontend/hooks/useWebSocket.ts` (new)

**Testing**:
- Create task and verify event published
- Subscribe to events via WebSocket
- Verify real-time notifications appear
- Test event replay after downtime
- Test Kafka failure fallback (local queue)

**Rollback**: Disable event publishing in config; remove Kafka deployment

---

## Phase 7: Integration & Testing (P3)

**Goal**: Comprehensive testing and integration validation

**Tasks**:
- T040: Write integration tests for all new endpoints
- T041: Write contract tests for API schemas
- T042: Write E2E tests for critical user flows
- T043: Performance testing (search, events, reminders)
- T044: Load testing (1000 concurrent users)
- T045: Documentation update (API docs, README)
- T046: Deploy to staging environment
- T047: User acceptance testing

**Files Modified**:
- `backend/tests/integration/test_tags.py` (new)
- `backend/tests/integration/test_search.py` (new)
- `backend/tests/integration/test_reminders.py` (new)
- `backend/tests/integration/test_events.py` (new)
- `backend/tests/contract/test_schemas.py` (new)
- `docs/API.md` (update)
- `README.md` (update)

**Testing**:
- Full regression test suite
- Performance benchmarks
- Load testing results
- Security scan
- Accessibility audit

**Rollback**: Full deployment rollback via Kubernetes

---

## Final Integration Validation Checklist

- [ ] All migrations run successfully on production database
- [ ] All endpoints respond with correct status codes
- [ ] Search returns results in <500ms p95
- [ ] Reminders delivered within 2 minutes (99% success rate)
- [ ] Events delivered within 3 seconds (99.5% success rate)
- [ ] Frontend displays all new features correctly
- [ ] No console errors in browser
- [ ] All tests pass (unit, integration, E2E)
- [ ] Documentation complete and accurate
- [ ] Rollback procedures tested and documented
- [ ] Monitoring dashboards configured (Kafka, Dapr, application)
- [ ] Alert rules configured for failures

---

## Summary of Deliverables

**Backend**:
- 7 new models (Tag, TaskReminder, RecurringTaskSeries, event types)
- 6 new services (TagService, SearchService, ReminderService, RecurrenceService, EventPublisher, EventConsumer)
- 6 new API endpoints (tags, search, reminders, recurring, events, WebSocket)
- 3 database migrations (tags, reminders, recurrence)
- Comprehensive test suite

**Frontend**:
- 8 new components (PriorityBadge, TagInput, RecurrenceBadge, ReminderConfig, NotificationCenter, SearchPage)
- 2 new hooks (useWebSocket, enhanced useTasks)
- Enhanced existing components (TaskCard, TaskFilter, TaskModal)

**Infrastructure**:
- Kafka deployment (Kubernetes)
- Dapr runtime (Kubernetes)
- Updated docker-compose.yml
- Monitoring and alerting configuration

**Documentation**:
- API documentation (OpenAPI)
- User guide for new features
- Deployment runbook
- Rollback procedures
