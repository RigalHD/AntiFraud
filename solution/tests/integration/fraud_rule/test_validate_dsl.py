import logging

from backend.application.exception.base import ForbiddenError, UnauthorizedError
from backend.application.forms.fraud_rule import DSLValidationForm
from backend.infrastructure.api.api_client import AntiFraudApiClient
from tests.utils.exception_validation import validate_exception
from tests.utils.misc_types import AuthorizedUser


async def test_ok_level_1(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    dsl_validation_form: DSLValidationForm,
) -> None:
    api_client.authorize(admin_user.access_token)
    dsl_validation_form.dsl_expression = "amount > 100"

    dsl_info = (await api_client.validate_dsl(dsl_validation_form)).expect_status(200).unwrap()

    assert dsl_info.is_valid is True
    assert dsl_info.normalized_expression == dsl_validation_form.dsl_expression
    assert len(dsl_info.errors) == 0


async def test_ok_level_1_normalization(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    dsl_validation_form: DSLValidationForm,
) -> None:
    api_client.authorize(admin_user.access_token)
    dsl_validation_form.dsl_expression = "amount>100"

    dsl_info = (await api_client.validate_dsl(dsl_validation_form)).expect_status(200).unwrap()

    assert dsl_info.is_valid is True
    assert dsl_info.normalized_expression == "amount > 100"
    assert len(dsl_info.errors) == 0


async def test_invalid_field(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    dsl_validation_form: DSLValidationForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    dsl_validation_form.dsl_expression = "AAAAAA > 100"
    dsl_info = (await api_client.validate_dsl(dsl_validation_form)).expect_status(200).unwrap()

    assert dsl_info.is_valid is False
    assert dsl_info.normalized_expression is None

    assert len(dsl_info.errors) == 1
    assert dsl_info.errors[0].position is None
    assert dsl_info.errors[0].near is None
    assert dsl_info.errors[0].code == "DSL_INVALID_FIELD"


async def test_parse_error(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    dsl_validation_form: DSLValidationForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    dsl_validation_form.dsl_expression = "amount > AND user.age < 21"
    dsl_info = (await api_client.validate_dsl(dsl_validation_form)).expect_status(200).unwrap()

    logging.critical(dsl_info)
    assert dsl_info.is_valid is False
    assert dsl_info.normalized_expression is None

    assert len(dsl_info.errors) == 1
    assert dsl_info.errors[0].position == 9
    assert dsl_info.errors[0].near is not None
    assert dsl_info.errors[0].code == "DSL_PARSE_ERROR"


async def test_invalid_operator(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    dsl_validation_form: DSLValidationForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    dsl_validation_form.dsl_expression = "currency > 1"
    dsl_info = (await api_client.validate_dsl(dsl_validation_form)).expect_status(200).unwrap()

    logging.critical(dsl_info)
    assert dsl_info.is_valid is False
    assert dsl_info.normalized_expression is None

    assert len(dsl_info.errors) == 1
    assert dsl_info.errors[0].position is None
    assert dsl_info.errors[0].near is None
    assert dsl_info.errors[0].code == "DSL_INVALID_OPERATOR"

    dsl_validation_form.dsl_expression = "amount < 'RUB'"
    dsl_info = (await api_client.validate_dsl(dsl_validation_form)).expect_status(200).unwrap()

    logging.critical(dsl_info)
    assert dsl_info.is_valid is False
    assert dsl_info.normalized_expression is None

    assert len(dsl_info.errors) == 1
    assert dsl_info.errors[0].position is None
    assert dsl_info.errors[0].near is None
    assert dsl_info.errors[0].code == "DSL_INVALID_OPERATOR"


async def test_ok_level_3(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    dsl_validation_form: DSLValidationForm,
) -> None:
    api_client.authorize(admin_user.access_token)
    dsl_validation_form.dsl_expression = "amount > 100 AND currency = 'RUB'"

    dsl_info = (await api_client.validate_dsl(dsl_validation_form)).expect_status(200).unwrap()

    assert dsl_info.is_valid is True
    assert dsl_info.normalized_expression == dsl_validation_form.dsl_expression
    assert len(dsl_info.errors) == 0


async def test_ok_level_3_normalization(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    dsl_validation_form: DSLValidationForm,
) -> None:
    api_client.authorize(admin_user.access_token)
    dsl_validation_form.dsl_expression = "amount> 100 aNd currency ='RUB'"

    dsl_info = (await api_client.validate_dsl(dsl_validation_form)).expect_status(200).unwrap()

    assert dsl_info.is_valid is True
    assert dsl_info.normalized_expression == "amount > 100 AND currency = 'RUB'"
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
