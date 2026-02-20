
import pytest
from app.models.task import Task
from app.models.user import User
from app.dependencies.auth import create_access_token
from uuid import uuid4
from fastapi import status
import logging

logger = logging.getLogger(__name__)

def test_search_tasks_basic(client, db):
    # Setup users
    user_id = uuid4()
    user = User(id=user_id, email=f"user-{user_id}@example.com", hashed_password="pw")
    db.add(user)
    db.commit()
    
    token = create_access_token(user_id=str(user_id))
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create tasks via API or DB? API is cleaner integration test
    client.post("/api/v1/tasks/", json={"title": "Buy milk", "description": "Go to the store", "status": "pending", "priority": "medium"}, headers=headers)
    client.post("/api/v1/tasks/", json={"title": "Walk dog", "description": "In the park", "status": "pending", "priority": "high"}, headers=headers)
    client.post("/api/v1/tasks/", json={"title": "Write code", "description": "Finish the search feature", "status": "in_progress", "priority": "high"}, headers=headers)
    
    # Search for "milk"
    response = client.post("/api/v1/search/", json={"query": "milk"}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Buy milk"

    # Search for "park"
    response = client.post("/api/v1/search/", json={"query": "park"}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Walk dog"
    
    # Search for "code"
    response = client.post("/api/v1/search/", json={"query": "code"}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Write code"

def test_search_filters(client, db):
    # Setup users
    user_id = uuid4()
    user = User(id=user_id, email=f"user-{user_id}@example.com", hashed_password="pw")
    db.add(user)
    db.commit()
    
    token = create_access_token(user_id=str(user_id))
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create tasks
    # 1. High priority, Pending
    client.post("/api/v1/tasks/", json={"title": "Task A", "priority": "high", "status": "pending"}, headers=headers)
    # 2. High priority, In Progress
    client.post("/api/v1/tasks/", json={"title": "Task B", "priority": "high", "status": "in_progress"}, headers=headers)
    # 3. Low priority, Pending
    client.post("/api/v1/tasks/", json={"title": "Task C", "priority": "low", "status": "pending"}, headers=headers)
    
    # Filter by Priority High
    response = client.post("/api/v1/search/", json={"priority": "high"}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 2
    titles = sorted([t["title"] for t in data["items"]])
    assert titles == ["Task A", "Task B"]
    
    # Filter by Status Pending
    response = client.post("/api/v1/search/", json={"status": "pending"}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 2
    titles = sorted([t["title"] for t in data["items"]])
    assert titles == ["Task A", "Task C"]

    # Filter by Priority High AND Status Pending
    response = client.post("/api/v1/search/", json={"priority": "high", "status": "pending"}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Task A"

