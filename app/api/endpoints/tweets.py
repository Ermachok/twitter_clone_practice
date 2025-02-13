from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db

from app.models.tweet import Tweet
from app.models.user import User
from app.models.like import Like

from app.schemas.tweet import TweetCreate, TweetResponse, TweetListResponse

router = APIRouter(prefix="/api/tweets", tags=["Tweets"])


@router.post("/", response_model=TweetResponse)
async def create_tweet(
        tweet_data: TweetCreate,
        api_key: str = Header(...),
        db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.name == api_key))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tweet = Tweet(content=tweet_data.content, author_id=user.id)
    db.add(tweet)
    await db.commit()
    await db.refresh(tweet)

    return {"result": True, "tweet_id": tweet.id}


@router.get("/", response_model=TweetListResponse)
async def get_tweets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tweet).order_by(Tweet.id.desc()))
    tweets = result.scalars().all()
    return {"result": True, "tweets": tweets}


@router.post("/{tweet_id}/like")
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

    like_result = await db.execute(select(Like).where(Like.user_id == user.id, Like.tweet_id == tweet.id))
    existing_like = like_result.scalars().first()
    if existing_like:
        raise HTTPException(status_code=400, detail="Tweet already liked")

    like = Like(user_id=user.id, tweet_id=tweet.id)
    db.add(like)
    await db.commit()
    return {"result": True, "message": "Tweet liked"}


@router.get("/{tweet_id}/likes")
async def get_tweet_likes(
        tweet_id: int,
        db: AsyncSession = Depends(get_db)
):
    tweet_result = await db.execute(select(Tweet).where(Tweet.id == tweet_id))
    tweet = tweet_result.scalars().first()
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    likes_result = await db.execute(select(Like).where(Like.tweet_id == tweet_id))
    likes = likes_result.scalars().unique().all()
    return {"result": True, "likes_count": len(likes)}


@router.delete("/{tweet_id}/like")
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

    like_result = await db.execute(select(Like).where(Like.user_id == user.id, Like.tweet_id == tweet_id))
    like = like_result.scalars().first()
    if not like:
        raise HTTPException(status_code=400, detail="Like not found")

    await db.delete(like)
    await db.commit()

    return {"result": True, "message": "Like removed"}
