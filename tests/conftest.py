import pytest
import asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.main import app
from fastapi.testclient import TestClient

from app.models.user import User
from app.models.base import Base
from app.models.follow import Follow
from app.models.tweet import Tweet
from app.models.like import Like
from app.models.media import Media

TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)

async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_users(session, num_users=5):
    """Создаёт пользователей в БД."""
    users = [User(name=f"user_{i}") for i in range(1, num_users + 1)]
    session.add_all(users)
    await session.commit()
    return users


async def create_tweets(session, users, num_tweets_per_user=3):
    """Создаёт твиты для каждого пользователя."""
    tweets = []
    for user in users:
        for i in range(num_tweets_per_user):
            tweets.append(Tweet(content=f"Tweet {i + 1} от {user.name}", author_id=user.id))
    session.add_all(tweets)
    await session.commit()
    return tweets


async def create_likes(session, users, tweets, num_likes=10):
    """Создаёт случайные лайки от пользователей к разным твитам."""
    likes = []
    for i in range(num_likes):
        user = users[i % len(users)]
        tweet = tweets[(i * 2) % len(tweets)]
        likes.append(Like(user_id=user.id, tweet_id=tweet.id))

    session.add_all(likes)
    await session.commit()


async def create_follows(session, users):
    """Создаёт подписки между пользователями (каждый подписан на следующего)."""
    follows = [
        Follow(follower_id=users[i].id, following_id=users[(i + 1) % len(users)].id)
        for i in range(len(users))
    ]
    session.add_all(follows)
    await session.commit()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    async def init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_session_maker() as session:
            users = await create_users(session, num_users=5)
            tweets = await create_tweets(session, users, num_tweets_per_user=3)
            await create_likes(session, users, tweets, num_likes=10)
            await create_follows(session, users)

    asyncio.run(init())
