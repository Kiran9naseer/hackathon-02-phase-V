"""Search API endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.task_schema import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter()

@router.post("/", response_model=SearchResponse)
async def search_tasks(
    request: SearchRequest,
    user_id: UUID = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform advanced full-text search on tasks with multi-criteria filtering.
    """
    service = SearchService(db, user_id)
    return service.search_tasks(
        query=request.query,
        status=request.status,
        priority=request.priority,
        category_id=request.category_id,
        tag_ids=request.tag_ids,
        limit=request.limit,
        offset=request.offset
    )
