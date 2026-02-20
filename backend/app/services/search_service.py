"""Search service for advanced full-text search across tasks."""

import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, text, and_
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.tag import Tag
from app.models.task_tags import TaskTag

logger = logging.getLogger(__name__)

class SearchService:
    """Service for performing full-text search using PostgreSQL."""

    def __init__(self, db: Session, user_id: UUID):
        """Initialize with DB session and user context."""
        self.db = db
        self.user_id = user_id

    def search_tasks(
        self,
        query: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category_id: Optional[UUID] = None,
        tag_ids: Optional[List[UUID]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> dict:
        """
        Perform full-text search on tasks for the current user.
        
        Uses PostgreSQL full-text search on title and description.
        """
        # Base query with user isolation
        base_stmt = select(Task).where(Task.user_id == self.user_id)
        
        dialect_name = self.db.bind.dialect.name
        
        if query.strip():
            if dialect_name == 'postgresql':
                # PostgreSQL full-text search
                search_query = func.plainto_tsquery('english', query)
                search_vector = func.to_tsvector('english', Task.title + ' ' + func.coalesce(Task.description, ''))
                base_stmt = base_stmt.where(search_vector.op('@@')(search_query))
            else:
                # SQLite/other fallback: simple case-insensitive substring match
                # combining title and description for search
                base_stmt = base_stmt.where(
                    (Task.title.ilike(f"%{query}%")) | 
                    (Task.description.ilike(f"%{query}%"))
                )

        # Apply additional filters (Consistency with task_service)
        if status:
            base_stmt = base_stmt.where(Task.status == status)
        if priority:
            base_stmt = base_stmt.where(Task.priority == priority)
        if category_id:
            base_stmt = base_stmt.where(Task.category_id == category_id)
            
        if tag_ids:
            for tag_id in tag_ids:
                base_stmt = base_stmt.where(
                    Task.id.in_(
                        select(TaskTag.task_id).where(TaskTag.tag_id == tag_id)
                    )
                )

        # Count total matches
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.db.execute(count_stmt).scalar() or 0

        # Apply ranking and pagination
        if query.strip() and dialect_name == 'postgresql':
            # Rank based on relevance (PG only)
            rank = func.ts_rank(search_vector, search_query).label('relevance')
            base_stmt = base_stmt.order_by(rank.desc())
        else:
            base_stmt = base_stmt.order_by(Task.created_at.desc())
            
        final_stmt = base_stmt.offset(offset).limit(limit)
        
        results = self.db.execute(final_stmt).scalars().all()
        
        logger.info(f"Search for '{query}' returned {len(results)} results for user {self.user_id}")

        return {
            "items": results,
            "total": total,
            "query": query,
            "limit": limit,
            "offset": offset
        }
