from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.follow import Follow
from app.models.user import User
from app.schemas.user import UserBase, UserProfile, UserResponse

router = APIRouter(prefix="/api/users", tags=["Users"])


async def get_user_with_follow_data(user_id: int, db: AsyncSession):
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    followers_result = await db.execute(
        select(User.id, User.name)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
    )
    followers = [UserBase(id=f.id, name=f.name) for f in followers_result.all()]

    following_result = await db.execute(
        select(User.id, User.name)
        .join(Follow, Follow.following_id == User.id)
        .where(Follow.follower_id == user_id)
    )
    following = [UserBase(id=f.id, name=f.name) for f in following_result.all()]

    return UserProfile(
        id=user.id, name=user.name, followers=followers, following=following
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    api_key: str = Header(...), db: AsyncSession = Depends(get_db)
):
    user_result = await db.execute(select(User).where(User.name == api_key))
    user = user_result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = await get_user_with_follow_data(user.id, db)

    return UserResponse(result=True, user=user_data)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    user_data = await get_user_with_follow_data(user_id, db)
    return UserResponse(result=True, user=user_data)
