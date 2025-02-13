from fastapi import APIRouter, Depends, HTTPException, Header
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
