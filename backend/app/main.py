import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.dependencies.database import init_db
from app.api.routes import api_router
from app.api.chat import router as chat_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
import asyncio
from app.dependencies.database import init_db, get_db
from app.services.reminder_service import ReminderService
from app.events.consumer import start_event_consumer
from uuid import UUID

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for database initialization and cleanup."""
    logger.info("Starting up: initializing database...")
    init_db()
    
    # Skip background tasks if testing
    if os.getenv("TESTING") == "true":
        logger.info("Testing mode active: skipping background tasks.")
        yield
        return

    # Start background maintenance task
    maintenance_task = asyncio.create_task(run_maintenance())
    
    # Start Kafka consumer for real-time events
    consumer_task = await start_event_consumer()
    
    yield
    
    # Clean up background tasks
    maintenance_task.cancel()
    consumer_task.cancel()
    try:
        await asyncio.gather(maintenance_task, consumer_task, return_exceptions=True)
    except asyncio.CancelledError:
        pass
    logger.info("Shutting down...")

async def run_maintenance():
    """Background loop for system maintenance."""
    while True:
        try:
            logger.info("Running background maintenance...")
            # We need a fresh DB session
            from app.dependencies.database import SessionLocal
            with SessionLocal() as db:
                # System-level maintenance (dummy user id for now or refactor service)
                service = ReminderService(db, UUID(int=0))
                await service.check_overdue_tasks()
                await service.process_due_reminders()
        except Exception as e:
            logger.error(f"Maintenance task error: {e}")
        
        # Run every 5 minutes
        await asyncio.sleep(300)

app = FastAPI(
    title="Todo Backend API",
    version="1.0.0",
    lifespan=lifespan
)

# Exception Handlers
from app.core.error_handlers import http_exception_handler, generic_exception_handler
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
# api_router typically includes the chat_router, but including it here as requested.
app.include_router(api_router)

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Todo Backend API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
