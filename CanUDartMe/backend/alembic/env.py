import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.core.config import get_settings
from app.core.database import Base
from app.models import user, group, game_session, score  # noqa: F401

settings = get_settings()
config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_online():
    engine = create_async_engine(settings.DATABASE_URL)

    async def _run():
        async with engine.connect() as conn:
            await conn.run_sync(
                lambda sync_conn: context.configure(connection=sync_conn, target_metadata=target_metadata)
            )
            async with conn.begin():
                await conn.run_sync(lambda _: context.run_migrations())

    asyncio.run(_run())


run_migrations_online()
