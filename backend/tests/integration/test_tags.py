import pytest
from fastapi import status
from uuid import uuid4
from app.dependencies.auth import create_access_token

def test_create_tag(client, auth_headers):
    tag_data = {
        "name": "Work",
        "color": "#FF0000"
    }
    response = client.post("/api/v1/tags/", json=tag_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Work"
    assert data["color"] == "#FF0000"
    assert "id" in data

def test_list_tags(client, auth_headers):
    # Create a couple of tags
    client.post("/api/v1/tags/", json={"name": "Work", "color": "#FF0000"}, headers=auth_headers)
    client.post("/api/v1/tags/", json={"name": "Personal", "color": "#00FF00"}, headers=auth_headers)
    
    response = client.get("/api/v1/tags/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] >= 2
    names = [item["name"] for item in data["items"]]
    assert "Work" in names
    assert "Personal" in names

def test_get_tag(client, auth_headers):
    # Create a tag
    create_response = client.post("/api/v1/tags/", json={"name": "Urgent", "color": "#FF0000"}, headers=auth_headers)
    tag_id = create_response.json()["id"]
    
    response = client.get(f"/api/v1/tags/{tag_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Urgent"

def test_update_tag(client, auth_headers):
    # Create a tag
    create_response = client.post("/api/v1/tags/", json={"name": "OldName", "color": "#FF0000"}, headers=auth_headers)
    tag_id = create_response.json()["id"]
    
    # Update it
    update_data = {"name": "NewName", "color": "#0000FF"}
    response = client.put(f"/api/v1/tags/{tag_id}", json=update_data, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "NewName"
    assert response.json()["color"] == "#0000FF"

def test_delete_tag(client, auth_headers):
    # Create a tag
    create_response = client.post("/api/v1/tags/", json={"name": "DeleteMe", "color": "#FF0000"}, headers=auth_headers)
    tag_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/api/v1/tags/{tag_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's gone
    get_response = client.get(f"/api/v1/tags/{tag_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_tag_user_isolation(client, db):
    from app.models.user import User
    
    # Create two different users in the database
    u1_id = uuid4()
    u2_id = uuid4()
    
    user1 = User(id=u1_id, email=f"u1-{u1_id}@example.com", hashed_password="pw")
    user2 = User(id=u2_id, email=f"u2-{u2_id}@example.com", hashed_password="pw")
    
    db.add(user1)
    db.add(user2)
    db.commit()

    user1_id = str(u1_id)
    user2_id = str(u2_id)
    
    token1 = create_access_token(user_id=user1_id)
    token2 = create_access_token(user_id=user2_id)
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # User 1 creates a tag
    client.post("/api/v1/tags/", json={"name": "User1Tag", "color": "#FF0000"}, headers=headers1)
    
    # User 2 should not see it
    response = client.get("/api/v1/tags/", headers=headers2)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0
    
    # User 2 creates their own tag
    client.post("/api/v1/tags/", json={"name": "User2Tag", "color": "#00FF00"}, headers=headers2)
    
    # User 2 should only see their own tag
    response = client.get("/api/v1/tags/", headers=headers2)
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "User2Tag"
