
import pytest
import asyncio
from unittest.mock import AsyncMock
from fastapi import status
from app.api.events import notify_user, event_manager
import json

@pytest.mark.asyncio
async def test_notify_user_reaches_stream(client, auth_headers, test_user):
    # This test verifies that notify_user puts data into the EventManager
    # and the SSE generator can read it.
    
    user_id_str = str(test_user.id)
    event_type = "TestEvent"
    payload = {"foo": "bar"}
    
    # We can't easily test the full SSE stream with Starlette TestClient in a non-blocking way 
    # while also triggering the event in the same thread.
    # So we test the EventManager and the notify_user hook directly.
    
    queue = event_manager.subscribe(user_id_str)
    try:
        await notify_user(user_id_str, event_type, payload)
        
        # Check if it appeared in the queue
        event = await asyncio.wait_for(queue.get(), timeout=1.0)
        assert event["type"] == event_type
        assert event["payload"] == payload
    finally:
        event_manager.unsubscribe(user_id_str, queue)

def test_task_actions_publish_to_kafka(client, auth_headers, mock_publisher):
    # Verify that creating a task calls the Kafka publisher
    # Note: TaskService uses asyncio.create_task which runs in the background.
    # In tests, this might be unpredictable. 
    # But since we are using static mock_publisher, we can check its calls.
    
    mock_publisher.publish = AsyncMock(return_value=None)
    
    response = client.post("/api/v1/tasks/", json={"title": "Kafka Task", "priority": "medium"}, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    task_id = response.json()["id"]
    
    # Give background task a moment
    import time
    time.sleep(0.2)
    
    # Check if publish was called
    # It should be called with topic "task_events"
    mock_publisher.publish.assert_called()
    args, kwargs = mock_publisher.publish.call_args
    assert args[0] == "task_events"
    assert args[1]["type"] == "TaskCreated"
    assert args[1]["task_id"] == task_id

def test_task_completion_publishes_event(client, auth_headers, mock_publisher, db, test_user):
    from app.models.task import Task
    from uuid import uuid4
    
    task = Task(id=uuid4(), title="Complete Me", user_id=test_user.id, status="pending", priority="medium")
    db.add(task)
    db.commit()
    
    mock_publisher.publish = AsyncMock(return_value=None)
    
    response = client.post(f"/api/v1/tasks/{task.id}/complete", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    import time
    time.sleep(0.2)
    
    mock_publisher.publish.assert_called()
    args, kwargs = mock_publisher.publish.call_args
    assert args[1]["type"] == "TaskCompleted"
    assert args[1]["task_id"] == str(task.id)

