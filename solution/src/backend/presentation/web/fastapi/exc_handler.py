from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from json import JSONDecodeError
from uuid import UUID, uuid4

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from backend.application.exception.base import (
    ApplicationError,
    ForbiddenError,
    InvalidPaginationQueryError,
    NotFoundError,
)
from backend.application.exception.user import EmailAlreadyExistsError, InactiveUserError, UserDoesNotExistError
from backend.infrastructure.auth.exception import UnauthorizedError
from backend.infrastructure.parser.pydantic_error import FieldErrorInfo, PydanticErrorInfoParser
from backend.infrastructure.serialization.error import FieldSkip, error_serializer
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
class ErrResponse:
    code: str
    message: str
    timestamp: datetime
    path: str
    trace_id: UUID | FieldSkip = FieldSkip.SKIP
    detail: dict[str, str | int] | FieldSkip = FieldSkip.SKIP
    field_errors: list[FieldErrorInfo] | FieldSkip = FieldSkip.SKIP

    @staticmethod
    def generate_default(exc_type: type[Exception], path: str) -> ErrResponse:
        return ErrResponse(
            code=ERROR_CODE[exc_type],
            message=ERROR_MESSAGE[exc_type],
            trace_id=uuid4(),
            timestamp=datetime.now(tz=UTC),
            path=path,
            detail=DETAIL.get(exc_type, FieldSkip.SKIP),
        )


async def page_not_found_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({"error": "Page not found"}, status_code=404)


async def validation_error_handler(
    request: Request,
    exc: ValidationError,
) -> Response:
    response = ErrResponse.generate_default(type(exc), request.url.path)
    response.field_errors = PydanticErrorInfoParser().get_validation_error_info(exc)

    return JSONResponse(
        content=error_serializer.dump(response, ErrResponse),
        status_code=ERROR_HTTP_CODE[type(exc)],
    )


async def email_already_exists_error_handler(request: Request, exc: EmailAlreadyExistsError) -> JSONResponse:
    response = ErrResponse.generate_default(type(exc), request.url.path)
    response.detail = {
        "field": "email",
        "value": exc.email,
    }
    return JSONResponse(content=error_serializer.dump(response), status_code=ERROR_HTTP_CODE[type(exc)])


async def app_error_handler(request: Request, exc: Exception) -> JSONResponse:
    response = ErrResponse.generate_default(type(exc), request.url.path)
    return JSONResponse(content=error_serializer.dump(response), status_code=ERROR_HTTP_CODE[type(exc)])


async def internal_server_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.error(exc)
    response = ErrResponse.generate_default(InternalServerError, request.url.path)
    return JSONResponse(content=error_serializer.dump(response), status_code=ERROR_HTTP_CODE[InternalServerError])
