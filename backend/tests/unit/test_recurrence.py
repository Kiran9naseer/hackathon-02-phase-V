
import pytest
from datetime import date, timedelta
from uuid import uuid4
from app.services.recurring_service import RecurringService
from app.models.recurring_series import RecurringTaskSeries
from app.models.task import Task

def test_calculate_next_date_daily():
    service = RecurringService(None, uuid4()) # None db is fine for this private method
    start = date(2024, 1, 1)
    
    # Daily, interval 1
    next_date = service._calculate_next_date(start, "daily", 1)
    assert next_date == date(2024, 1, 2)
    
    # Daily, interval 3
    next_date = service._calculate_next_date(start, "daily", 3)
    assert next_date == date(2024, 1, 4)

def test_calculate_next_date_weekly():
    service = RecurringService(None, uuid4())
    start = date(2024, 1, 1) # Monday
    
    # Weekly, interval 1
    next_date = service._calculate_next_date(start, "weekly", 1)
    assert next_date == date(2024, 1, 8)
    
    # Weekly, interval 2
    next_date = service._calculate_next_date(start, "weekly", 2)
    assert next_date == date(2024, 1, 15)

def test_calculate_next_date_monthly():
    service = RecurringService(None, uuid4())
    start = date(2024, 1, 15)
    
    # Monthly, interval 1
    next_date = service._calculate_next_date(start, "monthly", 1)
    assert next_date == date(2024, 2, 15)
    
    # Monthly, interval 12
    next_date = service._calculate_next_date(start, "monthly", 12)
    assert next_date == date(2025, 1, 15)
    
    # Check boundary (Jan 31 -> Feb 28)
    start_edge = date(2024, 1, 31)
    next_date = service._calculate_next_date(start_edge, "monthly", 1)
    assert next_date.month == 2
    assert next_date.day <= 28 # Implementation uses min(day, 28) for safety

def test_calculate_next_date_yearly():
    service = RecurringService(None, uuid4())
    start = date(2024, 1, 1)
    
    # Yearly, interval 1
    next_date = service._calculate_next_date(start, "yearly", 1)
    assert next_date == date(2025, 1, 1)

def test_recurrence_series_creation(db, test_user):
    service = RecurringService(db, test_user.id)
    
    series = service.create_series(
        title="Weekly Gym",
        frequency="weekly",
        interval=1,
        start_date=date(2024, 1, 1)
    )
    
    assert series.title == "Weekly Gym"
    assert series.user_id == test_user.id
    
    # Verify first instance created
    tasks = db.query(Task).filter(Task.recurrence_series_id == series.id).all()
    assert len(tasks) == 1
    assert tasks[0].due_date == date(2024, 1, 1)

def test_schedule_next_instance(db, test_user):
    service = RecurringService(db, test_user.id)
    
    series = service.create_series(
        title="Daily Standup",
        frequency="daily",
        interval=1,
        start_date=date(2024, 1, 1)
    )
    
    # Initial task is for Jan 1
    # Now schedule next from Jan 1
    next_task = service.schedule_next_instance(series.id, date(2024, 1, 1))
    
    assert next_task is not None
    assert next_task.due_date == date(2024, 1, 2)
    assert next_task.recurrence_series_id == series.id

def test_end_date_enforcement(db, test_user):
    service = RecurringService(db, test_user.id)
    
    # Series ends on Jan 2
    series = service.create_series(
        title="Short Series",
        frequency="daily",
        interval=1,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 2)
    )
    
    # First instance on Jan 1 (already created by create_series)
    # Next should be on Jan 2
    next_task = service.schedule_next_instance(series.id, date(2024, 1, 1))
    assert next_task is not None
    assert next_task.due_date == date(2024, 1, 2)
    
    # Next should be None (Jan 3 > Jan 2)
    one_more = service.schedule_next_instance(series.id, date(2024, 1, 2))
    assert one_more is None

