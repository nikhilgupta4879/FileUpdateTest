"""
Core game engine — stateless helpers that compute outcomes and
mutate game state stored in Redis (fast) + Postgres (persistent).

Game rules:
  - Up to 6 players per session
  - Thrower selects a target → dart travels (configurable, max 2 s)
  - Catcher taps a board region before travel time expires
      → Caught:  catcher gets region points, thrower gets 1 strike
      → Missed:  thrower gets 10 pts (miss bonus), catcher gets 1 strike
  - 3 strikes → player eliminated
  - 3 rounds → highest surviving score wins
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from typing import Optional
from app.core.config import get_settings
from app.redis.connection import get_redis

settings = get_settings()

REGION_POINTS = {
    "inner": settings.BOARD_INNER_POINTS,
    "middle": settings.BOARD_MIDDLE_POINTS,
    "outer": settings.BOARD_OUTER_POINTS,
}
MISS_BONUS_POINTS = 10  # points the thrower earns when dart is not caught


@dataclass
class PlayerState:
    user_id: str
    profile_name: str
    score: int = 0
    strikes: int = 0
    is_eliminated: bool = False

    def add_strike(self) -> bool:
        """Returns True if player is now eliminated."""
        self.strikes += 1
        if self.strikes >= settings.STRIKES_TO_ELIMINATE:
            self.is_eliminated = True
        return self.is_eliminated

    def add_score(self, points: int):
        self.score += points


@dataclass
class SessionState:
    session_id: str
    group_id: str
    dart_travel_time: float
    players: dict[str, PlayerState] = field(default_factory=dict)
    current_round: int = 1
    pending_throw: Optional[dict] = None   # {thrower_id, target_id, dart_type}
    status: str = "waiting"               # waiting | active | finished

    # ------------------------------------------------------------------ #
    # Redis persistence                                                     #
    # ------------------------------------------------------------------ #
    def _key(self) -> str:
        return f"session_state:{self.session_id}"

    async def save(self):
        redis = await get_redis()
        await redis.set(self._key(), json.dumps(asdict(self)), ex=3600)

    @classmethod
    async def load(cls, session_id: str) -> Optional["SessionState"]:
        redis = await get_redis()
        raw = await redis.get(f"session_state:{session_id}")
        if not raw:
            return None
        data = json.loads(raw)
        players = {uid: PlayerState(**ps) for uid, ps in data.pop("players").items()}
        obj = cls(**data)
        obj.players = players
        return obj

    # ------------------------------------------------------------------ #
    # Game actions                                                          #
    # ------------------------------------------------------------------ #
    def active_players(self) -> list[PlayerState]:
        return [p for p in self.players.values() if not p.is_eliminated]

    def process_throw(self, thrower_id: str, target_id: str, dart_type: str) -> dict:
        """Record a pending throw. Returns event payload broadcast to all."""
        if self.pending_throw:
            raise ValueError("A dart is already in flight.")
        if thrower_id not in self.players or self.players[thrower_id].is_eliminated:
            raise ValueError("Thrower is not an active player.")
        if target_id not in self.players or self.players[target_id].is_eliminated:
            raise ValueError("Target is not an active player.")

        self.pending_throw = {"thrower_id": thrower_id, "target_id": target_id, "dart_type": dart_type}
        return {
            "thrower_id": thrower_id,
            "target_id": target_id,
            "dart_type": dart_type,
            "travel_time": self.dart_travel_time,
        }

    def process_catch(self, catcher_id: str, region: str) -> dict:
        """
        Called when the target player catches the dart in time.
        Returns a result payload to broadcast.
        """
        if not self.pending_throw or self.pending_throw["target_id"] != catcher_id:
            raise ValueError("No pending dart for this player.")

        thrower_id = self.pending_throw["thrower_id"]
        points = REGION_POINTS.get(region, settings.BOARD_OUTER_POINTS)

        self.players[catcher_id].add_score(points)
        eliminated = self.players[thrower_id].add_strike()

        result = self._build_result(
            event="dart_caught",
            thrower_id=thrower_id,
            catcher_id=catcher_id,
            region=region,
            points_awarded_to=catcher_id,
            points=points,
            thrower_eliminated=eliminated,
        )
        self.pending_throw = None
        self._check_round_end()
        return result

    def process_miss(self) -> dict:
        """
        Called when the target player fails to catch the dart (timer expired).
        """
        if not self.pending_throw:
            raise ValueError("No dart in flight.")

        thrower_id = self.pending_throw["thrower_id"]
        target_id = self.pending_throw["target_id"]

        self.players[thrower_id].add_score(MISS_BONUS_POINTS)
        eliminated = self.players[target_id].add_strike()

        result = self._build_result(
            event="dart_missed",
            thrower_id=thrower_id,
            catcher_id=target_id,
            region=None,
            points_awarded_to=thrower_id,
            points=MISS_BONUS_POINTS,
            catcher_eliminated=eliminated,
        )
        self.pending_throw = None
        self._check_round_end()
        return result

    def _build_result(self, **kwargs) -> dict:
        kwargs["scoreboard"] = [
            {"user_id": p.user_id, "profile_name": p.profile_name,
             "score": p.score, "strikes": p.strikes, "is_eliminated": p.is_eliminated}
            for p in self.players.values()
        ]
        return kwargs

    def _check_round_end(self):
        active = self.active_players()
        if len(active) <= 1:
            if self.current_round >= settings.GAME_ROUNDS:
                self.status = "finished"
                self._determine_winner()
            else:
                self.current_round += 1
                # Reset strikes for next round, keep scores
                for p in self.players.values():
                    p.strikes = 0
                    p.is_eliminated = False

    def _determine_winner(self):
        best = max(self.players.values(), key=lambda p: p.score)
        best.is_eliminated = False   # winner mark (reuse field as flag here)
