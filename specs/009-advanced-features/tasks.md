# Tasks: Phase V – Advanced Task Management Features

**Input**: Design documents from `/specs/009-advanced-features/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - only include them if explicitly requested in the feature specification or if TDD approach is desired.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and preparation for feature implementation

**Note**: Existing project structure is already in place (85% complete application). These tasks verify and prepare the environment.

- [X] T001 Verify backend directory structure matches plan.md (backend/app/models/, services/, api/)
- [X] T002 Verify frontend directory structure matches plan.md (frontend/app/(protected)/, components/, hooks/)
- [X] T003 [P] Verify Kafka and Dapr dependencies added to backend/requirements.txt
- [X] T004 [P] Verify Redis dependency added for search caching

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Migrations Framework

- [X] T005 Create Alembic migration 001_add_tag_tables.py with Tag and task_tags tables
- [X] T006 Create Alembic migration 002_add_reminder_tables.py with TaskReminder table
- [X] T007 Create Alembic migration 003_add_recurrence_tables.py with RecurringTaskSeries table
- [X] T008 Create Alembic migration 004_add_task_enhancements.py adding reminder_config, recurrence_rule to tasks table
- [X] T009 Create Alembic migration 005_add_search_indexes.py with GIN indexes for full-text search

### Core Models (Shared Foundation)

- [X] T010 [P] Update backend/app/models/task.py with reminder_config, recurrence_rule JSONB fields
- [X] T011 [P] Create backend/app/models/tag.py with Tag SQLModel
- [X] T012 [P] Create backend/app/models/task_tags.py with TaskTag junction SQLModel
- [X] T013 [P] Create backend/app/models/recurring_series.py with RecurringTaskSeries SQLModel
- [X] T014 [P] Create backend/app/models/task_reminder.py with TaskReminder SQLModel

### Schema Foundation

- [X] T015 [P] Create backend/app/schemas/tag_schema.py with TagCreate, TagUpdate, TagResponse schemas
- [X] T016 [P] Create backend/app/schemas/search_schema.py with SearchRequest, TaskSearchResponse schemas
- [X] T017 [P] Create backend/app/schemas/reminder_schema.py with ReminderCreate, ReminderResponse schemas
- [X] T018 [P] Create backend/app/schemas/recurrence_schema.py with RecurringSeriesCreate, RecurringSeriesResponse schemas

### Infrastructure Setup

- [X] T019 Create k8s/kafka-deployment.yaml with Kafka broker configuration
- [X] T020 Create k8s/dapr-deployment.yaml with Dapr runtime configuration
- [X] T021 Update docker-compose.yml with Kafka and Dapr services
- [X] T022 [P] Create backend/app/dapr_client.py with Dapr reminder client initialization
- [X] T023 [P] Create backend/app/events/types.py with DomainEvent base class and event type definitions

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Priority Management (Priority: P1) 🎯 MVP

**Goal**: Complete task priority implementation with enum validation, filtering, sorting, and visual indicators

**Independent Test**: Can be fully tested by creating tasks with different priority levels, viewing them sorted by priority, and filtering tasks by priority - delivering immediate value even without other advanced features.

### Implementation for User Story 1

- [X] T024 [P] [US1] Add priority enum validation to backend/app/models/task.py TaskPriority enum
- [X] T025 [P] [US1] Update backend/app/schemas/task_schema.py with priority enum validation in TaskCreate, TaskUpdate
- [X] T026 [US1] Update backend/app/services/task_service.py list() method to support priority filter parameter
- [X] T027 [US1] Update backend/app/services/task_service.py list() method to support sort_by and sort_order parameters
- [X] T028 [US1] Update backend/app/api/tasks.py list_tasks endpoint with priority, sort_by, sort_order query parameters
- [X] T029 [P] [US1] Create frontend/components/tasks/PriorityBadge.tsx with color-coded priority display (high=red, medium=yellow, low=green)
- [X] T030 [US1] Update frontend/components/tasks/TaskCard.tsx to import and render PriorityBadge component
- [X] T031 [US1] Update frontend/hooks/useTasks.ts to support priority filter and sort functionality
- [X] T032 [US1] Add priority filter dropdown to frontend/components/tasks/TaskFilter.tsx

**Checkpoint**: User Story 1 complete - priority management working with filtering, sorting, and visual indicators

---

## Phase 4: User Story 2 - Task Tagging System (Priority: P1)

**Goal**: Implement many-to-many tag system for flexible task organization

**Independent Test**: Can be fully tested by creating tags, assigning multiple tags to tasks, and filtering tasks by tags - delivering immediate organizational value independently.

### Implementation for User Story 2

- [X] T033 [P] [US2] Create backend/app/services/tag_service.py with TagService CRUD operations (create, list, get, update, delete)
- [X] T034 [P] [US2] Create backend/app/api/tags.py with Tag CRUD endpoints (POST, GET, PUT, DELETE /api/v1/tags)
- [X] T035 [US2] Update backend/app/api/routes.py to include tags router with prefix /api/v1/tags
- [X] T036 [US2] Update backend/app/models/task.py to add tags relationship with TaskTag link_model
- [X] T037 [US2] Update backend/app/models/tag.py to add tasks relationship with TaskTag link_model
- [X] T038 [US2] Create backend/app/api/task_tags.py with endpoints for adding/removing tags from tasks (POST /tasks/{id}/tags, DELETE /tasks/{id}/tags/{tag_id})
- [X] T039 [US2] Update backend/app/services/task_service.py to support tag_ids parameter in create() and update() methods
- [X] T040 [US2] Update backend/app/services/task_service.py list() method to support tag_ids filter parameter
- [X] T041 [US2] Update backend/app/api/tasks.py list_tasks endpoint with tag_ids query parameter
- [X] T042 [P] [US2] Create frontend/components/tasks/TagInput.tsx with autocomplete for existing tags and create-new capability
- [X] T043 [US2] Update frontend/components/tasks/TaskCard.tsx to display tags as clickable labels with color coding
- [X] T044 [US2] Update frontend/components/tasks/TaskModal.tsx to include TagInput for tag assignment
- [X] T045 [US2] Add tag filter to frontend/components/tasks/TaskFilter.tsx with multi-select capability
- [X] T046 [US2] Create frontend/app/(protected)/tags/page.tsx for tag management UI

**Checkpoint**: User Story 2 complete - tagging system working with many-to-many relationships and filtering

---

## Phase 5: User Story 3 - Advanced Search and Filtering (Priority: P1)

**Goal**: Implement full-text search and multi-criteria filtering

**Independent Test**: Can be fully tested by entering search queries and applying filters, verifying that results match expected criteria - delivers value independently of other features.

### Implementation for User Story 3

- [X] T047 [P] [US3] Create backend/app/services/search_service.py with SearchService using PostgreSQL tsvector/tsquery
- [X] T048 [P] [US3] Create backend/app/api/search.py with POST /api/v1/search endpoint
- [X] T049 [US3] Update backend/app/api/routes.py to include search router with prefix /api/v1/search
- [X] T050 [US3] Update backend/app/services/task_service.py list() method to support composite filters (status + priority + category + tags)
- [X] T051 [US3] Update backend/app/services/task_service.py list() method to support multi-field sorting (created_at, due_date, priority, updated_at)
- [X] T052 [US3] Update backend/app/api/tasks.py list_tasks endpoint with combined filter support
- [X] T053 [P] [US3] Create frontend/app/(protected)/search/page.tsx with search input and filter controls
- [X] T054 [US3] Create frontend/components/search/SearchBar.tsx with debounced search input (300ms)
- [X] T055 [US3] Create frontend/components/search/SearchFilters.tsx with multi-filter UI (status, priority, tags, date range)
- [X] T056 [US3] Update frontend/components/tasks/TaskList.tsx to support search result highlighting
- [X] T057 [US3] Add search result count and pagination to frontend/components/search/SearchResults.tsx
- [X] T058 [US3] Implement empty state UI in frontend/components/search/SearchEmptyState.tsx with suggestions

**Checkpoint**: User Story 3 complete - advanced full-text search and filtering working end-to-end

**Checkpoint**: User Story 3 complete - search and filtering working with multi-criteria support

---

## Phase 6: User Story 4 - Recurring Task Automation (Priority: P2)

**Goal**: Automate routine task generation with recurrence rules

**Independent Test**: Can be fully tested by creating a recurring task, verifying that new instances are automatically generated according to the recurrence rule, and confirming that completing one instance doesn't affect future instances.

### Implementation for User Story 4

- [X] T059 [P] [US4] Create backend/app/services/recurrence_service.py with RecurrenceService for next instance calculation
- [X] T060 [P] [US4] Create backend/app/api/recurring.py with RecurringTaskSeries CRUD endpoints
- [X] T061 [US4] Update backend/app/api/routes.py to include recurring router with prefix /api/v1/recurring
- [X] T062 [US4] Implement recurrence rule validation in backend/app/schemas/recurrence_schema.py
- [X] T063 [US4] Update backend/app/api/tasks.py complete endpoint to trigger recurrence instance generation
- [X] T064 [US4] Add pause/resume endpoints to backend/app/api/recurring.py (POST /series/{id}/pause, POST /series/{id}/resume)
- [X] T065 [US4] Add delete series endpoint with delete_future_instances parameter to backend/app/api/recurring.py
- [X] T066 [P] [US4] Create frontend/components/tasks/RecurrenceConfig.tsx with frequency selector (daily/weekly/monthly) and options
- [X] T067 [US4] Update frontend/components/tasks/TaskModal.tsx to include RecurrenceConfig section
- [X] T068 [P] [US4] Create frontend/components/tasks/RecurrenceBadge.tsx with recurrence indicator icon
- [X] T069 [US4] Update frontend/components/tasks/TaskCard.tsx to display RecurrenceBadge for recurring tasks
- [X] T070 [US4] Create frontend/app/(protected)/recurring/page.tsx for recurring series management UI
- [X] T071 [US4] Add pause/resume buttons to frontend/components/recurring/RecurringSeriesCard.tsx

**Checkpoint**: User Story 4 complete - recurring task automation working with instance generation

---

## Phase 7: User Story 5 - Due Date Reminders (Priority: P2)

**Goal**: Implement scheduled reminders using Dapr runtime

**Independent Test**: Can be fully tested by setting a task with a due date and reminder, verifying that the reminder is triggered at the configured time, and confirming the user receives the notification.

### Implementation for User Story 5

- [X] T072 [P] [US5] Create backend/app/services/reminder_service.py with ReminderService using Dapr scheduling
- [X] T073 [P] [US5] Create backend/app/api/reminders.py with Reminder CRUD endpoints
- [X] T074 [US5] Update backend/app/api/routes.py to include reminders router with prefix /api/v1/reminders
- [X] T075 [US5] Implement reminder delivery logic in backend/app/services/reminder_service.py with retry and exponential backoff
- [X] T076 [US5] Add reminder acknowledgment endpoint to backend/app/api/reminders.py (POST /reminders/{id}/acknowledge)
- [X] T077 [US5] Implement database polling fallback in backend/app/services/reminder_service.py for Dapr unavailability
- [X] T078 [US5] Add overdue detection cron job in backend/app/services/reminder_service.py (runs every 5 minutes)
- [X] T079 [US5] Update backend/app/models/task.py to add reminders relationship
- [X] T080 [P] [US5] Create frontend/components/tasks/ReminderConfig.tsx with timing selector (1 hour, 1 day, 1 week before)
- [X] T081 [US5] Update frontend/components/forms/TaskForm.tsx to include ReminderConfig section
- [X] T082 [US5] Update frontend/components/tasks/TaskCard.tsx to display overdue indicator (red border) for overdue tasks
- [X] T083 [US5] Create frontend/app/(protected)/reminders/page.tsx for pending reminders list UI
- [X] T084 [US5] Create frontend/components/reminders/ReminderList.tsx with acknowledge action
- [X] T085 [US5] Add in-app notification toast when reminder received in frontend/components/notifications/ReminderToast.tsx

**Checkpoint**: User Story 5 complete - reminders working with Dapr scheduling and delivery tracking

---

## Phase 8: User Story 6 - Real-Time Event Notifications (Priority: P3)

**Goal**: Implement event-driven architecture for real-time notifications

**Independent Test**: Can be fully tested by creating/updating a task in one session and verifying that notifications appear in real-time in other active sessions.

### Implementation for User Story 6

- [X] T086 [P] [US6] Create backend/app/events/publisher.py with KafkaEventPublisher using aiokafka
- [X] T087 [P] [US6] Create backend/app/events/consumer.py with KafkaEventConsumer for WebSocket broadcasting
- [X] T088 [US6] Update backend/app/services/task_service.py to publish TaskCreated event on create()
- [X] T089 [US6] Update backend/app/services/task_service.py to publish TaskUpdated event on update()
- [X] T090 [US6] Update backend/app/services/task_service.py to publish TaskCompleted event on complete()
- [X] T091 [US6] Update backend/app/services/task_service.py to publish TaskDeleted event on delete()
- [X] T092 [US6] Update backend/app/services/reminder_service.py to publish ReminderTriggered event on delivery
- [X] T093 [P] [US6] Create backend/app/api/events.py with SSE endpoint GET /api/v1/events/stream
- [X] T094 [US6] Update backend/app/api/routes.py to include events router with prefix /api/v1/events
- [X] T095 [US6] Add event history endpoint to backend/app/api/events.py (GET /api/v1/events/history with since, limit params)
- [X] T096 [P] [US6] Create frontend/hooks/useWebSocket.ts with WebSocket connection management and reconnection logic
- [X] T097 [US6] Create frontend/components/notifications/NotificationCenter.tsx with real-time notification display
- [X] T098 [US6] Update frontend/app/(protected)/layout.tsx to include NotificationCenter in global layout
- [X] T099 [US6] Add event replay capability to frontend/hooks/useWebSocket.ts for missed events on reconnect
- [X] T100 [US6] Implement Kafka failure fallback (local queue) in backend/app/events/publisher.py

**Checkpoint**: User Story 6 complete - real-time event notifications working with Kafka streaming

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

### Documentation & Testing

- [X] T101 [P] Update backend/README.md with new features overview and API documentation links
- [X] T102 [P] Update frontend/README.md with new components documentation
- [X] T103 Create integration tests backend/tests/integration/test_tags.py for tag CRUD and filtering
- [X] T104 Create integration tests backend/tests/integration/test_search.py for search endpoint
- [X] T105 Create integration tests backend/tests/integration/test_reminders.py for reminder delivery
- [X] T106 Create integration tests backend/tests/integration/test_events.py for event publishing
- [X] T107 Create unit tests backend/tests/unit/test_recurrence.py for recurrence calculation
- [X] T108 [P] Run full test suite and fix any failures

### Performance & Validation

- [ ] T109 [P] Run search performance test (verify p95 < 500ms)
- [ ] T110 [P] Run reminder delivery test (verify 99% success rate within 2 minutes)
- [ ] T111 [P] Run event delivery test (verify 99.5% success rate within 3 seconds)
- [ ] T112 [P] Run load test with 1000 concurrent users
- [ ] T113 [P] Verify all migrations run successfully on staging database
- [ ] T114 [P] Verify rollback procedures work for each migration

### Deployment & Monitoring

- [ ] T115 [P] Deploy to staging environment
- [ ] T116 [P] Configure monitoring dashboards (Kafka lag, Dapr reminders, search latency)
- [ ] T117 [P] Configure alert rules for failures (reminder delivery <95%, event delivery <99%)
- [ ] T118 [P] Run user acceptance testing on staging
- [ ] T119 [P] Deploy to production
- [ ] T120 [P] Monitor production metrics for 1 week

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed) or sequentially in priority order
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

| User Story | Priority | Dependencies | Can Run Parallel With |
|------------|----------|--------------|----------------------|
| **US1**: Priority Management | P1 | Foundational (Phase 2) | US2, US3, US4, US5, US6 |
| **US2**: Tagging System | P1 | Foundational + US1 (Task model) | US3, US4, US5, US6 |
| **US3**: Search/Filter | P1 | Foundational + US1, US2 | US4, US5, US6 |
| **US4**: Recurring Tasks | P2 | Foundational + US1 | US5, US6 |
| **US5**: Reminders | P2 | Foundational + US4 (due date) | US6 |
| **US6**: Event Notifications | P3 | Foundational + US1-5 (events) | None (last to complete) |

### Within Each User Story

- Models (marked [P]) can run in parallel
- Services depend on models
- Endpoints depend on services
- UI components depend on backend endpoints
- Integration tasks depend on core implementation

### Parallel Opportunities

**After Foundational Phase Completes**:
```bash
# All P1 user stories can start in parallel:
Developer A: Phase 3 - User Story 1 (Priority Management)
Developer B: Phase 4 - User Story 2 (Tagging System)
Developer C: Phase 5 - User Story 3 (Search/Filter)

