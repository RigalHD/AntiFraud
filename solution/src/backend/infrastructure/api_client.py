from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from json import JSONDecodeError
from typing import Literal, Self
from uuid import UUID, uuid4

from adaptix import Retort
from aiohttp import ClientSession
from descanso import RestBuilder
from descanso.client import AsyncResponseWrapper
from descanso.http.aiohttp import AiohttpClient
from descanso.request import HttpRequest
from descanso.response import BaseResponseTransformer
from descanso.response import HttpResponse as DescansoHttpResponse
from pydantic import ValidationError

from backend.application.exception.base import (
    ApplicationError,
    ForbiddenError,
    InvalidPaginationQueryError,
    NotFoundError,
)
from backend.application.exception.user import EmailAlreadyExistsError, InactiveUserError, UserDoesNotExistError
from backend.infrastructure.auth.exception import UnauthorizedError
from backend.infrastructure.parser.pydantic_error import FieldErrorInfo
from backend.infrastructure.serialization.api_client import api_dump_serializer, api_load_serializer
from backend.infrastructure.serialization.base import FieldSkip
from backend.presentation.web.fastapi.exception import InternalServerError

ERROR_HTTP_CODE = {
    ApplicationError: 500,
    ForbiddenError: 403,
    NotFoundError: 404,
    EmailAlreadyExistsError: 409,
    UserDoesNotExistError: 404,
    UnauthorizedError: 401,
    InvalidPaginationQueryError: 422,
    JSONDecodeError: 400,
    InactiveUserError: 423,
    ValidationError: 422,
    InternalServerError: 500,
}

ERROR_MESSAGE = {
    ApplicationError: "Unhanded application error",
    InternalServerError: "Внутренняя ошибка сервера",
    NotFoundError: "Ресурс не найден",
    ForbiddenError: "Недостаточно прав для выполнения операции",
    EmailAlreadyExistsError: "Пользователь с таким email уже существует",
    UserDoesNotExistError: "User does not exist",
    UnauthorizedError: "Токен отсутствует или невалиден",
    InvalidPaginationQueryError: "Limit or offset < 0",
    JSONDecodeError: "Невалидный JSON",
    InactiveUserError: "Пользователь деактивирован",
    ValidationError: "Некоторые поля не прошли валидацию",
}

ERROR_CODE = {
    ApplicationError: "UNHANDLED",
    InternalServerError: "INTERNAL_SERVER_ERROR",
    ForbiddenError: "FORBIDDEN",
    NotFoundError: "NOT_FOUND",
    EmailAlreadyExistsError: "EMAIL_ALREADY_EXISTS",
    UserDoesNotExistError: "NOT_FOUND",
    UnauthorizedError: "UNAUTHORIZED",
    InvalidPaginationQueryError: "INVALID_PAGINATION_QUERY",
    JSONDecodeError: "BAD_REQUEST",
    InactiveUserError: "USER_INACTIVE",
    ValidationError: "VALIDATION_FAILED",
}

DETAIL: dict[type[Exception], dict[str, str | int]] = {
    JSONDecodeError: {"hint": "Проверьте запятые/кавычки"},
}


@dataclass(slots=True)
class ApiErrorResponse:
    code: str
    message: str
    timestamp: datetime
    path: str
    trace_id: UUID | FieldSkip = FieldSkip.SKIP
    detail: dict[str, str | int] | FieldSkip = FieldSkip.SKIP
    field_errors: list[FieldErrorInfo] | FieldSkip = FieldSkip.SKIP

    @staticmethod
    def generate_default(exc_type: type[Exception], path: str) -> ApiErrorResponse:
        return ApiErrorResponse(
            code=ERROR_CODE[exc_type],
            message=ERROR_MESSAGE[exc_type],
            trace_id=uuid4(),
            timestamp=datetime.now(tz=UTC),
            path=path,
            detail=DETAIL.get(exc_type, FieldSkip.SKIP),
        )


@dataclass(slots=True, frozen=True)
class HttpResponse:
    status: int
    url: str


class StatusMismatchError(Exception): ...


class UnableToUnwrapError(Exception): ...


@dataclass(slots=True, frozen=True)
class APIResponse[T]:
    data: T | None
    http_response: HttpResponse
    error: ApiErrorResponse | None

    def compare_status(self, expected_status: int) -> Self:
        if (response_status := self.http_response.status) != expected_status:
            message = f"Ожидаемый статус: {expected_status}, полученный: {response_status}"
            raise StatusMismatchError(message)
        return self

    def unwrap(self) -> T:
        if self.data is None:
            raise UnableToUnwrapError

        return self.data


@dataclass(slots=True, frozen=True)
class PingResponse:
    status: Literal["ok"]


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
