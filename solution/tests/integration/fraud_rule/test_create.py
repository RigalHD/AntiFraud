from backend.application.exception.base import ForbiddenError, UnauthorizedError
from backend.application.exception.fraud_rule import FraudRuleNameAlreadyExistsError
from backend.application.forms.fraud_rule import FraudRuleForm
from backend.domain.entity.fraud_rule import FraudRule
from backend.infrastructure.api.api_client import AntiFraudApiClient
from tests.utils.exception_validation import validate_exception
from tests.utils.misc_types import AuthorizedUser


async def test_ok(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    fraud_rule_form: FraudRuleForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    created_rule = (await api_client.create_fraud_rule(fraud_rule_form)).expect_status(201).unwrap()

    assert created_rule.name == fraud_rule_form.name
    assert created_rule.description == fraud_rule_form.description
    assert created_rule.dsl_expression == fraud_rule_form.dsl_expression
    assert created_rule.priority == fraud_rule_form.priority
    assert created_rule.enabled == fraud_rule_form.enabled


async def test_duplicate_name(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    fraud_rule: FraudRule,
    fraud_rule_form: FraudRuleForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    fraud_rule_form.description = "Second rule"
    error_data = (await api_client.create_fraud_rule(fraud_rule_form)).expect_status(409).err_unwrap()

    validate_exception(error_data, FraudRuleNameAlreadyExistsError)


async def test_no_auth(api_client: AntiFraudApiClient, fraud_rule_form: FraudRuleForm) -> None:
    error_data = (await api_client.create_fraud_rule(fraud_rule_form)).expect_status(401).err_unwrap()

    validate_exception(error_data, UnauthorizedError)


async def test_forbidden(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    fraud_rule_form: FraudRuleForm,
) -> None:
    api_client.authorize(authorized_user.access_token)

    error_data = (await api_client.create_fraud_rule(fraud_rule_form)).expect_status(403).err_unwrap()

    validate_exception(error_data, ForbiddenError)
