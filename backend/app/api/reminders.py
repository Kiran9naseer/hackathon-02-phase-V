"""API endpoints for managing task reminders."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.reminder_schema import ReminderResponse, ReminderCreate, ReminderListResponse
from app.services.reminder_service import ReminderService

router = APIRouter()

@router.get("/", response_model=ReminderListResponse)
async def list_reminders(
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all pending reminders for the current user."""
    service = ReminderService(db, user_id)
    reminders = service.list_pending_reminders()
    return {
        "items": reminders,
        "total": len(reminders),
        "limit": 100,
        "offset": 0
    }

@router.post("/{reminder_id}/acknowledge")
async def acknowledge_reminder(
    reminder_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Acknowledge a reminder."""
    service = ReminderService(db, user_id)
    if not await service.acknowledge_reminder(reminder_id):
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder acknowledged"}

@router.post("/{reminder_id}/trigger")
async def trigger_reminder_endpoint(
    reminder_id: UUID,
    # This might need a secret or specific validation if called by Dapr
    db: Session = Depends(get_db)
):
    """Endpoint called by Dapr to trigger a reminder (callback)."""
    # Note: In a real scenario, we'd verify this is from Dapr
    # For now we use a simple trigger
    # Since we don't have user_id from Depends here easily (Dapr callback),
    # we use a system-level trigger.
    service = ReminderService(db, UUID(int=0)) # dummy user_id
    await service.trigger_reminder(reminder_id)
    return {"message": "Reminder processed"}

@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel and delete a reminder."""
    service = ReminderService(db, user_id)
    if not await service.cancel_reminder(reminder_id):
        raise HTTPException(status_code=404, detail="Reminder not found")
    return None
