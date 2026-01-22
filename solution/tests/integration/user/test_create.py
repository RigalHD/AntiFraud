from backend.application.exception.base import ForbiddenError, UnauthorizedError
from backend.application.forms.user import AdminUserForm
from backend.infrastructure.api.api_client import AntiFraudApiClient
from tests.utils.exception_validation import validate_exception
from tests.utils.misc_types import AuthorizedUser


async def test_ok(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    admin_user_form: AdminUserForm,
) -> None:
    form = admin_user_form
    api_client.authorize(admin_user.access_token)

    user = (await api_client.create_user(form)).expect_status(201).unwrap()
    assert user.email == form.email
    assert user.full_name == form.full_name
    assert user.age == form.age
    assert user.region == form.region
    assert user.gender == form.gender
    assert user.marital_status == form.marital_status
    assert user.role == form.role
    assert user.is_active is True


async def test_no_auth(api_client: AntiFraudApiClient, admin_user_form: AdminUserForm) -> None:
    error_data = (await api_client.create_user(admin_user_form)).expect_status(401).err_unwrap()

    validate_exception(error_data, UnauthorizedError)


async def test_forbidden(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    admin_user_form: AdminUserForm,
) -> None:
    api_client.authorize(authorized_user.access_token)

    error_data = (await api_client.create_user(admin_user_form)).expect_status(403).err_unwrap()

    validate_exception(error_data, ForbiddenError)
