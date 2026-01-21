from aiohttp import ClientSession
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession


async def test_ok(http_session: ClientSession, session: AsyncSession, async_container: AsyncContainer) -> None:
    assert 1 == 1
    assert http_session
    assert session
    assert async_container
