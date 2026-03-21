"""
Unit tests for the game engine (no I/O — pure logic).
Run: pytest backend/tests/
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.services.game_engine import SessionState, PlayerState, MISS_BONUS_POINTS


def _make_state(n_players: int = 3) -> SessionState:
    players = {
        f"user_{i}": PlayerState(user_id=f"user_{i}", profile_name=f"Player{i}")
        for i in range(n_players)
    }
    with patch.object(SessionState, "save", new_callable=AsyncMock):
        state = SessionState(
            session_id="test-session",
            group_id="test-group",
            dart_travel_time=2.0,
            players=players,
            status="active",
        )
    return state


def test_throw_dart_sets_pending():
    state = _make_state()
    result = state.process_throw("user_0", "user_1", "classic")
    assert state.pending_throw["thrower_id"] == "user_0"
    assert state.pending_throw["target_id"] == "user_1"
    assert result["travel_time"] == 2.0


def test_catch_dart_awards_points_and_strike():
    state = _make_state()
    state.process_throw("user_0", "user_1", "classic")
    result = state.process_catch("user_1", "inner")
    assert state.players["user_1"].score == 30          # inner region
    assert state.players["user_0"].strikes == 1         # thrower gets strike
    assert state.pending_throw is None
    assert result["event"] == "dart_caught"


def test_miss_dart_awards_thrower_and_strikes_target():
    state = _make_state()
    state.process_throw("user_0", "user_1", "classic")
    result = state.process_miss()
    assert state.players["user_0"].score == MISS_BONUS_POINTS
    assert state.players["user_1"].strikes == 1
    assert result["event"] == "dart_missed"


def test_three_strikes_eliminates_player():
    state = _make_state()
    for _ in range(3):
        state.process_throw("user_0", "user_1", "classic")
        state.process_miss()
    assert state.players["user_1"].is_eliminated


def test_duplicate_throw_raises():
    state = _make_state()
    state.process_throw("user_0", "user_1", "classic")
    with pytest.raises(ValueError, match="in flight"):
        state.process_throw("user_0", "user_2", "classic")
