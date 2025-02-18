from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.follow import Follow
from app.models.like import Like
from app.models.media import Media
from app.models.tweet import Tweet
from app.models.user import User
from app.schemas.tweet import TweetCreate, TweetResponse

router = APIRouter(prefix="/api/tweets", tags=["Tweets"])


@router.post("", response_model=TweetResponse)
async def create_tweet(
    tweet_data: TweetCreate,
    api_key: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.name == api_key))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tweet = Tweet(content=tweet_data.tweet_data, author_id=user.id)
    db.add(tweet)
    await db.commit()
    await db.refresh(tweet)

    if tweet_data.tweet_media_ids:
        for media_id in tweet_data.tweet_media_ids:
            media = await db.execute(select(Media).where(Media.id == media_id))
            media_obj = media.scalars().first()
            if media_obj:
                media_obj.tweet_id = tweet.id
                db.add(media_obj)

        await db.commit()

    return {"result": True, "tweet_id": tweet.id}


@router.get("")
async def get_user_feed(
    api_key: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.name == api_key))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    following_result = await db.execute(
        select(Follow.following_id).where(Follow.follower_id == user.id)
    )
    following_ids = [row[0] for row in following_result.all()]
    following_ids.append(user.id)

    if not following_ids:
        return {"result": True, "tweets": []}

    tweets_result = await db.execute(
        select(Tweet)
        .where(Tweet.author_id.in_(following_ids))
        .order_by(Tweet.id.desc())
    )
    tweets = tweets_result.scalars().all()

    response = []
    for tweet in tweets:

        author_result = await db.execute(
            select(User).where(User.id == tweet.author_id)
        )
        author = author_result.scalars().first()

        likes_result = await db.execute(
            select(Like).where(Like.tweet_id == tweet.id)
        )
        likes = likes_result.scalars().all()
        likes_data = []
        for like in likes:
            user_like_result = await db.execute(
                select(User.name).where(User.id == like.user_id)
            )
            user_like = user_like_result.scalars().first()
            likes_data.append(
                {
                    "user_id": like.user_id,
                    "name": user_like if user_like else "Unknown",
                }
            )

        attachments_result = await db.execute(
            select(Media.file_path).where(Media.tweet_id == tweet.id)
        )
        attachments = [row[0] for row in attachments_result.all()]

        response.append(
            {
                "id": tweet.id,
                "content": tweet.content,
                "attachments": attachments,
                "author": {"id": author.id, "name": author.name},
                "likes": likes_data,
            }
        )

    return {"result": True, "tweets": response}


@router.delete("/{tweet_id}")
async def delete_tweet(
    tweet_id: int,
    api_key: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.name == api_key))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tweet_result = await db.execute(select(Tweet).where(Tweet.id == tweet_id))
    tweet = tweet_result.scalars().first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    if tweet.author_id != user.id:
        raise HTTPException(
            status_code=403, detail="You can only delete your own tweets"
        )

    await db.delete(tweet)
    await db.commit()

    return {"result": True}


@router.post("/{tweet_id}/likes")
async def like_tweet(
    tweet_id: int,
    api_key: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.name == api_key))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tweet_result = await db.execute(select(Tweet).where(Tweet.id == tweet_id))
    tweet = tweet_result.scalars().first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    like_result = await db.execute(
        select(Like).where(Like.user_id == user.id, Like.tweet_id == tweet.id)
    )
    existing_like = like_result.scalars().first()
    if existing_like:
        raise HTTPException(status_code=400, detail="Tweet already liked")

    like = Like(user_id=user.id, tweet_id=tweet.id)
    db.add(like)
    await db.commit()
    return {"result": True, "message": "Tweet liked"}


@router.get("/{tweet_id}/likes")
async def get_tweet_likes(tweet_id: int, db: AsyncSession = Depends(get_db)):
    tweet_result = await db.execute(select(Tweet).where(Tweet.id == tweet_id))
    tweet = tweet_result.scalars().first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    likes_result = await db.execute(
        select(Like).where(Like.tweet_id == tweet_id)
    )
    likes = likes_result.scalars().unique().all()
    return {"result": True, "likes_count": len(likes)}


@router.delete("/{tweet_id}/likes")
async def unlike_tweet(
    tweet_id: int,
    api_key: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.name == api_key))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tweet_result = await db.execute(select(Tweet).where(Tweet.id == tweet_id))
    tweet = tweet_result.scalars().first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    like_result = await db.execute(
        select(Like).where(Like.user_id == user.id, Like.tweet_id == tweet_id)
    )
    like = like_result.scalars().first()
    if not like:
        raise HTTPException(status_code=400, detail="Like not found")

    await db.delete(like)
    await db.commit()

    return {"result": True, "message": "Like removed"}
