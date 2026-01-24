from uuid import uuid4

from backend.application.exception.base import ForbiddenError, UnauthorizedError
from backend.application.exception.user import UserDoesNotExistError
from backend.infrastructure.api.api_client import AntiFraudApiClient
from tests.utils.exception_validation import validate_exception
from tests.utils.misc_types import AuthorizedUser


async def test_ok(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    authorized_user: AuthorizedUser,
) -> None:
    api_client.authorize(admin_user.access_token)

    (await api_client.delete_user(authorized_user.user.id)).expect_status(204)


async def test_no_auth(api_client: AntiFraudApiClient, authorized_user: AuthorizedUser) -> None:
    error_data = (await api_client.delete_user(authorized_user.user.id)).expect_status(401).err_unwrap()

    validate_exception(error_data, UnauthorizedError)


async def test_forbidden(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    another_authorized_user: AuthorizedUser,
) -> None:
    api_client.authorize(authorized_user.access_token)

    error_data = (
        (await api_client.delete_user(another_authorized_user.user.id)).expect_status(403).err_unwrap()
    )

    validate_exception(error_data, ForbiddenError)


async def test_not_found(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
) -> None:
    api_client.authorize(admin_user.access_token)

    error_data = (await api_client.delete_user(uuid4())).expect_status(404).err_unwrap()

    validate_exception(error_data, UserDoesNotExistError)
