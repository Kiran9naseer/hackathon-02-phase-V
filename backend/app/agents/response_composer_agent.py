from uuid import UUID
from sqlalchemy.orm import Session
from app.repositories.message_repository import MessageRepository
from app.schemas.chat_response import ChatResponse, ToolCall
from typing import List, Optional

class ResponseComposerAgent:
    """Agent responsible for composing the final AI response and persisting it to the database."""

    @staticmethod
    def compose_response(
        db: Session,
        user_id: UUID,
        conversation_id: int,
        user_message: str,
        ai_response_text: str,
        tool_calls: Optional[List[ToolCall]] = None
    ) -> ChatResponse:
        """Persist message history and return the structured response."""
        # 1. Persist User Message
        MessageRepository.create_message(
            db, 
            conversation_id=conversation_id, 
            user_id=user_id, 
            role="user", 
            content=user_message
        )
        
        # 2. Persist AI Message
        MessageRepository.create_message(
            db, 
            conversation_id=conversation_id, 
            user_id=user_id, 
            role="assistant", 
            content=ai_response_text
        )
        
        # 3. Return formatted response
        return ChatResponse(
            conversation_id=conversation_id,
            response=ai_response_text,
            tool_calls=tool_calls
        )
