"""Task-Tag association API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.core.exceptions import NotFoundException
from app.models.task import Task
from app.models.tag import Tag
from app.models.task_tags import TaskTag

router = APIRouter()


@router.post("/tasks/{task_id}/tags/{tag_id}", status_code=status.HTTP_201_CREATED)
async def add_tag_to_task(
    task_id: UUID,
    tag_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a tag to a task.
    
    Args:
        task_id: UUID of the task
        tag_id: UUID of the tag to add
        user_id: Authenticated user ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        NotFoundException: If task or tag not found or not owned by user
    """
    # Verify task exists and belongs to user
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()
    
    if not task:
        raise NotFoundException(detail="Task not found")
    
    # Verify tag exists and belongs to user
    tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.user_id == user_id
    ).first()
    
    if not tag:
        raise NotFoundException(detail="Tag not found")
    
    # Check if association already exists
    existing = db.query(TaskTag).filter(
        TaskTag.task_id == task_id,
        TaskTag.tag_id == tag_id
    ).first()
    
    if existing:
        return {"message": "Tag already associated with task"}
    
    # Create association
    task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
    db.add(task_tag)
    db.commit()
    
    return {"message": "Tag added to task successfully"}


@router.delete("/tasks/{task_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag_from_task(
    task_id: UUID,
    tag_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a tag from a task.
    
    Args:
        task_id: UUID of the task
        tag_id: UUID of the tag to remove
        user_id: Authenticated user ID
        db: Database session
        
    Returns:
        None (204 No Content)
        
    Raises:
        NotFoundException: If task or tag not found or not owned by user
    """
    # Verify task exists and belongs to user
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()
    
    if not task:
        raise NotFoundException(detail="Task not found")
    
    # Find and delete association
    task_tag = db.query(TaskTag).filter(
        TaskTag.task_id == task_id,
        TaskTag.tag_id == tag_id
    ).first()
    
    if not task_tag:
        raise NotFoundException(detail="Tag association not found")
    
    db.delete(task_tag)
    db.commit()
    
    return None