# After US1-3 complete:
Developer A: Phase 6 - User Story 4 (Recurring Tasks)
Developer B: Phase 7 - User Story 5 (Reminders)

# After US4-5 complete:
Developer A: Phase 8 - User Story 6 (Event Notifications)
```

**Within User Story 1 (Priority Management)**:
```bash
# Models can run in parallel:
Task: "Add priority enum validation to task.py"
Task: "Update task_schema.py with priority enum validation"

# Services can run in parallel:
Task: "Update task_service.py list() for priority filter"
Task: "Update task_service.py list() for sort parameters"
```

**Within User Story 2 (Tagging System)**:
```bash
# Models can run in parallel:
Task: "Create tag_service.py"
Task: "Create tags.py API endpoints"

# UI components can run in parallel:
Task: "Create TagInput.tsx"
Task: "Update TaskCard.tsx for tag display"
Task: "Update TaskFilter.tsx for tag filter"
```

---

## Parallel Execution Examples

### Parallel for User Story 1 (Phase 3)
```bash
Task: "Add priority enum validation to task.py"
Task: "Update task_schema.py with priority enum validation"
Task: "Create PriorityBadge.tsx component"
```

### Parallel for User Story 2 (Phase 4)
```bash
Task: "Create tag_service.py"
Task: "Create tags.py API endpoints"
Task: "Create TagInput.tsx"
Task: "Update TaskCard.tsx for tag display"
```

### Parallel for User Story 3 (Phase 5)
```bash
Task: "Create search_service.py"
Task: "Create search.py API endpoint"
Task: "Create SearchBar.tsx"
Task: "Create SearchFilters.tsx"
```

### Parallel for User Story 4 (Phase 6)
```bash
Task: "Create recurrence_service.py"
Task: "Create recurring.py API endpoints"
Task: "Create RecurrenceConfig.tsx"
Task: "Create RecurrenceBadge.tsx"
```

### Parallel for User Story 5 (Phase 7)
```bash
Task: "Create reminder_service.py"
Task: "Create reminders.py API endpoints"
Task: "Create ReminderConfig.tsx"
Task: "Create ReminderToast.tsx"
```

### Parallel for User Story 6 (Phase 8)
```bash
Task: "Create publisher.py"
Task: "Create consumer.py"
Task: "Create events.py SSE endpoint"
Task: "Create useWebSocket.ts hook"
Task: "Create NotificationCenter.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Priority Management)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Create tasks with different priorities
   - Filter by priority
   - Sort by priority
   - Verify visual indicators
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Add User Story 6 → Test independently → Deploy/Demo
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Priority)
   - Developer B: User Story 2 (Tags)
   - Developer C: User Story 3 (Search)
