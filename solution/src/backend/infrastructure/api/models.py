from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from json import JSONDecodeError
from typing import Literal, Self
from uuid import UUID, uuid4

from pydantic import ValidationError

from backend.application.exception.base import (
    ApplicationError,
    ForbiddenError,
    InvalidPaginationQueryError,
    NotFoundError,
    UnauthorizedError,
)
from backend.application.exception.user import EmailAlreadyExistsError, InactiveUserError, UserDoesNotExistError
from backend.infrastructure.api.exception import InternalServerError, StatusMismatchError, UnableToUnwrapError
from backend.infrastructure.parser.pydantic_error import FieldErrorInfo
from backend.infrastructure.serialization.base import FieldSkip

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

DETAILS: dict[type[Exception], dict[str, str | int]] = {
    JSONDecodeError: {"hint": "Проверьте запятые/кавычки"},
}


@dataclass(slots=True)
class ApiErrorResponse:
    # Обязательно при инициализации нужно отрезать слеш в конце
    code: str
    message: str
    timestamp: datetime
    path: str
    trace_id: UUID
    details: dict[str, str | int] | FieldSkip = FieldSkip.SKIP
    field_errors: list[FieldErrorInfo] | FieldSkip = FieldSkip.SKIP

    @staticmethod
    def generate_default(exc_type: type[Exception], path: str) -> ApiErrorResponse:
        return ApiErrorResponse(
            code=ERROR_CODE[exc_type],
            message=ERROR_MESSAGE[exc_type],
            trace_id=uuid4(),
            timestamp=datetime.now(tz=UTC),
            path=path.rstrip("/"),
            details=DETAILS.get(exc_type, FieldSkip.SKIP),
        )


@dataclass(slots=True, frozen=True)
class HttpResponse:
    status: int
    url: str


@dataclass(slots=True, frozen=True)
class PingResponse:
    status: Literal["ok"]


@dataclass(slots=True, frozen=True)
class UnwrappedErrorData:
    http_response: HttpResponse
    error_data: ApiErrorResponse


@dataclass(slots=True, frozen=True)
class APIResponse[T]:
    data: T | None
    http_response: HttpResponse
    error_data: ApiErrorResponse | None

    def expect_status(self, expected_status: int) -> Self:
        if (response_status := self.http_response.status) != expected_status:
            message = f"Ожидаемый статус: {expected_status}, полученный: {response_status}"
            raise StatusMismatchError(message)

        return self

    def unwrap(self) -> T:
        if self.data is not None and self.error_data is None:
            return self.data

        raise UnableToUnwrapError

    def err_unwrap(self) -> UnwrappedErrorData:
        if self.data is None and self.error_data is not None:
            return UnwrappedErrorData(
                http_response=self.http_response,
                error_data=self.error_data,
            )

        raise UnableToUnwrapError
