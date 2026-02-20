import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies.auth import get_current_user
from app.models.user import User
from sqlalchemy.orm import Session

def test_chat_api_contract_success(client: TestClient, db: Session):
    user_id = uuid4()
    db.add(User(id=user_id, email="contract@example.com", hashed_password="pw"))
    db.commit()
    
    def override_get_current_user():
        return user_id
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    payload = {"message": "test message"}
    response = client.post(f"/api/v1/{user_id}/chat", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify contract
    assert "conversation_id" in data
    assert isinstance(data["conversation_id"], int)
    assert "response" in data
    assert isinstance(data["response"], str)
    assert "tool_calls" in data
    assert isinstance(data["tool_calls"], list)
    
    del app.dependency_overrides[get_current_user]

def test_chat_api_contract_invalid_payload(client: TestClient, db: Session):
    user_id = uuid4()
    db.add(User(id=user_id, email="contract2@example.com", hashed_password="pw"))
    db.commit()
    
    def override_get_current_user():
        return user_id
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    # Missing 'message'
    response = client.post(f"/api/v1/{user_id}/chat", json={})
    assert response.status_code == 422 # FastAPI validation error
    
    del app.dependency_overrides[get_current_user]

def test_chat_api_contract_wrong_user_format(client: TestClient):
    u_id = uuid4()
    def override_get_current_user():
        return u_id
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    # Invalid UUID format
    response = client.post("/api/v1/not-a-uuid/chat", json={"message": "hi"})
    assert response.status_code == 400
    assert "Invalid user_id format" in response.json()["error"]["message"]
    
    del app.dependency_overrides[get_current_user]
