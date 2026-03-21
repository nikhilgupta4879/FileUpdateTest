from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services import group_service
from app.schemas.group import GroupCreate, GroupPublic, JoinGroupRequest
from app.models.group import Group

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=GroupPublic, status_code=201)
async def create_group(
    data: GroupCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    group = await group_service.create_group(db, user_id, data)
    count = await group_service.get_member_count(db, group.id)
    return _to_public(group, count)


@router.get("/search", response_model=list[GroupPublic])
async def search_groups(q: str, db: AsyncSession = Depends(get_db)):
    groups = await group_service.search_groups(db, q)
    results = []
    for g in groups:
        count = await group_service.get_member_count(db, g.id)
        results.append(_to_public(g, count))
    return results


@router.post("/join", status_code=200)
async def join_group(
    data: JoinGroupRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    group = await db.get(Group, data.group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found.")
    count = await group_service.get_member_count(db, data.group_id)
    if count >= 6:
        raise HTTPException(status_code=400, detail="Group is full (max 6 members).")
    await group_service.join_group(db, user_id, data.group_id)
    return {"detail": "Joined group."}


@router.post("/{group_id}/favorite")
async def toggle_favorite(
    group_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    is_fav = await group_service.toggle_favorite(db, user_id, group_id)
    return {"is_favorite": is_fav}


def _to_public(group: Group, member_count: int) -> GroupPublic:
    return GroupPublic(
        id=group.id,
        name=group.name,
        owner_id=group.owner_id,
        is_public=group.is_public,
        member_count=member_count,
        created_at=group.created_at,
    )
