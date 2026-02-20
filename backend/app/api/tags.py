"""Tags API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.core.exceptions import NotFoundException
from app.schemas.tag_schema import (
    TagCreate,
    TagUpdate,
    TagResponse,
    TagListResponse,
)
from app.services.tag_service import TagService

router = APIRouter()


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new tag for the authenticated user."""
    service = TagService(db, user_id)
    return service.create(tag_data)


@router.get("/", response_model=TagListResponse)
async def list_tags(
    limit: int = 100,
    offset: int = 0,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all tags for the authenticated user."""
    service = TagService(db, user_id)
    return service.list(limit=limit, offset=offset)


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific tag by ID."""
    service = TagService(db, user_id)
    tag = service.get(tag_id)
    if not tag:
        raise NotFoundException(detail="Tag not found")
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: UUID,
    tag_data: TagUpdate,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing tag."""
    service = TagService(db, user_id)
    tag = service.update(tag_id, tag_data)
    if not tag:
        raise NotFoundException(detail="Tag not found")
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a tag."""
    service = TagService(db, user_id)
    success = service.delete(tag_id)
    if not success:
        raise NotFoundException(detail="Tag not found")
    return None
