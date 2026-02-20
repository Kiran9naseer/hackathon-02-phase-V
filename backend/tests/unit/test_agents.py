import pytest
from uuid import uuid4
from unittest.mock import MagicMock
from app.agents.task_manager_agent import TaskManagerAgent
from app.agents.task_action_agent import TaskActionAgent
from app.agents.response_composer_agent import ResponseComposerAgent
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from sqlalchemy.orm import Session

@pytest.mark.asyncio
async def test_task_manager_agent_add_intent(db: Session):
    user_id = uuid4()
    message = "Add a task to buy bread"
    decision = await TaskManagerAgent.process_message(db, message, [], user_id)
    
    assert decision["action"] == "add_task"
    assert "bread" in decision["parameters"]["title"].lower()
    assert decision["requires_action_agent"] is True

@pytest.mark.asyncio
async def test_task_manager_agent_list_intent(db: Session):
    user_id = uuid4()
    message = "show my tasks"
    decision = await TaskManagerAgent.process_message(db, message, [], user_id)
    
    assert decision["action"] == "list_tasks"
    assert decision["requires_action_agent"] is True

def test_response_composer_agent(db: Session):
    user_id = uuid4()
    user = User(id=user_id, email="test@example.com", hashed_password="pw")
    db.add(user)
    db.commit()
    
    conv = Conversation(user_id=user_id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    
    response = ResponseComposerAgent.compose_response(
        db,
        user_id=user_id,
        conversation_id=conv.id,
        user_message="Hello",
        ai_response_text="Hi there",
        tool_calls=[]
    )
    
    assert response.conversation_id == conv.id
    assert response.response == "Hi there"
    
    # Verify messages were persisted
    messages = db.query(Message).filter(Message.conversation_id == conv.id).all()
    assert len(messages) == 2
    assert messages[0].role == MessageRole.USER.value
    assert messages[1].role == MessageRole.ASSISTANT.value
