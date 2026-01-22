from uuid import uuid4

from backend.application.exception.base import ForbiddenError, UnauthorizedError
from backend.application.exception.user import UserDoesNotExistError
from backend.infrastructure.api.api_client import AntiFraudApiClient
from tests.utils.exception_validation import validate_exception
from tests.utils.misc_types import AuthorizedUser


async def test_ok_me(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
) -> None:
    api_client.authorize(authorized_user.access_token)

    read_user = (await api_client.read_user()).expect_status(200).unwrap()

    assert authorized_user.user == read_user


async def test_ok_me_no_auth(api_client: AntiFraudApiClient) -> None:
    error_data = (await api_client.read_user()).expect_status(401).err_unwrap()

    validate_exception(error_data, UnauthorizedError)


async def test_ok_by_id(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    admin_user: AuthorizedUser,
) -> None:
    user = authorized_user.user
    api_client.authorize(admin_user.access_token)

    read_user = (await api_client.read_user_by_id(user.id)).expect_status(200).unwrap()

    assert read_user == user


async def test_ok_user_himself_by_id(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
) -> None:
    api_client.authorize(authorized_user.access_token)

    user = authorized_user.user

    read_user = (await api_client.read_user_by_id(user.id)).expect_status(200).unwrap()

    assert user == read_user


async def test_forbidden_by_id(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    another_authorized_user: AuthorizedUser,
) -> None:
    api_client.authorize(authorized_user.access_token)

    error_data = (await api_client.read_user_by_id(another_authorized_user.user.id)).expect_status(403).err_unwrap()

    validate_exception(error_data, ForbiddenError)


async def test_no_auth_by_id(api_client: AntiFraudApiClient, another_authorized_user: AuthorizedUser) -> None:
    error_data = (await api_client.read_user_by_id(another_authorized_user.user.id)).expect_status(401).err_unwrap()

    validate_exception(error_data, UnauthorizedError)


async def test_not_found_by_id(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
) -> None:
    api_client.authorize(admin_user.access_token)

    error_data = (await api_client.read_user_by_id(uuid4())).expect_status(404).err_unwrap()

    validate_exception(error_data, UserDoesNotExistError)
