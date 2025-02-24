import pytest
from app.models.user import User
from app.models.follow import Follow

@pytest.mark.anyio
async def test_get_current_user(test_session, client):
    """Test retrieving the current user's profile"""
    user1 = User(id=1, name="user1")
    user2 = User(id=2, name="user2")
    follow = Follow(follower_id=1, following_id=2)  # user1 follows user2

    test_session.add_all([user1, user2, follow])
    await test_session.commit()

    response = await client.get("/api/users/me", headers={"api-key": "user1"})

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert data["user"]["id"] == 1
    assert data["user"]["name"] == "user1"
    assert len(data["user"]["following"]) == 1
    assert data["user"]["following"][0]["id"] == 2
    assert data["user"]["following"][0]["name"] == "user2"


@pytest.mark.anyio
async def test_get_current_user_not_found(test_session, client):
    """Test retrieving current user when user does not exist (should return 404)"""
    response = await client.get("/api/users/me", headers={"api-key": "nonexistent_user"})

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.anyio
async def test_get_user_profile(test_session, client):
    """Test retrieving a user's profile"""
    user1 = User(id=1, name="user1")
    user2 = User(id=2, name="user2")
    user3 = User(id=3, name="user3")
    follow1 = Follow(follower_id=2, following_id=1)  # user2 follows user1
    follow2 = Follow(follower_id=3, following_id=1)  # user3 follows user1

    test_session.add_all([user1, user2, user3, follow1, follow2])
    await test_session.commit()

    response = await client.get("/api/users/1")

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert data["user"]["id"] == 1
    assert data["user"]["name"] == "user1"
    assert len(data["user"]["followers"]) == 2
    assert {"id": 2, "name": "user2"} in data["user"]["followers"]
    assert {"id": 3, "name": "user3"} in data["user"]["followers"]


@pytest.mark.anyio
async def test_get_user_profile_not_found(test_session, client):
    """Test retrieving a user profile that does not exist (should return 404)"""
    response = await client.get("/api/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
