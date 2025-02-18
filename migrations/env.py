import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from app.database import DATABASE_URL
from app.models.base import Base
from app.models.follow import Follow
from app.models.like import Like
from app.models.media import Media
from app.models.tweet import Tweet
from app.models.user import User

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

connectable = create_async_engine(DATABASE_URL, echo=True, future=True)


def do_run_migrations(connection: AsyncConnection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    context.configure(url=DATABASE_URL, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
else:
    asyncio.run(run_migrations_online())


__all__ = ["Follow", "Like", "Media", "Tweet", "User"]
