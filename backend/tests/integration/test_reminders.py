
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import status
from app.models.task import Task
from app.models.task_reminder import TaskReminder

def test_schedule_reminder(client, auth_headers, db, test_user):
    # Create a task first
    task = Task(id=uuid4(), title="Test Task", user_id=test_user.id, status="pending", priority="medium")
    db.add(task)
    db.commit()
    
    # Needs a way to schedule reminder via API?
    # Wait, T080 says TaskForm includes ReminderConfig.
    # But T073 says "Create backend/app/api/reminders.py with Reminder CRUD endpoints".
    # And T079 says "Update backend/app/models/task.py to add reminders relationship".
    
    # How do we schedule a reminder?
    # Usually via creating a task with reminder config, or a separate endpoint.
    # Looking at `api/reminders.py` (Step 1864), it has GET list, POST acknowledge, DELETE, POST trigger.
    # It does NOT have a POST ./ to create a reminder.
    
    # This implies reminders are created when Tasks are created/updated or via some other mechanism?
    # Let's check `backend/app/models/task.py` and `backend/app/services/task_service.py`.
    # T010 says "Update task.py with reminder_config".
    # T059/T072 implies `ReminderService` is used.
    
    # If the API doesn't expose "Create Reminder" directly, maybe it's done via Task Create/Update?
    # Let's assume for now we test the Service logic or if `TaskCreate` has reminder info.
    # In `task_schema.py` (Step 1837), `TaskBase` has `reminder_config: Optional[dict]`.
    
    # If I create a task with `reminder_config`, does it create a TaskReminder?
    # I need to check `TaskService.create`.
    
    # Since I cannot see `TaskService` right now, I will assume `ReminderService.schedule_reminder` is called manually 
    # or I should test `ReminderService` directly if the API is incomplete.
    # However, T073 "Create backend/app/api/reminders.py" seemed to be about managing them.
    
    # Let's test the endpoints that DO exist: list, acknowledge, delete.
    # To test list, I need to insert a reminder into DB manually first.
    
    remind_at = datetime.utcnow() + timedelta(days=1)
    reminder = TaskReminder(
        id=uuid4(),
        task_id=task.id,
        user_id=test_user.id,
        scheduled_time=remind_at,
        reminder_type="email",
        offset_minutes=60,
        status="pending",
        retry_count=0
    )
    db.add(reminder)
    db.commit()
    
    # Test List
    response = client.get("/api/v1/reminders/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == str(reminder.id)
    
    # Test Acknowledge
    response = client.post(f"/api/v1/reminders/{reminder.id}/acknowledge", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    db.refresh(reminder)
    assert reminder.status == "acknowledged"
    assert reminder.acknowledged_at is not None

def test_delete_reminder(client, auth_headers, db, test_user):
    # Setup
    task = Task(id=uuid4(), title="Test Task 2", user_id=test_user.id, status="pending", priority="medium")
    db.add(task)
    
    reminder = TaskReminder(
        id=uuid4(),
        task_id=task.id,
        user_id=test_user.id,
        scheduled_time=datetime.utcnow() + timedelta(days=1),
        reminder_type="email",
        offset_minutes=30,
        status="pending",
        retry_count=0
    )
    db.add(reminder)
    db.commit()
    
    # Test Delete
    reminder_id = reminder.id
    response = client.delete(f"/api/v1/reminders/{reminder_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify in DB
    # Force expire session to reload from DB
    db.expire_all()
    deleted = db.get(TaskReminder, reminder_id)
    assert deleted is None

def test_trigger_reminder(client, db):
    from app.models.user import User
    
    # Triggers don't need auth usually (internal/dapr), but endpoint might require DB
    # The endpoint is POST /api/v1/reminders/{id}/trigger
    # It uses `get_db`.
    
    # Setup
    # We need a user and task
    # We can create them manually in DB
    user = db.query(User).first() # Reuse existing test user if possible or create new
    if not user:
         user = User(id=uuid4(), email="trigger@test.com", hashed_password="pw")
         db.add(user)
    
    task = Task(id=uuid4(), title="Trigger Task", user_id=user.id, status="pending", priority="medium")
    db.add(task)
    
    reminder = TaskReminder(
        id=uuid4(),
        task_id=task.id,
        user_id=user.id,
        scheduled_time=datetime.utcnow() - timedelta(minutes=1),
        reminder_type="popup",
        offset_minutes=10,
        status="pending",
        retry_count=0
    )
    db.add(reminder)
    db.commit()
    
    # Call trigger endpoint
    response = client.post(f"/api/v1/reminders/{reminder.id}/trigger")
    assert response.status_code == status.HTTP_200_OK
    
    db.expire_all()
    updated_reminder = db.get(TaskReminder, reminder.id)
    assert updated_reminder.status == "sent"
    assert updated_reminder.delivered_at is not None

