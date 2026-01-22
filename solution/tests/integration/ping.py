from backend.infrastructure.api.api_client import AntiFraudApiClient
from backend.infrastructure.api.exception import InternalServerError
from tests.utils.exception_validation import validate_exception


async def test_ok(api_client: AntiFraudApiClient) -> None:
    data = (await api_client.ping()).expect_status(200).unwrap()

    assert data.status == "ok"


async def test_internal_server_error_ok(api_client: AntiFraudApiClient) -> None:
    error_data = (await api_client.error()).expect_status(500).err_unwrap()

    validate_exception(error_data, InternalServerError)
