from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "CanUDartMe"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://canudart:canudart@db:5432/canudartme"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Game rules
    MAX_PLAYERS_PER_GROUP: int = 6
    DART_TRAVEL_TIME_SECONDS: float = 2.0   # configurable per session (max 2s)
    STRIKES_TO_ELIMINATE: int = 3
    GAME_ROUNDS: int = 3

    # Dart board regions (points awarded to catcher)
    BOARD_INNER_POINTS: int = 30
    BOARD_MIDDLE_POINTS: int = 20
    BOARD_OUTER_POINTS: int = 10

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
