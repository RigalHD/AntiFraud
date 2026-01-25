import asyncio
import logging
from decimal import Decimal
from uuid import uuid4

from backend.application.exception.base import UnauthorizedError
from backend.application.exception.user import UserDoesNotExistError
from backend.application.forms.fraud_rule import FraudRuleForm
from backend.application.forms.transaction import TransactionForm
from backend.domain.misc_types import TransactionStatus
from backend.infrastructure.api.api_client import AntiFraudApiClient
from tests.utils.exception_validation import validate_exception, validate_validation_error
from tests.utils.misc_types import AuthorizedUser


async def test_ok_admin(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    another_authorized_user: AuthorizedUser,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    transaction_decision = (await api_client.create_transaction(transaction_form)).expect_status(201).unwrap()
    transaction = transaction_decision.transaction

    assert transaction.amount == transaction_form.amount
    assert transaction.currency == transaction_form.currency
    assert transaction.merchant_id == transaction_form.merchant_id
    assert transaction.merchant_category_code == transaction_form.merchant_category_code
    assert transaction.ip_address == str(transaction_form.ip_address)
    assert transaction.device_id == transaction_form.device_id
    assert transaction.channel == transaction_form.channel
    assert transaction.location is not None
    assert transaction.location.country == transaction_form.location.country
    assert transaction.location.city == transaction_form.location.city
    assert transaction.location.latitude == transaction_form.location.latitude
    assert transaction.location.longitude == transaction_form.location.longitude
    assert transaction.user_id == another_authorized_user.user.id
    assert transaction.status == TransactionStatus.APPROVED
    assert transaction.is_fraud is False


async def test_ok_round(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    another_authorized_user: AuthorizedUser,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    transaction_form.amount = Decimal("100.119")

    transaction_decision = (await api_client.create_transaction(transaction_form)).expect_status(201).unwrap()
    transaction = transaction_decision.transaction

    assert transaction.amount == Decimal("100.12")


async def test_rule_results_approved(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    fraud_rule_form: FraudRuleForm,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    transaction_form.amount = Decimal("101.51")
    jobs = []
    rule_names = ["rule1", "rule2", "rule3"]
    enabled: dict[str, bool] = {"rule1": True, "rule2": True, "rule3": False}
    dsl_expr: list[str] = ["amount>=1000", "currency != 'RUB' oR merchantId != 'merchant_001'", "amount > 10"]
    for i in range(3):
        form = fraud_rule_form.model_copy(
            update={
                "name": f"{rule_names[i]}",
                "priority": i + 1,
                "enabled": enabled[rule_names[i]],
                "dsl_expression": dsl_expr[i],
            },
        )
        jobs.append(api_client.create_fraud_rule(form))

    await asyncio.gather(*jobs)

    transaction_decision = (await api_client.create_transaction(transaction_form)).expect_status(201).unwrap()
    transaction = transaction_decision.transaction
    rule_results = transaction_decision.rule_results

    logging.critical(transaction_decision)

    assert len(rule_results) == 2
    assert transaction.is_fraud is False
    assert transaction.status == TransactionStatus.APPROVED

    prev_priority = 0
    for rule_result in rule_results:
        assert rule_result.matched is False
        assert enabled[rule_result.rule_name] is True
        assert rule_result.priority >= prev_priority

        prev_priority = rule_result.priority


async def test_one_rule_result_declined(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    fraud_rule_form: FraudRuleForm,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    fraud_rule_form.priority = 1
    fraud_rule_form.enabled = True
    fraud_rule_form.dsl_expression = "amount >= -100"

    await api_client.create_fraud_rule(fraud_rule_form)

    transaction_decision = (await api_client.create_transaction(transaction_form)).expect_status(201).unwrap()
    transaction = transaction_decision.transaction
    rule_results = transaction_decision.rule_results

    assert len(rule_results) == 1
    assert transaction.is_fraud is True
    assert transaction.status == TransactionStatus.DECLINED

    assert rule_results[0].matched is True
    assert rule_results[0].priority == 1


async def test_rule_results_declined(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    fraud_rule_form: FraudRuleForm,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    jobs = []
    rule_names = ["rule1", "rule2", "rule3"]
    enabled: dict[str, bool] = {"rule1": True, "rule2": False, "rule3": True}
    dsl_expr: list[str] = [
        "amount >= 100",
        "currency != 'RUB' oR merchantId != 'merchant_001'",
        "amount >= -100",
    ]
    for i in range(3):
        form = fraud_rule_form.model_copy(
            update={
                "name": f"{rule_names[i]}",
                "priority": i + 1,
                "enabled": enabled[rule_names[i]],
                "dsl_expression": dsl_expr[i],
            },
        )
        jobs.append(api_client.create_fraud_rule(form))

    await asyncio.gather(*jobs)

    transaction_decision = (await api_client.create_transaction(transaction_form)).expect_status(201).unwrap()
    transaction = transaction_decision.transaction
    rule_results = transaction_decision.rule_results

    logging.critical(transaction_decision)

    assert len(rule_results) == 2
    assert transaction.is_fraud is True
    assert transaction.status == TransactionStatus.DECLINED

    prev_priority = 0
    for rule_result in rule_results:
        assert rule_result.matched is True
        assert enabled[rule_result.rule_name] is True
        assert rule_result.priority >= prev_priority

        prev_priority = rule_result.priority


async def test_ok_self(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(authorized_user.access_token)
    transaction_form.user_id = authorized_user.user.id
    transaction_decision = (await api_client.create_transaction(transaction_form)).expect_status(201).unwrap()
    transaction = transaction_decision.transaction

    assert transaction.user_id == authorized_user.user.id
    assert transaction.amount == transaction_form.amount
    assert transaction.currency == transaction_form.currency


async def test_no_auth(
    api_client: AntiFraudApiClient,
    transaction_form: TransactionForm,
) -> None:
    error_data = (await api_client.create_transaction(transaction_form)).expect_status(401).err_unwrap()

    validate_exception(error_data, UnauthorizedError)


async def test_lat_missing(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(authorized_user.access_token)
    transaction_form.location.latitude = None

    error_data = (await api_client.create_transaction(transaction_form)).expect_status(422).err_unwrap()

    validate_validation_error(error_data, {"latitude": None})


async def test_lon_missing(
    api_client: AntiFraudApiClient,
    authorized_user: AuthorizedUser,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(authorized_user.access_token)
    transaction_form.location.longitude = None

    error_data = (await api_client.create_transaction(transaction_form)).expect_status(422).err_unwrap()

    validate_validation_error(error_data, {"longitude": None})


async def test_user_not_found(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    transaction_form.user_id = uuid4()
    error_data = (await api_client.create_transaction(transaction_form)).expect_status(404).err_unwrap()

    validate_exception(error_data, UserDoesNotExistError)
