"""Tasks API endpoints.

This module provides REST API endpoints for task CRUD operations.
All endpoints require authentication and enforce user ownership.
"""

from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.core.exceptions import NotFoundException
from app.schemas.task_schema import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)
from app.services.task_service import TaskService

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new task for the authenticated user.

    The user_id is automatically set from the authenticated user's token.
    
    Args:
        task_data: Task creation data
        tag_ids: Optional list of tag UUIDs to associate with the task

    Returns:
        TaskResponse: The created task with generated ID and timestamps.
    """
    service = TaskService(db, user_id)
    return service.create(task_data, tag_ids=task_data.tag_ids)


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category_id: Optional[UUID] = None,
    tag_ids: Optional[List[UUID]] = Query(None),
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List tasks for the authenticated user with optional filtering.

    Query Parameters:
        status: Filter by task status (pending, in_progress, completed, archived)
        priority: Filter by priority (low, medium, high)
        category_id: Filter by category UUID
        tag_ids: Filter by tag UUIDs (tasks must have ALL specified tags)
        sort_by: Sort field (created_at, updated_at, due_date, priority, title)
        sort_order: Sort order (asc or desc)
        limit: Maximum number of results (default 20)
        offset: Number of results to skip (default 0)

    Returns:
        TaskListResponse: Paginated list of tasks.
    """
    service = TaskService(db, user_id)
    return service.list(
        status=status,
        priority=priority,
        category_id=category_id,
        tag_ids=tag_ids,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific task by ID.

    Only returns the task if it belongs to the authenticated user.
    Returns 404 for non-existent or non-owned tasks.

    Returns:
        TaskResponse: The requested task.
    """
    service = TaskService(db, user_id)
    task = service.get(task_id)
    if not task:
        raise NotFoundException(detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing task.

    Only updates tasks owned by the authenticated user.
    Returns 404 for non-existent or non-owned tasks.
    
    Args:
        task_id: UUID of the task to update
        task_data: Task update data
        tag_ids: Optional list of tag UUIDs to replace existing tags

    Returns:
        TaskResponse: The updated task.
    """
    service = TaskService(db, user_id)
    task = service.update(task_id, task_data, tag_ids=task_data.tag_ids)
    if not task:
        raise NotFoundException(detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a task.

    Only deletes tasks owned by the authenticated user.
    Returns 404 for non-existent or non-owned tasks.

    Returns:
        204 No Content on successful deletion.
    """
    service = TaskService(db, user_id)
    success = service.delete(task_id)
    if not success:
        raise NotFoundException(detail="Task not found")
    return None


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark a task as completed.

    Only completes tasks owned by the authenticated user.
    Returns 404 for non-existent or non-owned tasks.

    Returns:
        TaskResponse: The completed task.
    """
    service = TaskService(db, user_id)
    task = service.complete(task_id)
    if not task:
        raise NotFoundException(detail="Task not found")
    return task
