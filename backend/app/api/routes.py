"""Route aggregation module.

This module imports and aggregates all API routers for inclusion
in the main FastAPI application.
"""

from fastapi import APIRouter

# Import routers from submodules
from app.api.tasks import router as tasks_router
from app.api.categories import router as categories_router
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.tags import router as tags_router
from app.api.task_tags import router as task_tags_router
from app.api.search import router as search_router
from app.api.recurring import router as recurring_router
from app.api.reminders import router as reminders_router
from app.api.events import router as events_router

# Create main API router
api_router = APIRouter()

# Include auth router first (unauthenticated routes)
api_router.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

# Include routers with versioned prefixes
api_router.include_router(tasks_router, prefix="/api/v1/tasks", tags=["Tasks"])
api_router.include_router(categories_router, prefix="/api/v1/categories", tags=["Categories"])
api_router.include_router(tags_router, prefix="/api/v1/tags", tags=["Tags"])
api_router.include_router(task_tags_router, prefix="/api/v1", tags=["Task-Tags"])
api_router.include_router(search_router, prefix="/api/v1/search", tags=["Search"])
api_router.include_router(recurring_router, prefix="/api/v1/recurring", tags=["Recurring"])
api_router.include_router(reminders_router, prefix="/api/v1/reminders", tags=["Reminders"])
api_router.include_router(events_router, prefix="/api/v1/events", tags=["Events"])

# Include chat router (AI endpoints)
api_router.include_router(chat_router, prefix="/api/v1", tags=["Chat"])


