# Quickstart: Phase V Advanced Features

**Feature**: Phase V – Advanced Task Management Features
**Branch**: `009-advanced-features`
**Date**: 2026-02-17

---

## Overview

This quickstart guide provides step-by-step instructions for implementing Phase V advanced features in the correct order. Follow these steps sequentially to ensure safe, incremental deployment.

---

## Prerequisites

- [ ] Backend and frontend development environments set up
- [ ] Database access (Neon Serverless PostgreSQL)
- [ ] Docker Desktop installed and running
- [ ] Kubernetes cluster accessible (for Kafka/Dapr deployment)
- [ ] Git branch `009-advanced-features` checked out

---

## Phase 1: Task Priority Enhancement (2-3 hours)

### Step 1.1: Update Task Model Enum Validation

**File**: `backend/app/models/task.py`

Add enum validation for priority field:

```python
# Ensure TaskPriority enum is used for validation
priority: str = Field(
    default=TaskPriority.MEDIUM.value,
    max_length=10,
    schema_extra={"enum": [p.value for p in TaskPriority]}
)
```

**Test**: 
```bash
cd backend
pytest tests/unit/test_models.py -v
```

---

### Step 1.2: Add Priority Filter/Sort to API

**File**: `backend/app/api/tasks.py`

Add query parameters:

```python
@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,  # NEW
    sort_by: str = "created_at",     # NEW
    sort_order: str = "desc",        # NEW
    # ... existing params
):
```

**File**: `backend/app/services/task_service.py`

Update list method to handle priority filter and sorting.

**Test**:
```bash
# Test priority filtering
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/tasks?priority=high"

# Test sorting
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/tasks?sort_by=priority&sort_order=asc"
```

---

### Step 1.3: Create PriorityBadge Component

**File**: `frontend/components/tasks/PriorityBadge.tsx` (new)

```typescript
import { Priority } from '@/types/task';

interface PriorityBadgeProps {
  priority: Priority;
}

export function PriorityBadge({ priority }: PriorityBadgeProps) {
  const colors = {
    high: 'bg-red-500',
    medium: 'bg-yellow-500',
    low: 'bg-green-500',
  };
  
  return (
    <span className={`px-2 py-1 rounded text-xs font-bold ${colors[priority]}`}>
      {priority.toUpperCase()}
    </span>
  );
}
```

---

### Step 1.4: Update TaskCard with Priority

**File**: `frontend/components/tasks/TaskCard.tsx`

Add PriorityBadge import and render:

```typescript
import { PriorityBadge } from './PriorityBadge';

// In component render:
<div className="flex items-center gap-2">
  <PriorityBadge priority={task.priority} />
  {/* ... existing content */}
</div>
```

**Test**:
```bash
cd frontend
npm run dev
# Navigate to /dashboard and verify priority badges display
```

---

### Phase 1 Validation

- [ ] Tasks display priority badges (color-coded)
- [ ] Priority filter works correctly
- [ ] Sorting by priority works
- [ ] All existing tests pass
- [ ] No console errors

---

## Phase 2: Tags System (6-8 hours)

### Step 2.1: Create Database Migration

**File**: `backend/alembic/versions/001_add_tag_tables.py`

Run migration:
```bash
cd backend
alembic upgrade head
```

Verify tables created:
```bash
psql $DATABASE_URL -c "\dt tag task_tags"
```

---

### Step 2.2: Implement Tag Service

**File**: `backend/app/services/tag_service.py` (new)

Implement CRUD operations with user isolation.

**Test**:
```bash
pytest backend/tests/unit/test_tag_service.py -v
```

---

### Step 2.3: Create Tag API Endpoints

**File**: `backend/app/api/tags.py` (new)

Implement endpoints per api-contracts.md.

**Test**:
```bash
# Create tag
curl -X POST http://localhost:8000/api/v1/tags \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "urgent", "color": "#FF6B6B"}'

# List tags
curl http://localhost:8000/api/v1/tags \
  -H "Authorization: Bearer $TOKEN"
```

---

### Step 2.4: Build TagInput Component

**File**: `frontend/components/tasks/TagInput.tsx` (new)

Implement autocomplete with existing tags.

---

### Step 2.5: Update TaskCard with Tags

**File**: `frontend/components/tasks/TaskCard.tsx`

Add tag display:

```typescript
<div className="flex flex-wrap gap-1 mt-2">
  {task.tags.map(tag => (
    <span 
      key={tag.id}
      className="px-2 py-1 rounded text-xs"
      style={{ backgroundColor: tag.color + '40', color: tag.color }}
    >
      #{tag.name}
    </span>
  ))}
</div>
```

