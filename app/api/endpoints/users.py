from fastapi import APIRouter, Depends, HTTPException, Header

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me")
async def get_current_user(
        api_key: str = Header(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.name == api_key))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"result": True, "user": {"id": user.id, "name": user.name}}


@router.get("/search")
async def search_users(query: str, db: AsyncSession = Depends(get_db)):
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")

    result = await db.execute(
        select(User).where(func.lower(User.name).like(f"%{query.lower()}%")).limit(10)
    )
    users = result.scalars().unique().all()

    return {"result": True, "users": [{"id": u.id, "name": u.name} for u in users]}
