from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.infrastructure.config_loader import DataBaseConfig


async def get_async_engine(
    db_config: DataBaseConfig,
) -> AsyncGenerator[AsyncEngine]:
    sqlalchemy_url = db_config.build_connection_str()
    async_engine = create_async_engine(url=sqlalchemy_url, echo=db_config.debug, pool_pre_ping=True, future=True)

    yield async_engine

    await async_engine.dispose()


def get_async_sessionmaker(
    async_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)


async def get_async_session(
    async_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
