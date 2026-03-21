import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String, ForeignKey("game_sessions.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, default=1)
    total_score: Mapped[int] = mapped_column(Integer, default=0)
    strikes: Mapped[int] = mapped_column(Integer, default=0)
    is_eliminated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_winner: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session: Mapped["GameSession"] = relationship(back_populates="scores")  # noqa: F821
    user: Mapped["User"] = relationship(back_populates="scores")  # noqa: F821
