from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from uuid import UUID
import logging
import time
from typing import List, Optional

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.chat_request import ChatRequest
from app.schemas.chat_response import ChatResponse, ToolCall
from app.agents.conversation_agent import ConversationAgent
from app.agents.task_manager_agent import TaskManagerAgent
from app.agents.response_composer_agent import ResponseComposerAgent

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/{user_id}/chat", response_model=ChatResponse)


async def chat_with_agent(
    user_id: str,
    request: ChatRequest,
    response: Response,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user)
):
    """
    Stateless chat endpoint orchestrating the AI agent pipeline.
    """
    start_time = time.time()
    
    # 1. Authentication & Security Validation
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id format"
        )

    if current_user_id != user_uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User identity mismatch"
        )

    # 2. Load/Create Conversation (Ensures stateless persistence)
    conversation, messages = ConversationAgent.load_or_create_conversation(
        db, user_uuid, request.conversation_id
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Return 201 Created for new chat sessions
    if request.conversation_id is None:
        response.status_code = status.HTTP_201_CREATED

    # 3. Process Message with TaskManager Agent
    # Fetches history and determines intent/actions
    history = ConversationAgent.format_history_for_ai(messages)
    decision = await TaskManagerAgent.process_message(
        db,
        request.message, 
        history, 
        user_uuid
    )

    # 4. Extract Tool Calls
    # Logic for executing tools via TaskActionAgent is contained within TaskManagerAgent
    tool_calls_data = decision.get("tool_calls", [])
    tool_calls = [ToolCall(**tc) for tc in tool_calls_data] if tool_calls_data else []

    # 5. Compose Final Response & Persist History
    chat_response = ResponseComposerAgent.compose_response(
        db,
        user_id=user_uuid,
        conversation_id=conversation.id,
        user_message=request.message,
        ai_response_text=decision.get("response", ""),
        tool_calls=tool_calls
    )

    # Logging and Observability
    duration = int((time.time() - start_time) * 1000)
    logger.info(f"Chat request completed: user={user_id} duration={duration}ms")

    return chat_response
