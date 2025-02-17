import os
import shutil

from fastapi import APIRouter, File, UploadFile, Depends, Header, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.media import Media
from app.models.user import User

router = APIRouter(prefix="/api/medias", tags=["Media"])

UPLOAD_DIR = "uploads"


@router.post("")
async def upload_media(
        api_key: str = Header(...),
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.name == api_key))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    media = Media(file_path=file_path)
    db.add(media)
    await db.commit()
    await db.refresh(media)

    return {"result": True, "media_id": media.id}
