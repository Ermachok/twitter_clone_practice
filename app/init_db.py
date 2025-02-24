import asyncio

from sqlalchemy import select

from app.database import async_session_maker
from app.models.follow import Follow
from app.models.like import Like
from app.models.tweet import Tweet
from app.models.user import User
from app.models.media import Media


async def create_test_data():
    async with async_session_maker() as session:
        user0 = User(name="test")
        user1 = User(name="Alice")
        user2 = User(name="Bob")
        user3 = User(name="Charlie")

        session.add_all([user0,user1, user2, user3])
        await session.commit()

        users = await session.execute(select(User))
        users = users.scalars().all()

        tweet1 = Tweet(content="Hello world!", author_id=users[0].id)
        tweet2 = Tweet(content="My second tweet!", author_id=users[1].id)
        tweet3 = Tweet(content="This is Charlie's tweet!", author_id=users[2].id)

        session.add_all([tweet1, tweet2, tweet3])
        await session.commit()

        tweets = await session.execute(select(Tweet))
        tweets = tweets.scalars().all()

        follow1 = Follow(follower_id=users[0].id, following_id=users[1].id)
        follow2 = Follow(follower_id=users[1].id, following_id=users[2].id)
        follow3 = Follow(follower_id=users[2].id, following_id=users[0].id)

        session.add_all([follow1, follow2, follow3])
        await session.commit()

        like1 = Like(user_id=users[0].id, tweet_id=tweets[1].id)
        like2 = Like(user_id=users[1].id, tweet_id=tweets[2].id)
        like3 = Like(user_id=users[2].id, tweet_id=tweets[0].id)

        session.add_all([like1, like2, like3])
        await session.commit()


if __name__ == "__main__":
    asyncio.run(create_test_data())