**Test**:
```bash
# Verify tags display on tasks
# Test tag creation and assignment
# Test filtering by tag
```

---

### Phase 2 Validation

- [ ] Tags can be created and deleted
- [ ] Multiple tags can be assigned to tasks
- [ ] Tag filtering works
- [ ] Tag autocomplete functions
- [ ] User isolation enforced (can't see other users' tags)

---

## Phase 3: Search/Filter/Sort (8-10 hours)

### Step 3.1: Add Search Index

**File**: `backend/alembic/versions/004_add_search_indexes.py`

Create GIN index for full-text search.

---

### Step 3.2: Implement Search Service

**File**: `backend/app/services/search_service.py` (new)

Use PostgreSQL tsvector/tsquery.

---

### Step 3.3: Create Search Endpoint

**File**: `backend/app/api/search.py` (new)

Implement per api-contracts.md.

**Test**:
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "quarterly review", "filters": {"priority": ["high"]}}'
```

---

### Step 3.4: Build Search Page

**File**: `frontend/app/(protected)/search/page.tsx` (new)

Create search UI with filters.

---

### Phase 3 Validation

- [ ] Search returns results in <500ms
- [ ] Multiple filters combine correctly
- [ ] Sorting works for all fields
- [ ] Pagination functions
- [ ] Empty results handled gracefully

---

## Phase 4: Recurring Tasks (10-12 hours)

### Step 4.1: Create Recurring Series Migration

**File**: `backend/alembic/versions/003_add_recurrence_tables.py`

---

### Step 4.2: Implement Recurrence Service

**File**: `backend/app/services/recurrence_service.py` (new)

Implement next instance calculation.

---

### Step 4.3: Auto-Generate on Completion

**File**: `backend/app/api/tasks.py`

Modify complete endpoint to trigger recurrence generation.

---

### Phase 4 Validation

- [ ] Recurring series can be created
- [ ] Next instance generated on completion
- [ ] Pause/resume works
- [ ] Delete series vs instance works correctly

---

## Phase 5: Reminders with Dapr (12-16 hours)

### Step 5.1: Deploy Dapr

```bash
kubectl apply -f k8s/dapr-deployment.yaml
```

Verify:
```bash
kubectl get pods -l app=dapr
```

---

### Step 5.2: Create Reminder Migration

**File**: `backend/alembic/versions/002_add_reminder_tables.py`

---

### Step 5.3: Implement Dapr Reminder Service

**File**: `backend/app/services/reminder_service.py`

---

### Phase 5 Validation

- [ ] Reminders scheduled correctly
- [ ] Notifications delivered on time
- [ ] Retry logic works
- [ ] Acknowledgment tracked

---

## Phase 6: Event Publishing with Kafka (10-14 hours)

### Step 5.1: Deploy Kafka

```bash
kubectl apply -f k8s/kafka-deployment.yaml
docker-compose up -d kafka  # For local dev
```

---

### Step 6.2: Implement Event Publisher

**File**: `backend/app/events/publisher.py`

---

### Phase 6 Validation

- [ ] Events published on CRUD operations
- [ ] SSE stream delivers events in real-time
- [ ] Event history accessible
- [ ] Kafka failure handled gracefully

---

## Phase 7: Integration Testing (8-10 hours)

### Run Full Test Suite

```bash
# Backend
cd backend
pytest tests/ -v --cov=app

# Frontend
cd frontend
npm test
npm run test:e2e  # If Playwright configured
```

### Performance Testing

```bash
# Load test search endpoint
ab -n 1000 -c 10 http://localhost:8000/api/v1/search

# Verify p95 < 500ms
```

---

## Rollback Procedures

### Per-Phase Rollback

```bash
# Phase 2 (Tags)
alembic downgrade -1

# Phase 4 (Recurrence)
alembic downgrade 003

# Phase 5 (Reminders)
alembic downgrade 002

# Phase 6 (Kafka)
kubectl delete -f k8s/kafka-deployment.yaml
```

### Full Rollback

```bash
# Revert all migrations
alembic downgrade base

# Remove infrastructure
kubectl delete -f k8s/dapr-deployment.yaml
kubectl delete -f k8s/kafka-deployment.yaml

# Revert code
git checkout <previous-commit>
```

---

## Next Steps

After completing all phases:

1. Deploy to staging environment
2. Run user acceptance testing
3. Monitor metrics for 1 week
4. Deploy to production
5. Update user documentation

---

## Support

- **API Documentation**: http://localhost:8000/docs
- **Spec Documentation**: specs/009-advanced-features/spec.md
- **Implementation Plan**: specs/009-advanced-features/plan.md
- **Data Model**: specs/009-advanced-features/data-model.md
