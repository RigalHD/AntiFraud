from backend.application.exception.base import ForbiddenError, UnauthorizedError
from backend.application.forms.fraud_rule import DSLValidationForm
from backend.infrastructure.api.api_client import AntiFraudApiClient
from tests.utils.exception_validation import validate_exception
from tests.utils.misc_types import AuthorizedUser


async def test_ok_for_0_support_level(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    dsl_validation_form: DSLValidationForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    dsl_info = (await api_client.validate_dsl(dsl_validation_form)).expect_status(200).unwrap()

    assert dsl_info.is_valid is False
    assert dsl_info.normalized_expression != dsl_validation_form.dsl_expression
    assert len(dsl_info.errors) == 0


async def test_no_auth(
    api_client: AntiFraudApiClient,
    dsl_validation_form: DSLValidationForm,
) -> None:
    error_data = (await api_client.validate_dsl(dsl_validation_form)).expect_status(401).err_unwrap()

    validate_exception(error_data, UnauthorizedError)


async def test_forbidden(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    dsl_validation_form: DSLValidationForm,
) -> None:
    api_client.authorize(authorized_user.access_token)

    error_data = (await api_client.validate_dsl(dsl_validation_form)).expect_status(403).err_unwrap()

    validate_exception(error_data, ForbiddenError)
