import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies.auth import get_current_user
from app.models.user import User
from sqlalchemy.orm import Session

# We'll use the client fixture from conftest.py if possible, 
# but for now we'll just redefine the override to work with the conftest setup.

def test_chat_endpoint_new_conversation(client: TestClient, db: Session):
    # 1. Create a mock user in the test database
    user_id = uuid4()
    mock_user = User(id=user_id, email="test@example.com", is_active=True, hashed_password="hashed")
    db.add(mock_user)
    db.commit()
    
    # 2. Override get_current_user to return this user's ID
    def override_get_current_user():
        return user_id
    
    app.dependency_overrides[get_current_user] = override_get_current_user

    # 3. Request
    payload = {
        "message": "Hello, add a task to buy milk"
    }
    response = client.post(f"/api/v1/{user_id}/chat", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert "conversation_id" in data
    assert "response" in data
    assert "buy milk" in data["response"].lower()
    
    # Cleanup override
    del app.dependency_overrides[get_current_user]

def test_chat_endpoint_list_tasks(client: TestClient, db: Session):
    # 1. Create a mock user
    user_id = uuid4()
    mock_user = User(id=user_id, email="list@example.com", is_active=True, hashed_password="hashed")
    db.add(mock_user)
    db.commit()
    
    # 2. Override get_current_user
    def override_get_current_user():
        return user_id
    
    app.dependency_overrides[get_current_user] = override_get_current_user

    # 3. Request
    payload = {
        "message": "show my tasks"
    }
    response = client.post(f"/api/v1/{user_id}/chat", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert "conversation_id" in data
    assert "response" in data
    assert "task" in data["response"].lower()
    
    # Cleanup override
    del app.dependency_overrides[get_current_user]
