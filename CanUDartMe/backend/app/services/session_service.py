from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.game_session import GameSession, SessionStatus
from app.models.group import Group
from app.schemas.game import SessionCreate
from app.services.game_engine import SessionState, PlayerState
from app.models.user import User


async def create_session(db: AsyncSession, data: SessionCreate) -> GameSession:
    session = GameSession(
        group_id=data.group_id,
        dart_travel_time=data.dart_travel_time,
        max_players=data.max_players,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def list_active_sessions(db: AsyncSession) -> list[GameSession]:
    stmt = (
        select(GameSession)
        .where(GameSession.status.in_([SessionStatus.WAITING, SessionStatus.ACTIVE]))
        .order_by(GameSession.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_session(db: AsyncSession, session_id: str) -> GameSession | None:
    return await db.get(GameSession, session_id)


async def initialize_session_state(session: GameSession, players: list[User]) -> SessionState:
    """Build a fresh in-memory + Redis state for a newly starting session."""
    state = SessionState(
        session_id=session.id,
        group_id=session.group_id,
        dart_travel_time=session.dart_travel_time,
        players={
            u.id: PlayerState(user_id=u.id, profile_name=u.profile_name)
            for u in players
        },
        status="active",
    )
    await state.save()
    return state
