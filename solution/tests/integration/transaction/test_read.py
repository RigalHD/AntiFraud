from uuid import uuid4

from backend.application.exception.base import ForbiddenError, UnauthorizedError
from backend.application.exception.transaction import TransactionDoesNotExistError
from backend.application.forms.transaction import TransactionForm
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

    created = (await api_client.create_transaction(transaction_form)).expect_status(201).unwrap()
    transaction_id = created.transaction.id

    read_result = (await api_client.read_transaction(transaction_id)).expect_status(200).unwrap()

    assert read_result.transaction.id == transaction_id
    assert read_result.transaction.amount == created.transaction.amount
    assert read_result.transaction.currency == created.transaction.currency
    assert read_result.transaction.user_id == another_authorized_user.user.id


async def test_ok_self(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    authorized_user: AuthorizedUser,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    transaction_form.user_id = authorized_user.user.id
    created = (await api_client.create_transaction(transaction_form)).expect_status(201).unwrap()
    transaction_id = created.transaction.id

    api_client.authorize(authorized_user.access_token)
    read_result = (await api_client.read_transaction(transaction_id)).expect_status(200).unwrap()

    assert read_result.transaction.id == transaction_id
    assert read_result.transaction.user_id == authorized_user.user.id


async def test_no_auth(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    another_authorized_user: AuthorizedUser,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    created = (await api_client.create_transaction(transaction_form)).expect_status(201).unwrap()
    transaction_id = created.transaction.id

    api_client.reset_authorization()
    error_data = (await api_client.read_transaction(transaction_id)).expect_status(401).err_unwrap()

    validate_exception(error_data, UnauthorizedError)


async def test_forbidden(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
    authorized_user: AuthorizedUser,
    transaction_form: TransactionForm,
) -> None:
    api_client.authorize(admin_user.access_token)

    created = (await api_client.create_transaction(transaction_form)).expect_status(201).unwrap()
    transaction_id = created.transaction.id

    api_client.authorize(authorized_user.access_token)
    error_data = (await api_client.read_transaction(transaction_id)).expect_status(403).err_unwrap()

    validate_exception(error_data, ForbiddenError)


async def test_not_found(
    api_client: AntiFraudApiClient,
    admin_user: AuthorizedUser,
) -> None:
    api_client.authorize(admin_user.access_token)

    error_data = (await api_client.read_transaction(uuid4())).expect_status(404).err_unwrap()

    validate_exception(error_data, TransactionDoesNotExistError)
