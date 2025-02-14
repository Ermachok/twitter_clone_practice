from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.follow import Follow

router = APIRouter(prefix="/api/follows", tags=["Follows"])


@router.post("/{user_id}")
async def follow_user(
        user_id: int,
        api_key: str = Header(...),
        db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.name == api_key))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    target_user_result = await db.execute(select(User).where(User.id == user_id))
    target_user = target_user_result.scalars().first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    follow_result = await db.execute(
        select(Follow).where(Follow.follower_id == user.id, Follow.following_id == user_id))
    existing_follow = follow_result.scalars().first()
    if existing_follow:
        raise HTTPException(status_code=400, detail="Already following this user")

    follow = Follow(follower_id=user.id, following_id=user_id)
    db.add(follow)
    await db.commit()

    return {"result": True, "message": "Followed successfully"}


@router.delete("/{user_id}")
async def unfollow_user(
        user_id: int,
        api_key: str = Header(...),
        db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.name == api_key))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    follow_result = await db.execute(
        select(Follow).where(Follow.follower_id == user.id, Follow.following_id == user_id))
    follow = follow_result.scalars().first()
    if not follow:
        raise HTTPException(status_code=400, detail="Not following this user")

    await db.delete(follow)
    await db.commit()

    return {"result": True, "message": "Unfollowed successfully"}


@router.get("/following")
async def get_following(api_key: str = Header(...), db: AsyncSession = Depends(get_db)):
    user_result = await db.execute(select(User).where(User.name == api_key))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    following_result = await db.execute(select(Follow).where(Follow.follower_id == user.id))
    following = following_result.scalars().unique().all()

    following_users = [
        {"id": f.following_id,
         "name": (await db.execute(select(User.name).where(User.id == f.following_id))).scalar_one()}
        for f in following
    ]

    return {"result": True, "following": following_users}


@router.get("/followers")
async def get_followers(api_key: str = Header(...), db: AsyncSession = Depends(get_db)):
    user_result = await db.execute(select(User).where(User.name == api_key))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    followers_result = await db.execute(select(Follow).where(Follow.following_id == user.id))
    followers = followers_result.scalars().unique().all()

    followers_users = [
        {"id": f.follower_id,
         "name": (await db.execute(select(User.name).where(User.id == f.follower_id))).scalar_one()}
        for f in followers
    ]

    return {"result": True, "followers": followers_users}
