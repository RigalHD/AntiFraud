import os
from collections.abc import AsyncIterable, AsyncIterator

import aiohttp
import pytest
from aiohttp import ClientSession
from dishka import AsyncContainer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.bootstrap.di.container import get_async_container
from backend.infrastructure.api.api_client import AntiFraudApiClient


@pytest.fixture
async def async_container() -> AsyncIterator[AsyncContainer]:
    async_container = get_async_container()
    yield async_container
    await async_container.close()


@pytest.fixture
async def session(async_container: AsyncContainer) -> AsyncIterator[AsyncSession]:
    async with async_container() as r:
        yield (await r.get(AsyncSession))


@pytest.fixture(autouse=True)
async def gracefully_teardown(
    session: AsyncSession,
) -> AsyncIterable[None]:
    yield
    await session.execute(
        text("""
            DO $$
            DECLARE
                tb text;
            BEGIN
                FOR tb IN (
                    SELECT tablename
                    FROM pg_catalog.pg_tables
                    WHERE schemaname = 'public'
                      AND tablename != 'alembic_version'
                )
                LOOP
                    EXECUTE 'TRUNCATE TABLE ' || tb || ' CASCADE';
                END LOOP;
            END $$;
        """),
    )
    await session.commit()


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ["API_URL"]


@pytest.fixture
async def http_session(base_url: str) -> AsyncIterator[ClientSession]:
    async with aiohttp.ClientSession(base_url=base_url) as session:
        yield session


@pytest.fixture
def api_client(base_url: str, http_session: ClientSession) -> AntiFraudApiClient:
    return AntiFraudApiClient(base_url=base_url, session=http_session)
