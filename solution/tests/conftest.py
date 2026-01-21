from collections.abc import AsyncIterator

import aiohttp
import pytest
from aiohttp import ClientSession
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.bootstrap.di.container import get_async_container


@pytest.fixture
async def async_container() -> AsyncIterator[AsyncContainer]:
    async_container = get_async_container()
    yield async_container
    await async_container.close()


@pytest.fixture
async def session(async_container: AsyncContainer) -> AsyncIterator[AsyncSession]:
    async with async_container() as r:
        yield (await r.get(AsyncSession))


@pytest.fixture(scope="session")
def base_url() -> str:
    return "http://127.0.0.1:8080/api/v1/"


@pytest.fixture
async def http_session(base_url: str) -> AsyncIterator[ClientSession]:
    async with aiohttp.ClientSession(base_url=base_url) as session:
        yield session
