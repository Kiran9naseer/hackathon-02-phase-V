"""Tag service implementing CRUD operations with ownership enforcement."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.tag import Tag
from app.schemas.tag_schema import TagCreate, TagUpdate

logger = logging.getLogger(__name__)


class TagService:
    """Service class for tag operations with ownership enforcement.

    All operations automatically filter by user_id to ensure
    users can only access their own tags.
    """

    def __init__(self, db: Session, user_id: UUID):
        """Initialize the tag service.

        Args:
            db: SQLAlchemy database session.
            user_id: The authenticated user's ID for ownership filtering.
        """
        self.db = db
        self.user_id = user_id

    def get(self, tag_id: UUID) -> Tag | None:
        """Get a tag by ID with ownership check."""
        result = self.db.execute(
            select(Tag).where(
                Tag.id == tag_id,
                Tag.user_id == self.user_id,
            )
        )
        tag = result.scalar_one_or_none()
        if tag:
            logger.info(f"Tag {tag_id} retrieved for user {self.user_id}")
        return tag

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """List tags with pagination."""
        base_query = select(Tag).where(Tag.user_id == self.user_id)

        count_query = select(func.count()).select_from(base_query.subquery())
        total = self.db.execute(count_query).scalar() or 0

        query = (
            base_query
            .order_by(Tag.name.asc())
            .offset(offset)
            .limit(limit)
        )

        tags = list(self.db.execute(query).scalars().all())

        logger.info(f"Listed {len(tags)} tags for user {self.user_id}")

        return {
            "items": tags,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def create(self, tag_data: TagCreate) -> Tag:
        """Create a new tag."""
        tag = Tag(
            user_id=self.user_id,
            name=tag_data.name.strip(),
            color=tag_data.color,
        )

        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)

        logger.info(f"Tag {tag.id} created for user {self.user_id}")
        return tag

    def update(self, tag_id: UUID, tag_data: TagUpdate) -> Tag | None:
        """Update a tag with ownership check."""
        tag = self.get(tag_id)
        if not tag:
            return None

        update_data = tag_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                if field == 'name':
                    value = value.strip()
                setattr(tag, field, value)

        tag.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(tag)

        logger.info(f"Tag {tag_id} updated for user {self.user_id}")
        return tag

    def delete(self, tag_id: UUID) -> bool:
        """Delete a tag with ownership check."""
        tag = self.get(tag_id)
        if not tag:
            return False

        self.db.delete(tag)
        self.db.commit()

        logger.info(f"Tag {tag_id} deleted for user {self.user_id}")
        return True
