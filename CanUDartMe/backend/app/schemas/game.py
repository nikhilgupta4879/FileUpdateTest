from pydantic import BaseModel, Field
from datetime import datetime
from app.models.game_session import SessionStatus


class SessionCreate(BaseModel):
    group_id: str
    dart_travel_time: float = Field(default=2.0, ge=0.5, le=2.0)
    max_players: int = Field(default=6, ge=2, le=6)


class SessionPublic(BaseModel):
    id: str
    group_id: str
    group_name: str = ""
    status: SessionStatus
    current_round: int
    dart_travel_time: float
    player_count: int = 0
    max_players: int
    started_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PlayerScore(BaseModel):
    user_id: str
    profile_name: str
    total_score: int
    strikes: int
    is_eliminated: bool
    is_winner: bool


# ---------------------------------------------------------------------------
# WebSocket message envelopes
# ---------------------------------------------------------------------------

class WsMessage(BaseModel):
    """Base WebSocket message."""
    event: str
    payload: dict = {}


class DartThrowPayload(BaseModel):
    """Sent by the throwing player."""
    target_user_id: str
    dart_type: str = "default"      # animation variant


class DartCatchPayload(BaseModel):
    """Sent by the receiving player."""
    region: str = Field(..., pattern="^(inner|middle|outer)$")
