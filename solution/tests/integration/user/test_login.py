# from datetime import UTC, datetime
# from backend.application.exception.user import EmailAlreadyExistsError
# from backend.application.forms.user import UserForm
# from backend.domain.misc_types import Role
# from backend.infrastructure.api.api_client import AntiFraudApiClient
# from backend.infrastructure.auth.hasher import Hasher
# from backend.infrastructure.auth.idp.token_processor import AccessTokenProcessor
# from backend.infrastructure.auth.login import WebLoginForm

# from tests.utils.exception_validation import validate_exception


# async def test_ok(
#     api_client: AntiFraudApiClient,
#     user_form: UserForm,
#     login_form: WebLoginForm,
#     hasher: Hasher,
#     access_token_processor: AccessTokenProcessor,
# ) -> None:
#     register_resp = await api_client.register(user_form)

#     assert register_resp.http_response.status == 201
#     assert register_resp.data is not None
#     assert register_resp.error_data is None

#     login_resp = await api_client.login(login_form)

#     assert login_resp.http_response.status == 200
#     assert login_resp.data is not None
#     assert login_resp.error_data is None

#     access_token = login_resp.data.access_token
#     expires_in = login_resp.data.expires_in
#     user = login_resp.data.user

#     assert user.email == user_form.email
#     assert hasher.verify(user_form.password, user.password)
#     assert user.full_name == user_form.full_name
#     assert user.region == user_form.region
#     assert user.gender == user_form.gender
#     assert user.marital_status == user_form.marital_status
#     assert user.role == Role.USER
#     assert user.is_active == True

#     decoded_token = access_token_processor.decode(access_token)

#     assert isinstance(decoded_token, dict)
#     assert decoded_token["sub"] == str(user.id)
#     assert decoded_token["exp"] == expires_in
#     assert decoded_token["exp"] + decoded_token["iat"] >= int(datetime.now(tz=UTC).timestamp())
#     assert decoded_token["role"] == Role.USER.value

#     assert register_resp.data.access_token == login_resp.data.access_token


# async def test_invalid_password(
#     api_client: AntiFraudApiClient,
#     user_form: UserForm,
# ) -> None:
#     resp = await api_client.register(user_form)

#     assert resp.http_response.status == 201
#     assert resp.data is not None
#     assert resp.error_data is None

#     resp = await api_client.register(user_form)

#     assert resp.http_response.status == 409
#     assert resp.data is None
#     assert resp.error_data is not None

#     validate_exception(resp, EmailAlreadyExistsError)


# !!! ДОБАВИТЬ ЮЗЕРА В ФИКСТУРЫ И ИСПОЛЬЗОВАТЬ .unwrap()
