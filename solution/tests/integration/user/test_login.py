from datetime import UTC, datetime

from pydantic import ValidationError
import pytest

from tests.utils.exception_validation import validate_exception, validate_validation_error
from tests.utils.misc_types import AuthorizedUser, TestField

from backend.infrastructure.api.api_client import AntiFraudApiClient
from backend.infrastructure.auth.hasher import Hasher
from backend.infrastructure.auth.idp.token_processor import AccessTokenProcessor
from backend.infrastructure.auth.login import WebLoginForm
from backend.infrastructure.auth.exception import UnauthorizedError


async def test_ok(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    login_form: WebLoginForm,
    access_token_processor: AccessTokenProcessor,
) -> None:
    data = (await api_client.login(login_form)).expect_status(200).unwrap()

    user = authorized_user.user
    
    access_token = data.access_token
    expires_in = data.expires_in
    resp_user = data.user

    assert resp_user.email == user.email
    assert resp_user.password == user.password
    assert resp_user.full_name == user.full_name
    assert resp_user.region == user.region
    assert resp_user.gender == user.gender
    assert resp_user.marital_status == user.marital_status
    assert resp_user.role == user.role
    assert resp_user.is_active is True

    decoded_token = access_token_processor.decode(access_token)

    assert isinstance(decoded_token, dict)
    assert decoded_token["sub"] == str(resp_user.id)
    assert decoded_token["exp"] == expires_in
    assert decoded_token["exp"] + decoded_token["iat"] >= int(datetime.now(tz=UTC).timestamp())
    assert decoded_token["role"] == user.role.value

    assert data.access_token == authorized_user.access_token


@pytest.mark.parametrize(
    ("email", "password"),
    [
        (TestField.USE_DEFAULT, TestField.CHANGE_IN_TEST),
        (TestField.CHANGE_IN_TEST, TestField.USE_DEFAULT),
        (TestField.CHANGE_IN_TEST, TestField.CHANGE_IN_TEST),
    ],
)
async def test_invalid_auth_data(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,  # не трогать. Это нужно, чтобы автоматически зарегало пользователя
    login_form: WebLoginForm,
    email: TestField,
    password: TestField,
) -> None:
    if email == TestField.CHANGE_IN_TEST:
        login_form.email = "a" + login_form.email 
    if password == TestField.CHANGE_IN_TEST:
        login_form.password += "a"
        
    error_data = (await api_client.login(login_form)).expect_status(401).err_unwrap()
    validate_exception(error_data, UnauthorizedError)
    
    
@pytest.mark.parametrize(
    ("email", "password"),
    [("1", TestField.USE_DEFAULT), ("a" * 255 + "@example.com", "a" * 73)],
)
async def test_validation_error(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    login_form: WebLoginForm,
    email: str,
    password: str | TestField,
) -> None:
    invalid_fields = {"email": email}
    login_form.email = email
    if isinstance(password, str):
        login_form.password = password
        invalid_fields["password"] = password

    error_data = (await api_client.login(login_form)).expect_status(422).err_unwrap()

    validate_validation_error(error_data, ValidationError, invalid_fields)
