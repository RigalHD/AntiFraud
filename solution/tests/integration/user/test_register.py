from datetime import UTC, datetime

import pytest

from backend.application.exception.user import EmailAlreadyExistsError
from backend.application.forms.user import UserForm
from backend.domain.misc_types import Role
from backend.infrastructure.api.api_client import AntiFraudApiClient
from backend.infrastructure.auth.hasher import Hasher
from backend.infrastructure.auth.idp.token_processor import AccessTokenProcessor
from tests.utils.exception_validation import validate_exception, validate_validation_error
from tests.utils.misc_types import TestField


async def test_ok(
    api_client: AntiFraudApiClient,
    user_form: UserForm,
    hasher: Hasher,
    access_token_processor: AccessTokenProcessor,
) -> None:
    data = (await api_client.register(user_form)).expect_status(201).unwrap()

    access_token = data.access_token
    expires_in = data.expires_in
    user = data.user

    assert user.email == user_form.email
    assert hasher.verify(user_form.password, user.password)
    assert user.full_name == user_form.full_name
    assert user.region == user_form.region
    assert user.gender == user_form.gender
    assert user.marital_status == user_form.marital_status
    assert user.role == Role.USER
    assert user.is_active is True

    decoded_token = access_token_processor.decode(access_token)

    assert isinstance(decoded_token, dict)
    assert decoded_token["sub"] == str(user.id)
    assert decoded_token["exp"] == expires_in
    assert decoded_token["exp"] + decoded_token["iat"] >= int(datetime.now(tz=UTC).timestamp())
    assert decoded_token["role"] == Role.USER.value


async def test_twice(
    api_client: AntiFraudApiClient,
    user_form: UserForm,
) -> None:
    (await api_client.register(user_form)).expect_status(201).unwrap()

    error_data = (await api_client.register(user_form)).expect_status(409).err_unwrap()

    validate_exception(error_data, EmailAlreadyExistsError)


@pytest.mark.parametrize(
    ("email", "password"),
    [("1", TestField.USE_DEFAULT), ("a" * 255 + "@example.com", "a" * 73)],
)
async def test_validation_error(
    api_client: AntiFraudApiClient,
    user_form: UserForm,
    email: str,
    password: str | TestField,
) -> None:
    invalid_fields = {"email": email}
    user_form.email = email
    if isinstance(password, str):
        user_form.password = password
        invalid_fields["password"] = password

    error_data = (await api_client.register(user_form)).expect_status(422).err_unwrap()

    validate_validation_error(error_data, invalid_fields)
