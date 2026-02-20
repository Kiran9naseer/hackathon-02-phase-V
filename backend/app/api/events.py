"""SSE endpoint for real-time task events."""

import asyncio
import json
import logging
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.dependencies.auth import get_current_user
from uuid import UUID

logger = logging.getLogger(__name__)
router = APIRouter()

# Simple multi-user subscription manager
class EventManager:
    def __init__(self):
        self.queues: dict[str, list[asyncio.Queue]] = {}

    def subscribe(self, user_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        if user_id not in self.queues:
            self.queues[user_id] = []
        self.queues[user_id].append(queue)
        return queue

    def unsubscribe(self, user_id: str, queue: asyncio.Queue):
        if user_id in self.queues:
            self.queues[user_id].remove(queue)
            if not self.queues[user_id]:
                del self.queues[user_id]

    async def broadcast(self, user_id: str, event: dict):
        if user_id in self.queues:
            for queue in self.queues[user_id]:
                await queue.put(event)

event_manager = EventManager()

@router.get("/stream")
async def event_stream(
    request: Request,
    user_id: UUID = Depends(get_current_user)
):
    """Stream real-time events to the client using SSE."""
    user_id_str = str(user_id)
    queue = event_manager.subscribe(user_id_str)

    async def generate() -> AsyncGenerator[str, None]:
        try:
            while True:
                if await request.is_disconnected():
                    break
                
                event = await queue.get()
                yield f"data: {json.dumps(event)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            event_manager.unsubscribe(user_id_str, queue)

    return StreamingResponse(generate(), media_type="text/event-stream")

# Hook to allow other services to broadcast events through this manager
async def notify_user(user_id: str, event_type: str, payload: dict):
    await event_manager.broadcast(user_id, {
        "type": event_type,
        "payload": payload
    })
