from backend.infrastructure.api.api_client import AntiFraudApiClient
from backend.infrastructure.api.exception import InternalServerError
from tests.utils.exception_validation import validate_exception


async def test_ok(api_client: AntiFraudApiClient) -> None:
    resp = await api_client.ping()

    assert resp.http_response.status == 200
    assert resp.error_data is None
    assert resp.data is not None
    assert resp.data.status == "ok"


async def test_internal_server_error_ok(api_client: AntiFraudApiClient) -> None:
    resp = await api_client.error()

    assert resp.http_response.status == 500
    assert resp.data is None
    assert resp.error_data is not None

    validate_exception(resp, InternalServerError)
