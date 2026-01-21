from backend.infrastructure.api.api_client import AntiFraudApiClient


async def test_ok(api_client: AntiFraudApiClient) -> None:
    resp = await api_client.ping()
    assert resp.http_response.status == 200
    assert resp.error_data is None
    assert resp.data is not None
    assert resp.data.status == "ok"
