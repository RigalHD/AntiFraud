import os
from collections.abc import AsyncIterable, AsyncIterator

import aiohttp
import pytest
from aiohttp import ClientSession
from dishka import AsyncContainer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.forms.user import UserForm
from backend.bootstrap.di.container import get_async_container
from backend.domain.misc_types import Gender, MaritalStatus
from backend.infrastructure.api.api_client import AntiFraudApiClient
from backend.infrastructure.auth.hasher import Hasher
from backend.infrastructure.auth.idp.token_processor import AccessTokenProcessor
from backend.infrastructure.auth.login import WebLoginForm
from tests.utils.misc_types import AuthorizedUser


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


@pytest.fixture
async def hasher(async_container: AsyncContainer) -> AsyncIterator[Hasher]:
    async with async_container() as r:
        yield (await r.get(Hasher))


@pytest.fixture
async def access_token_processor(async_container: AsyncContainer) -> AsyncIterator[AccessTokenProcessor]:
    async with async_container() as r:
        yield (await r.get(AccessTokenProcessor))


@pytest.fixture
def user_form() -> UserForm:
    form = UserForm(
        email="user@example.com",
        password="Qwerty_123!!!",
        fullName="Ivan Ivanov",
        region="RU-MOW",
        gender=Gender.MALE,
        maritalStatus=MaritalStatus.SINGLE,
    )
    return form


@pytest.fixture
def login_form() -> WebLoginForm:
    form = WebLoginForm(
        email="user@example.com",
        password="Qwerty_123!!!",
    )
    return form


@pytest.fixture
async def authorized_user(
    api_client: AntiFraudApiClient,
    user_form: UserForm,
) -> AuthorizedUser:
    return (await api_client.register(user_form)).expect_status(201).unwrap()
