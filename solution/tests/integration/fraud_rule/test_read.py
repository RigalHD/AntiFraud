from uuid import uuid4

from backend.application.exception.base import ForbiddenError, UnauthorizedError
from backend.application.exception.fraud_rule import FraudRuleDoesNotExistError
from backend.domain.entity.fraud_rule import FraudRule
from backend.infrastructure.api.api_client import AntiFraudApiClient
from tests.utils.exception_validation import validate_exception
from tests.utils.misc_types import AuthorizedUser


async def test_ok(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    fraud_rule: FraudRule,
) -> None:
    api_client.authorize(admin_user.access_token)

    read_rule = (await api_client.read_fraud_rule(fraud_rule.id)).expect_status(200).unwrap()

    assert read_rule == fraud_rule


async def test_no_auth(api_client: AntiFraudApiClient, fraud_rule: FraudRule) -> None:
    error_data = (await api_client.read_fraud_rule(fraud_rule.id)).expect_status(401).err_unwrap()

    validate_exception(error_data, UnauthorizedError)


async def test_forbidden(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    fraud_rule: FraudRule,
) -> None:
    api_client.authorize(authorized_user.access_token)

    error_data = (await api_client.read_fraud_rule(fraud_rule.id)).expect_status(403).err_unwrap()

    validate_exception(error_data, ForbiddenError)


async def test_not_found(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
) -> None:
    api_client.authorize(admin_user.access_token)

    error_data = (await api_client.read_fraud_rule(uuid4())).expect_status(404).err_unwrap()

    validate_exception(error_data, FraudRuleDoesNotExistError)
