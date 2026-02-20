import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from sqlalchemy.orm import Session

def test_chat_user_isolation(client: TestClient, db: Session):
    # 1. Create two users
    user_a_id = uuid4()
    user_b_id = uuid4()
    
    user_a = User(id=user_a_id, email="user_a@example.com", is_active=True, hashed_password="hashed")
    user_b = User(id=user_b_id, email="user_b@example.com", is_active=True, hashed_password="hashed")
    
    db.add(user_a)
    db.add(user_b)
    db.commit()
    
    # 2. User A creates a conversation
    conv_a = Conversation(user_id=user_a_id)
    db.add(conv_a)
    db.commit()
    db.refresh(conv_a)
    
    # 3. User B tries to access User A's conversation
    def override_get_current_user_b():
        return user_b_id
    
    app.dependency_overrides[get_current_user] = override_get_current_user_b
    
    payload = {
        "conversation_id": conv_a.id,
        "message": "I am User B trying to peek"
    }
    
    # Try with User B's ID in URL but User A's conversation_id in payload
    response = client.post(f"/api/v1/{user_b_id}/chat", json=payload)
    
    # The current implementation returns 404 if conversation doesn't exist FOR THAT USER
    assert response.status_code == 404
    assert "Conversation not found" in response.json()["error"]["message"]
    
    # 4. User B tries to use User A's ID in URL
    response = client.post(f"/api/v1/{user_a_id}/chat", json=payload)
    assert response.status_code == 403
    assert "User identity mismatch" in response.json()["error"]["message"]
    
    # Cleanup
    del app.dependency_overrides[get_current_user]

def test_chat_unauthorized(client: TestClient):
    # No override for get_current_user, should trigger 401 (if not overridden in conftest)
    # Actually conftest might not be overriding it by default for all tests.
    # Let's see if we can trigger a real 401 by NOT having a token.
    # But wait, the endpoint has Depends(get_current_user).
    
    payload = {"message": "hello"}
    # We need to make sure get_current_user isn't overridden to something that always works
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
        
    response = client.post(f"/api/v1/{uuid4()}/chat", json=payload)
    assert response.status_code == 401
