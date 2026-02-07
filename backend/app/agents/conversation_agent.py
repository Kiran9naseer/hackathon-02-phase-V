from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository

class ConversationAgent:
    """Agent responsible for managing conversation state and history logic."""
    
    @staticmethod
    def load_or_create_conversation(
        db: Session, 
        user_id: UUID, 
        conversation_id: Optional[int] = None
    ) -> Tuple[Optional[Conversation], List[Message]]:
        """Load an existing conversation or create a new one."""
        if conversation_id:
            conv = ConversationRepository.get_conversation(db, conversation_id, user_id)
            if not conv:
                return None, []
            messages = MessageRepository.get_messages_for_conversation(db, conv.id)
            return conv, messages
        else:
            conv = ConversationRepository.create_conversation(db, user_id)
            return conv, []

    @staticmethod
    def format_history_for_ai(messages: List[Message]) -> List[Dict[str, str]]:
        """Format database messages into the standard AI role/content format."""
        return [{"role": msg.role, "content": msg.content} for msg in messages]
