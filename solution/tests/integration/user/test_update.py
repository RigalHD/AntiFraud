from uuid import uuid4

from backend.application.exception.base import ForbiddenError, UnauthorizedError
from backend.application.exception.user import UserDoesNotExistError
from backend.application.forms.user import UpdateUserForm
from backend.infrastructure.api.api_client import AntiFraudApiClient
from tests.utils.exception_validation import validate_exception
from tests.utils.misc_types import AuthorizedUser


async def test_ok_me(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    update_user_form: UpdateUserForm,
) -> None:
    api_client.authorize(authorized_user.access_token)

    updated_user = (await api_client.update_user(update_user_form)).expect_status(200).unwrap()

    assert updated_user.full_name == update_user_form.full_name
    assert updated_user.age == update_user_form.age
    assert updated_user.region == update_user_form.region
    assert updated_user.gender == update_user_form.gender
    assert updated_user.marital_status == update_user_form.marital_status


async def test_ok_by_id(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    admin_user: AuthorizedUser,
    update_user_form: UpdateUserForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    old_user = authorized_user.user
    updated_user = (await api_client.update_user_by_id(old_user.id, update_user_form)).expect_status(200).unwrap()

    assert updated_user.full_name == update_user_form.full_name
    assert updated_user.age == update_user_form.age
    assert updated_user.region == update_user_form.region
    assert updated_user.gender == update_user_form.gender
    assert updated_user.marital_status == update_user_form.marital_status


async def test_no_auth_me(api_client: AntiFraudApiClient, update_user_form: UpdateUserForm) -> None:
    error_data = (await api_client.update_user(update_user_form)).expect_status(401).err_unwrap()

    validate_exception(error_data, UnauthorizedError)


async def test_no_auth_by_id(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    update_user_form: UpdateUserForm,
) -> None:
    error_data = (
        (await api_client.update_user_by_id(authorized_user.user.id, update_user_form)).expect_status(401).err_unwrap()
    )

    validate_exception(error_data, UnauthorizedError)


async def test_forbidden_by_id(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    another_authorized_user: AuthorizedUser,
    update_user_form: UpdateUserForm,
) -> None:
    api_client.authorize(authorized_user.access_token)

    error_data = (
        (await api_client.update_user_by_id(another_authorized_user.user.id, update_user_form))
        .expect_status(403)
        .err_unwrap()
    )

    validate_exception(error_data, ForbiddenError)


async def test_not_found(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    update_user_form: UpdateUserForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    error_data = (await api_client.update_user_by_id(uuid4(), update_user_form)).expect_status(404).err_unwrap()

    validate_exception(error_data, UserDoesNotExistError)