3. After US1-3 complete:
   - Developer A: User Story 4 (Recurring)
   - Developer B: User Story 5 (Reminders)
4. After US4-5 complete:
   - All developers: User Story 6 (Events) + Phase 9 (Polish)

---

## Task Summary

| Category | Count |
|----------|-------|
| Setup (Phase 1) | 4 tasks |
| Foundational (Phase 2) | 19 tasks |
| User Story 1 - Priority (Phase 3) | 9 tasks |
| User Story 2 - Tags (Phase 4) | 14 tasks |
| User Story 3 - Search (Phase 5) | 12 tasks |
| User Story 4 - Recurring (Phase 6) | 13 tasks |
| User Story 5 - Reminders (Phase 7) | 14 tasks |
| User Story 6 - Events (Phase 8) | 15 tasks |
| Polish (Phase 9) | 20 tasks |
| **Total** | **120 tasks** |

### Task Count per User Story

| User Story | Priority | Task Count | Dependencies | Independent Test |
|------------|----------|------------|--------------|------------------|
| US1: Priority Management | P1 | 9 | Foundational | ✅ Create/filter/sort by priority |
| US2: Tagging System | P1 | 14 | Foundational + US1 | ✅ Create tags, assign to tasks, filter |
| US3: Search/Filter | P1 | 12 | Foundational + US1, US2 | ✅ Search with multi-filters |
| US4: Recurring Tasks | P2 | 13 | Foundational + US1 | ✅ Create series, auto-generate instances |
| US5: Reminders | P2 | 14 | Foundational + US4 | ✅ Set reminder, receive notification |
| US6: Event Notifications | P3 | 15 | Foundational + US1-5 | ✅ Real-time notifications via SSE |

### Suggested MVP Scope

**MVP = Phase 1 + Phase 2 + Phase 3 (User Story 1 - Priority Management)**

This delivers:
- Task priority levels (Low, Medium, High)
- Priority filtering and sorting
- Visual priority indicators
- Fully functional and independently testable

After MVP validated, proceed with:
- Phase 4 (Tags) - enhances organization
- Phase 5 (Search) - power user feature
- Phase 6 (Recurring) - automation
- Phase 7 (Reminders) - proactive notifications
- Phase 8 (Events) - real-time updates
- Phase 9 (Polish) - production readiness

---

## Notes

- **[P] tasks** = different files, no dependencies within phase
- **[Story] label** maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- **Tests are OPTIONAL** - only include if TDD approach requested
