from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.tweet import Tweet
from app.models.user import User
from app.schemas.tweet import TweetCreate, TweetResponse

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
