"""
Redis Pub/Sub helpers for broadcasting game events across server instances.
Each game session has its own channel: game_session:<session_id>
"""
import json
from app.redis.connection import get_redis


SESSION_CHANNEL_PREFIX = "game_session:"


def session_channel(session_id: str) -> str:
    return f"{SESSION_CHANNEL_PREFIX}{session_id}"


async def publish(session_id: str, event: str, payload: dict):
    redis = await get_redis()
    message = json.dumps({"event": event, "payload": payload})
    await redis.publish(session_channel(session_id), message)


async def subscribe(session_id: str):
    """Returns an async generator of (event, payload) tuples."""
    redis = await get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(session_channel(session_id))
    async for raw in pubsub.listen():
        if raw["type"] == "message":
            data = json.loads(raw["data"])
            yield data["event"], data["payload"]
