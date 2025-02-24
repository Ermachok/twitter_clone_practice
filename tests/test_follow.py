import pytest
from sqlalchemy import select
from app.models.user import User
from app.models.follow import Follow


@pytest.mark.anyio
async def test_follow_user(test_session, client):
    """Test following a user (user1 -> user2)"""
    user1 = User(id=1, name="user1")
    user2 = User(id=2, name="user2")
    test_session.add_all([user1, user2])
    await test_session.commit()

    response = await client.post("/api/follows/2", headers={"api-key": "user1"})

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert data["message"] == "Followed successfully"

    # Check if follow record exists in DB
    follow = await test_session.execute(
        select(Follow).where(Follow.follower_id == 1, Follow.following_id == 2)
    )
    assert follow.scalar() is not None


@pytest.mark.anyio
async def test_follow_user_already_following(test_session, client):
    """Test following a user who is already followed (should return 400)"""
    user1 = User(id=1, name="user1")
    user2 = User(id=2, name="user2")
    follow = Follow(follower_id=1, following_id=2)

    test_session.add_all([user1, user2, follow])
    await test_session.commit()

    response = await client.post("/api/follows/2", headers={"api-key": "user1"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Already following this user"


@pytest.mark.anyio
async def test_unfollow_user(test_session, client):
    """Test unfollowing a user (user1 -> user2)"""
    user1 = User(id=1, name="user1")
    user2 = User(id=2, name="user2")
    follow = Follow(follower_id=1, following_id=2)

    test_session.add_all([user1, user2, follow])
    await test_session.commit()

    response = await client.delete("/api/follows/2", headers={"api-key": "user1"})

    assert response.status_code == 200
    assert response.json()["message"] == "Unfollowed successfully"

    # Check if follow record was deleted
    follow = await test_session.execute(
        select(Follow).where(Follow.follower_id == 1, Follow.following_id == 2)
    )
    assert follow.scalar() is None


@pytest.mark.anyio
async def test_unfollow_user_not_following(test_session, client):
    """Test unfollowing a user when not following them (should return 400)"""
    user1 = User(id=1, name="user1")
    user2 = User(id=2, name="user2")

    test_session.add_all([user1, user2])
    await test_session.commit()

    response = await client.delete("/api/follows/2", headers={"api-key": "user1"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Not following this user"


@pytest.mark.anyio
async def test_get_following(test_session, client):
    """Test retrieving the list of followed users"""
    user1 = User(id=1, name="user1")
    user2 = User(id=2, name="user2")
    user3 = User(id=3, name="user3")
    follow1 = Follow(follower_id=1, following_id=2)
    follow2 = Follow(follower_id=1, following_id=3)

    test_session.add_all([user1, user2, user3, follow1, follow2])
    await test_session.commit()

    response = await client.get("/api/follows/following", headers={"api-key": "user1"})

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert len(data["following"]) == 2
    assert {"id": 2, "name": "user2"} in data["following"]
    assert {"id": 3, "name": "user3"} in data["following"]


@pytest.mark.anyio
async def test_get_followers(test_session, client):
    """Test retrieving the list of followers"""
    user1 = User(id=1, name="user1")
    user2 = User(id=2, name="user2")
    user3 = User(id=3, name="user3")
    follow1 = Follow(follower_id=2, following_id=1)
    follow2 = Follow(follower_id=3, following_id=1)

    test_session.add_all([user1, user2, user3, follow1, follow2])
    await test_session.commit()

    response = await client.get("/api/follows/followers", headers={"api-key": "user1"})

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert len(data["followers"]) == 2
    assert {"id": 2, "name": "user2"} in data["followers"]
    assert {"id": 3, "name": "user3"} in data["followers"]
