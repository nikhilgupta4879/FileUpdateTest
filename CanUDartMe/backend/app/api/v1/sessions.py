from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services import session_service
from app.schemas.game import SessionCreate, SessionPublic
from app.models.game_session import GameSession
from app.models.group import Group, GroupMember

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/", response_model=list[SessionPublic])
async def list_sessions(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns all active/waiting sessions.
    Sessions from favorite groups appear first.
    """
    sessions = await session_service.list_active_sessions(db)

    # Fetch user's favorite group IDs for ordering
    fav_stmt = select(GroupMember.group_id).where(
        GroupMember.user_id == user_id, GroupMember.is_favorite.is_(True)
    )
    fav_ids = set((await db.execute(fav_stmt)).scalars().all())

    def sort_key(s: GameSession):
        return (0 if s.group_id in fav_ids else 1, s.created_at)

    sessions.sort(key=sort_key)

    result = []
    for s in sessions:
        group = await db.get(Group, s.group_id)
        result.append(SessionPublic(
            id=s.id,
            group_id=s.group_id,
            group_name=group.name if group else "",
            status=s.status,
            current_round=s.current_round,
            dart_travel_time=s.dart_travel_time,
            player_count=len(s.scores),
            max_players=s.max_players,
            started_at=s.started_at,
            created_at=s.created_at,
        ))
    return result


@router.post("/", response_model=SessionPublic, status_code=201)
async def create_session(
    data: SessionCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    group = await db.get(Group, data.group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found.")
    session = await session_service.create_session(db, data)
    return SessionPublic(
        id=session.id,
        group_id=session.group_id,
        group_name=group.name,
        status=session.status,
        current_round=session.current_round,
        dart_travel_time=session.dart_travel_time,
        player_count=0,
        max_players=session.max_players,
        started_at=session.started_at,
        created_at=session.created_at,
    )
