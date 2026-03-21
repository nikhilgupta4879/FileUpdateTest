from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.group_service import find_user_by_profile
from app.schemas.user import UserPublic
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
async def get_me(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.get("/search", response_model=UserPublic)
async def find_friend(profile_name: str, db: AsyncSession = Depends(get_db)):
    user = await find_user_by_profile(db, profile_name)
    if not user:
        raise HTTPException(status_code=404, detail="No player with that profile name.")
    return user
