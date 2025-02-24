import pytest
from sqlalchemy import select
from app.models.user import User
from app.models.tweet import Tweet
from app.models.follow import Follow
from app.models.like import Like
from app.schemas.tweet import TweetCreate


@pytest.mark.anyio
async def test_create_tweet(test_session, client):
    """Test creating a tweet"""
    user = User(id=1, name="user1")
    test_session.add(user)
    await test_session.commit()

    response = await client.post(
        "/api/tweets",
        headers={"api-key": "user1"},
        json={"tweet_data": "Hello, world!", "tweet_media_ids": []},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert "tweet_id" in data

    # Check if tweet exists in DB
    tweet = await test_session.execute(select(Tweet).where(Tweet.id == data["tweet_id"]))
    assert tweet.scalar() is not None


@pytest.mark.anyio
async def test_get_user_feed(test_session, client):
    """Test retrieving user feed"""
    user1 = User(id=1, name="user1")
    user2 = User(id=2, name="user2")
    tweet1 = Tweet(id=1, content="Tweet 1", author_id=2)
    tweet2 = Tweet(id=2, content="Tweet 2", author_id=2)
    follow = Follow(follower_id=1, following_id=2)

    test_session.add_all([user1, user2, tweet1, tweet2, follow])
    await test_session.commit()

    response = await client.get("/api/tweets", headers={"api-key": "user1"})

    assert response.status_code == 200
    data = response.json()
    assert data["result"] is True
    assert len(data["tweets"]) == 2
    assert data["tweets"][0]["content"] == "Tweet 2"
    assert data["tweets"][1]["content"] == "Tweet 1"


@pytest.mark.anyio
async def test_delete_tweet(test_session, client):
    """Test deleting a tweet"""
    user = User(id=1, name="user1")
    tweet = Tweet(id=1, content="Delete me", author_id=1)

    test_session.add_all([user, tweet])
    await test_session.commit()

    response = await client.delete("/api/tweets/1", headers={"api-key": "user1"})

    assert response.status_code == 200
    assert response.json()["result"] is True

    # Check if tweet was deleted
    tweet = await test_session.execute(select(Tweet).where(Tweet.id == 1))
    assert tweet.scalar() is None


@pytest.mark.anyio
async def test_delete_tweet_not_author(test_session, client):
    """Test deleting someone else's tweet (should return 403)"""
    user1 = User(id=1, name="user1")
    user2 = User(id=2, name="user2")
    tweet = Tweet(id=1, content="Not yours", author_id=2)

    test_session.add_all([user1, user2, tweet])
    await test_session.commit()

    response = await client.delete("/api/tweets/1", headers={"api-key": "user1"})

    assert response.status_code == 403
    assert response.json()["detail"] == "You can only delete your own tweets"


@pytest.mark.anyio
async def test_like_tweet(test_session, client):
    """Test liking a tweet"""
    user = User(id=1, name="user1")
    tweet = Tweet(id=1, content="Like me", author_id=2)

    test_session.add_all([user, tweet])
    await test_session.commit()

    response = await client.post("/api/tweets/1/likes", headers={"api-key": "user1"})

    assert response.status_code == 200
    assert response.json()["message"] == "Tweet liked"

    # Check if like exists in DB
    like = await test_session.execute(select(Like).where(Like.user_id == 1, Like.tweet_id == 1))
    assert like.scalar() is not None


@pytest.mark.anyio
async def test_like_tweet_already_liked(test_session, client):
    """Test liking a tweet twice (should return 400)"""
    user = User(id=1, name="user1")
    tweet = Tweet(id=1, content="Like me", author_id=2)
    like = Like(user_id=1, tweet_id=1)

    test_session.add_all([user, tweet, like])
    await test_session.commit()

    response = await client.post("/api/tweets/1/likes", headers={"api-key": "user1"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Tweet already liked"


@pytest.mark.anyio
async def test_get_tweet_likes(test_session, client):
    """Test retrieving tweet likes count"""
    user1 = User(id=1, name="user1")
    user2 = User(id=2, name="user2")
    tweet = Tweet(id=1, content="Popular tweet", author_id=1)
    like1 = Like(user_id=1, tweet_id=1)
    like2 = Like(user_id=2, tweet_id=1)

    test_session.add_all([user1, user2, tweet, like1, like2])
    await test_session.commit()

    response = await client.get("/api/tweets/1/likes")

    assert response.status_code == 200
    assert response.json()["likes_count"] == 2


@pytest.mark.anyio
async def test_unlike_tweet(test_session, client):
    """Test unliking a tweet"""
    user = User(id=1, name="user1")
    tweet = Tweet(id=1, content="Unlike me", author_id=2)
    like = Like(user_id=1, tweet_id=1)

    test_session.add_all([user, tweet, like])
    await test_session.commit()

    response = await client.delete("/api/tweets/1/likes", headers={"api-key": "user1"})

    assert response.status_code == 200
    assert response.json()["message"] == "Like removed"

    like = await test_session.execute(select(Like).where(Like.user_id == 1, Like.tweet_id == 1))
    assert like.scalar() is None


@pytest.mark.anyio
async def test_unlike_tweet_not_liked(test_session, client):
    """Test unliking a tweet that wasn't liked (should return 400)"""
    user = User(id=1, name="user1")
    tweet = Tweet(id=1, content="Not liked", author_id=2)

    test_session.add_all([user, tweet])
    await test_session.commit()

    response = await client.delete("/api/tweets/1/likes", headers={"api-key": "user1"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Like not found"

