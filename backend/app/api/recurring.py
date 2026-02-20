"""API endpoints for managing recurring task series."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.recurring_schema import (
    RecurringSeriesCreate,
    RecurringSeriesResponse,
    RecurringSeriesUpdate
)
from app.services.recurring_service import RecurringService

router = APIRouter()

@router.post("/", response_model=RecurringSeriesResponse, status_code=status.HTTP_201_CREATED)
async def create_recurring_series(
    data: RecurringSeriesCreate,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new recurring task series."""
    service = RecurringService(db, user_id)
    return service.create_series(
        title=data.title,
        frequency=data.frequency,
        interval=data.interval,
        description=data.description,
        priority=data.priority,
        category_id=data.category_id,
        start_date=data.start_date,
        end_date=data.end_date
    )

@router.get("/", response_model=List[RecurringSeriesResponse])
async def list_recurring_series(
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all recurring series for the user."""
    service = RecurringService(db, user_id)
    return service.list_series()

@router.post("/{series_id}/pause")
async def pause_recurring_series(
    series_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pause a recurring task series."""
    service = RecurringService(db, user_id)
    if not service.toggle_pause(series_id, paused=True):
        raise HTTPException(status_code=404, detail="Series not found")
    return {"message": "Series paused"}

@router.post("/{series_id}/resume")
async def resume_recurring_series(
    series_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resume a paused recurring task series."""
    service = RecurringService(db, user_id)
    if not service.toggle_pause(series_id, paused=False):
        raise HTTPException(status_code=404, detail="Series not found")
    return {"message": "Series resumed"}

@router.delete("/{series_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring_series(
    series_id: UUID,
    delete_future_instances: bool = False,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a recurring series."""
    service = RecurringService(db, user_id)
    if not service.delete_series(series_id, delete_future_instances):
        raise HTTPException(status_code=404, detail="Series not found")
    return None
