"""
WebSocket endpoint: /ws/session/{session_id}?token=<jwt>

Each connected client is identified by their JWT user ID.
Events flow:
  Client → Server:
    throw_dart   { target_user_id, dart_type }
    catch_dart   { region: "inner"|"middle"|"outer" }
    miss_dart    {}           # sent by server's timer, or client fallback

  Server → Client (broadcast via Redis pub/sub):
    player_joined  { user_id, profile_name }
    player_left    { user_id }
    dart_thrown    { thrower_id, target_id, dart_type, travel_time }
    dart_caught    { ... scoreboard }
    dart_missed    { ... scoreboard }
    player_out     { user_id }
    round_end      { round, scoreboard }
    game_over      { winner_id, scoreboard }
    error          { detail }
"""
import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.core.security import decode_token
from app.redis.pub_sub import publish, subscribe
from app.services.game_engine import SessionState

router = APIRouter()
logger = logging.getLogger(__name__)

# In-process registry: session_id → {user_id: WebSocket}
_connections: dict[str, dict[str, WebSocket]] = {}


def _register(session_id: str, user_id: str, ws: WebSocket):
    _connections.setdefault(session_id, {})[user_id] = ws


def _unregister(session_id: str, user_id: str):
    _connections.get(session_id, {}).pop(user_id, None)


async def _send_to(session_id: str, user_id: str, event: str, payload: dict):
    ws = _connections.get(session_id, {}).get(user_id)
    if ws:
        try:
            await ws.send_text(json.dumps({"event": event, "payload": payload}))
        except Exception:
            pass


async def _broadcast(session_id: str, event: str, payload: dict):
    """Broadcast via Redis so all server instances receive it."""
    await publish(session_id, event, payload)


async def _listen_redis(session_id: str):
    """Forward Redis pub/sub messages to local WebSocket clients."""
    async for event, payload in subscribe(session_id):
        for user_id, ws in list(_connections.get(session_id, {}).items()):
            try:
                await ws.send_text(json.dumps({"event": event, "payload": payload}))
            except Exception:
                _unregister(session_id, user_id)


@router.websocket("/ws/session/{session_id}")
async def game_websocket(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(...),
):
    try:
        user_id = decode_token(token)
    except Exception:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await websocket.accept()
    _register(session_id, user_id, websocket)

    # Start Redis listener (once per session per process)
    if len(_connections.get(session_id, {})) == 1:
        asyncio.create_task(_listen_redis(session_id))

    state = await SessionState.load(session_id)
    if state and user_id in state.players:
        await _broadcast(session_id, "player_joined", {
            "user_id": user_id,
            "profile_name": state.players[user_id].profile_name,
        })

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            event = msg.get("event")
            payload = msg.get("payload", {})

            state = await SessionState.load(session_id)
            if not state:
                await _send_to(session_id, user_id, "error", {"detail": "Session not found."})
                continue

            if event == "throw_dart":
                try:
                    result = state.process_throw(
                        thrower_id=user_id,
                        target_id=payload["target_user_id"],
                        dart_type=payload.get("dart_type", "default"),
                    )
                    await state.save()
                    await _broadcast(session_id, "dart_thrown", result)

                    # Schedule automatic miss after travel_time + grace period
                    async def auto_miss(sid=session_id, uid=user_id, travel=state.dart_travel_time):
                        await asyncio.sleep(travel + 0.5)
                        s = await SessionState.load(sid)
                        if s and s.pending_throw and s.pending_throw["thrower_id"] == uid:
                            result = s.process_miss()
                            await s.save()
                            await _broadcast(sid, "dart_missed", result)
                            if s.status == "finished":
                                await _broadcast(sid, "game_over", result)

                    asyncio.create_task(auto_miss())

                except ValueError as e:
                    await _send_to(session_id, user_id, "error", {"detail": str(e)})

            elif event == "catch_dart":
                try:
                    result = state.process_catch(catcher_id=user_id, region=payload["region"])
                    await state.save()
                    await _broadcast(session_id, "dart_caught", result)
                    if state.status == "finished":
                        await _broadcast(session_id, "game_over", result)
                except ValueError as e:
                    await _send_to(session_id, user_id, "error", {"detail": str(e)})

    except WebSocketDisconnect:
        _unregister(session_id, user_id)
        await _broadcast(session_id, "player_left", {"user_id": user_id})
        logger.info("Player %s disconnected from session %s", user_id, session_id)
