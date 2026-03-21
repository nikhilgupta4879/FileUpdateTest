from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.database import init_db
from app.redis.connection import close_redis
from app.api.v1 import auth, users, groups, sessions
from app.api import websocket

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(groups.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")

# WebSocket
app.include_router(websocket.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}
