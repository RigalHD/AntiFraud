import os
from collections.abc import AsyncIterable, AsyncIterator

import aiohttp
import pytest
from aiohttp import ClientSession
from dishka import AsyncContainer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.forms.fraud_rule import FraudRuleForm, UpdateFraudRuleForm
from backend.application.forms.user import AdminUserForm, UpdateUserForm, UserForm
from backend.bootstrap.di.container import get_async_container
from backend.domain.entity.fraud_rule import FraudRule
from backend.domain.misc_types import Gender, MaritalStatus, Role
from backend.infrastructure.api.api_client import AntiFraudApiClient
from backend.infrastructure.auth.hasher import Hasher
from backend.infrastructure.auth.idp.token_processor import AccessTokenProcessor
from backend.infrastructure.auth.login import WebLoginForm
from backend.infrastructure.config_loader import Config
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


@pytest.fixture
async def config(async_container: AsyncContainer) -> AsyncIterator[Config]:
    async with async_container() as r:
        yield (await r.get(Config))


@pytest.fixture(autouse=True)
async def gracefully_teardown(session: AsyncSession, config: Config) -> AsyncIterable[None]:
    yield
    await session.execute(
        text(f"""
            DO $$
            DECLARE
                tb text;
                mail text := '{config.admin.admin_email}';
            BEGIN
                FOR tb IN (
                    SELECT tablename
                    FROM pg_catalog.pg_tables
                    WHERE schemaname = 'public'
                    AND tablename != 'alembic_version'
                    AND tablename != 'user_table'
                )
                LOOP
                    EXECUTE 'TRUNCATE TABLE ' || quote_ident(tb) || ' CASCADE';
                END LOOP;

                EXECUTE 'DELETE FROM user_table WHERE email != $1' USING mail;
            END $$;
        """),  # noqa: S608
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


@pytest.fixture
async def admin_user(
    api_client: AntiFraudApiClient,
    login_form: WebLoginForm,
    config: Config,
) -> AuthorizedUser:
    login_form.email = config.admin.admin_email
    login_form.password = config.admin.admin_password

    return (await api_client.login(login_form)).expect_status(200).unwrap()


@pytest.fixture
async def another_authorized_user(
    api_client: AntiFraudApiClient,
    user_form: UserForm,
) -> AuthorizedUser:
    user_form.email = "uuuuuuu@example.com"
    return (await api_client.register(user_form)).expect_status(201).unwrap()


@pytest.fixture
def update_user_form() -> UpdateUserForm:
    form = UpdateUserForm(
        fullName="IvanU IvanovU",
        age=30,
        region="RU-SPB",
        gender=None,
        maritalStatus=MaritalStatus.SINGLE,
    )
    return form


@pytest.fixture
def fraud_rule_form() -> FraudRuleForm:
    form = FraudRuleForm(
        name="Test Fraud Rule",
        description="A test rule for fraud detection",
        dslExpression="amount > 10",
        priority=1,
        enabled=True,
    )
    return form


@pytest.fixture
def update_fraud_rule_form() -> UpdateFraudRuleForm:
    form = UpdateFraudRuleForm(
        name="Updated Fraud Rule",
        description="Updated description",
        dslExpression="amount < 10",
        priority=2,
        enabled=False,
    )
    return form


@pytest.fixture
def admin_user_form() -> AdminUserForm:
    form = AdminUserForm(
        email="newuser@example.com",
        password="Qwerty_123!!!",
        fullName="New User",
        age=25,
        region="RU-MOW",
        gender=Gender.MALE,
        maritalStatus=MaritalStatus.SINGLE,
        role=Role.ADMIN,
    )

    return form


@pytest.fixture
async def fraud_rule(
    fraud_rule_form: FraudRuleForm,
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
) -> FraudRule:
    api_client.authorize(admin_user.access_token)

    fraud_rule = (await api_client.create_fraud_rule(fraud_rule_form)).expect_status(201).unwrap()

    api_client.reset_authorization()

    return fraud_rule
