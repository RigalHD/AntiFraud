import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from backend.application.exception.base import CustomValidationError, UnauthorizedError
from backend.application.forms.transaction import TransactionForm
from backend.domain.misc_types import TransactionStatus
from backend.infrastructure.api.api_client import AntiFraudApiClient
from tests.utils.exception_validation import validate_exception
from tests.utils.misc_types import AuthorizedUser


async def test_ok_admin(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    another_authorized_user: AuthorizedUser,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    jobs = []
    for i in range(3):
        form = transaction_form.model_copy(update={"amount": Decimal(f"{100 + i}.00")})
        jobs.append(api_client.create_transaction(form))

    await asyncio.gather(*jobs)

    result = (await api_client.read_transactions(page=0, size=20)).expect_status(200).unwrap()

    assert len(result.items) == 3
    assert result.total == 3
    assert result.page == 0
    assert result.size == 20


async def test_ok_user_sees_own(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    authorized_user: AuthorizedUser,
    another_authorized_user: AuthorizedUser,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    transaction_form.user_id = authorized_user.user.id
    (await api_client.create_transaction(transaction_form)).expect_status(201)

    transaction_form.user_id = another_authorized_user.user.id
    (await api_client.create_transaction(transaction_form)).expect_status(201)
    (await api_client.create_transaction(transaction_form)).expect_status(201)

    api_client.authorize(authorized_user.access_token)
    result = (await api_client.read_transactions()).expect_status(200).unwrap()

    assert len(result.items) == 1
    assert result.total == 1
    for item in result.items:
        assert item.user_id == authorized_user.user.id


async def test_ok_pagination(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    another_authorized_user: AuthorizedUser,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    jobs = []
    for i in range(5):
        form = transaction_form.model_copy(update={"amount": Decimal(f"{100 + i}.00")})
        jobs.append(api_client.create_transaction(form))

    await asyncio.gather(*jobs)

    result_page_0 = (await api_client.read_transactions(page=0, size=2)).expect_status(200).unwrap()
    assert len(result_page_0.items) == 2
    assert result_page_0.total == 5
    assert result_page_0.page == 0
    assert result_page_0.size == 2

    result_page_1 = (await api_client.read_transactions(page=1, size=2)).expect_status(200).unwrap()
    assert len(result_page_1.items) == 2
    assert result_page_1.total == 5
    assert result_page_1.page == 1

    result_page_2 = (await api_client.read_transactions(page=2, size=2)).expect_status(200).unwrap()
    assert len(result_page_2.items) == 1
    assert result_page_2.total == 5


async def test_ok_filter_status(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    another_authorized_user: AuthorizedUser,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    (await api_client.create_transaction(transaction_form)).expect_status(201)
    (await api_client.create_transaction(transaction_form)).expect_status(201)

    result = (
        (await api_client.read_transactions(status=TransactionStatus.APPROVED.value))
        .expect_status(200)
        .unwrap()
    )

    assert result.total >= 0
    for item in result.items:
        assert item.status == TransactionStatus.APPROVED


async def test_ok_filter_is_fraud(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    another_authorized_user: AuthorizedUser,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    (await api_client.create_transaction(transaction_form)).expect_status(201)

    result = (await api_client.read_transactions(isFraud=False)).expect_status(200).unwrap()

    for item in result.items:
        assert item.is_fraud is False


async def test_no_auth(
    api_client: AntiFraudApiClient,
) -> None:
    error_data = (await api_client.read_transactions()).expect_status(401).err_unwrap()

    validate_exception(error_data, UnauthorizedError)


async def test_from_greater_than_to(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
) -> None:
    api_client.authorize(admin_user.access_token)

    now = datetime.now(tz=UTC)
    error_data = (
        (
            await api_client.read_transactions(
                from_=now,
                to=now - timedelta(days=1),
            )
        )
        .expect_status(422)
        .err_unwrap()
    )

    validate_exception(error_data, CustomValidationError)


async def test_interval_too_large(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
) -> None:
    api_client.authorize(admin_user.access_token)

    now = datetime.now(tz=UTC)
    error_data = (
        (
            await api_client.read_transactions(
                from_=now - timedelta(days=100),
                to=now,
            )
        )
        .expect_status(422)
        .err_unwrap()
    )

    validate_exception(error_data, CustomValidationError)
