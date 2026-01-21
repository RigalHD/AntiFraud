from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from adaptix import Retort
from aiohttp import ClientSession
from descanso import RestBuilder
from descanso.client import AsyncResponseWrapper
from descanso.http.aiohttp import AiohttpClient
from descanso.request import HttpRequest
from descanso.response import BaseResponseTransformer
from descanso.response import HttpResponse as DescansoHttpResponse

from backend.infrastructure.api.models import APIResponse, HttpResponse, PingResponse
from backend.infrastructure.serialization.api_client import api_dump_serializer, api_load_serializer


class ApiResponseTransformer(BaseResponseTransformer):
    def need_response_body(self, response: DescansoHttpResponse) -> bool:
        return False

    def transform_response(
        self,
        request: HttpRequest,
        response: DescansoHttpResponse,
    ) -> DescansoHttpResponse:
        data = None
        http_response = HttpResponse(status=response.status_code, url=response.url)
        error_data = None

        if response.status_code >= 200 and response.status_code < 300:
            data = response.body
        elif response.status_code >= 400:
            error_data = response.body

        response.body = {"data": data, "http_response": http_response, "error_data": error_data}

        return response


rest = RestBuilder(
    request_body_dumper=api_dump_serializer,
    response_body_loader=api_load_serializer,
    query_param_dumper=Retort(),
    response_body_pre_load=ApiResponseTransformer(),
)


class AntiFraudApiClient(AiohttpClient):
    def __init__(self, base_url: str, session: ClientSession, token: str | None = None) -> None:
        super().__init__(
            base_url=base_url,
            session=session,
        )
        self.token = token

    def authorize_by_token(self, token: str) -> None:
        self.token = token

    def reset_authorization(self) -> None:
        self.token = None

    @asynccontextmanager
    async def asend_request(
        self,
        request: HttpRequest,
    ) -> AsyncIterator[AsyncResponseWrapper]:
        if self.token is not None:
            request.headers["Authorization"] = f"Bearer {self.token}"

        async with super().asend_request(request) as response:
            yield response

    @rest.get("ping/")
    def ping(self) -> APIResponse[PingResponse]:
        raise NotImplementedError
