from uuid import uuid4

from backend.application.exception.base import ForbiddenError, UnauthorizedError
from backend.application.exception.fraud_rule import (
    FraudRuleDoesNotExistError,
    FraudRuleNameAlreadyExistsError,
)
from backend.application.forms.fraud_rule import FraudRuleForm, UpdateFraudRuleForm
from backend.domain.entity.fraud_rule import FraudRule
from backend.infrastructure.api.api_client import AntiFraudApiClient
from tests.utils.exception_validation import validate_exception
from tests.utils.misc_types import AuthorizedUser


async def test_ok(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    fraud_rule: FraudRule,
    update_fraud_rule_form: UpdateFraudRuleForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    updated_rule = (
        (await api_client.update_fraud_rule(fraud_rule.id, update_fraud_rule_form))
        .expect_status(200)
        .unwrap()
    )

    assert updated_rule.name == update_fraud_rule_form.name
    assert updated_rule.description == update_fraud_rule_form.description
    assert updated_rule.dsl_expression == update_fraud_rule_form.dsl_expression
    assert updated_rule.priority == update_fraud_rule_form.priority
    assert updated_rule.enabled == update_fraud_rule_form.enabled


async def test_used_name(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    fraud_rule: FraudRule,
    fraud_rule_form: FraudRuleForm,
    update_fraud_rule_form: UpdateFraudRuleForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    fraud_rule_form.name = "nameeeeeee"
    (await api_client.create_fraud_rule(fraud_rule_form)).expect_status(201)

    update_fraud_rule_form.name = fraud_rule_form.name
    error_data = (
        (await api_client.update_fraud_rule(fraud_rule.id, update_fraud_rule_form))
        .expect_status(409)
        .err_unwrap()
    )

    validate_exception(error_data, FraudRuleNameAlreadyExistsError)


async def test_ok_with_the_same_name(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    fraud_rule: FraudRule,
    update_fraud_rule_form: UpdateFraudRuleForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    update_fraud_rule_form.name = fraud_rule.name
    updated_rule = (
        (await api_client.update_fraud_rule(fraud_rule.id, update_fraud_rule_form))
        .expect_status(200)
        .unwrap()
    )

    assert updated_rule.name == update_fraud_rule_form.name
    assert updated_rule.description == update_fraud_rule_form.description
    assert updated_rule.dsl_expression == update_fraud_rule_form.dsl_expression
    assert updated_rule.priority == update_fraud_rule_form.priority
    assert updated_rule.enabled == update_fraud_rule_form.enabled


async def test_no_auth(
    api_client: AntiFraudApiClient,
    fraud_rule: FraudRule,
    update_fraud_rule_form: UpdateFraudRuleForm,
) -> None:
    error_data = (
        (await api_client.update_fraud_rule(fraud_rule.id, update_fraud_rule_form))
        .expect_status(401)
        .err_unwrap()
    )

    validate_exception(error_data, UnauthorizedError)


async def test_forbidden(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    fraud_rule: FraudRule,
    update_fraud_rule_form: UpdateFraudRuleForm,
) -> None:
    api_client.authorize(authorized_user.access_token)

    error_data = (
        (await api_client.update_fraud_rule(fraud_rule.id, update_fraud_rule_form))
        .expect_status(403)
        .err_unwrap()
    )

    validate_exception(error_data, ForbiddenError)


async def test_not_found(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    update_fraud_rule_form: UpdateFraudRuleForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    error_data = (
        (await api_client.update_fraud_rule(uuid4(), update_fraud_rule_form)).expect_status(404).err_unwrap()
    )

    validate_exception(error_data, FraudRuleDoesNotExistError)
