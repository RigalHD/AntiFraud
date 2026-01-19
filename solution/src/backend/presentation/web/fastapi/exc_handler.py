from dataclasses import dataclass
from datetime import UTC, datetime
from json import JSONDecodeError
from uuid import UUID, uuid4

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from backend.application.exception.base import ApplicationError, ForbiddenError, InvalidPaginationQueryError
from backend.application.exception.user import EmailAlreadyExistsError, InactiveUserError, UserDoesNotExistError
from backend.infrastructure.exceptions.auth import UnauthorizedError
from backend.presentation.web.serializer import serializer

ERROR_HTTP_CODE = {
    ApplicationError: 500,
    ForbiddenError: 403,
    EmailAlreadyExistsError: 409,
    UserDoesNotExistError: 404,
    UnauthorizedError: 401,
    InvalidPaginationQueryError: 422,
    JSONDecodeError: 400,
    InactiveUserError: 423,
}

ERROR_MESSAGE = {
    ApplicationError: "Unhanded application error",
    ForbiddenError: "Недостаточно прав для выполнения операции",
    EmailAlreadyExistsError: "Пользователь с таким email уже существует",
    UserDoesNotExistError: "User does not exist",
    UnauthorizedError: "Токен отсутствует или невалиден",
    InvalidPaginationQueryError: "Limit or offset < 0",
    JSONDecodeError: "Невалидный JSON",
    InactiveUserError: "Пользователь деактивирован",
}

ERROR_CODE = {
    ApplicationError: "UNHANDLED",
    ForbiddenError: "FORBIDDEN",
    EmailAlreadyExistsError: "EMAIL_ALREADY_EXISTS",
    UserDoesNotExistError: "USER_DOES_NOT_EXIST",
    UnauthorizedError: "UNAUTHORIZED",
    InvalidPaginationQueryError: "INVALID_PAGINATION_QUERY",
    JSONDecodeError: "BAD_REQUEST",
    InactiveUserError: "USER_INACTIVE",
}

DETAIL: dict[type[Exception], dict[str, str | int]] = {
    JSONDecodeError: {"hint": "Проверьте запятые/кавычки"},
}


@dataclass(slots=True, frozen=True)
class ErrorResponse:
    code: str
    message: str
    timestamp: datetime
    path: str
    trace_id: UUID | None = None
    detail: dict[str, str | int] | None = None
    field_errors: dict[str, str | int] | None = None


async def page_not_found_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse({"error": 404})


async def validation_error_handler(request: Request, exc: ValidationError) -> Response:
    response = Response(exc.json(), status_code=422)
    return response


async def json_decode_error_handler(request: Request, exc: JSONDecodeError) -> JSONResponse:
    response = ErrorResponse(
        code=ERROR_CODE[type(exc)],
        message=ERROR_MESSAGE[type(exc)],
        trace_id=uuid4(),
        timestamp=datetime.now(tz=UTC),
        path=request.url.path,
        detail=DETAIL.get(type(exc)),
    )
    return JSONResponse(content=serializer.dump(response), status_code=ERROR_HTTP_CODE[type(exc)])


async def inactive_user_error_handler(request: Request, exc: InactiveUserError) -> JSONResponse:
    response = ErrorResponse(
        code=ERROR_CODE[type(exc)],
        message=ERROR_MESSAGE[type(exc)],
        timestamp=datetime.now(tz=UTC),
        path=request.url.path,
    )
    return JSONResponse(content=serializer.dump(response), status_code=ERROR_HTTP_CODE[type(exc)])


async def app_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
    response = ErrorResponse(
        code=ERROR_CODE[type(exc)],
        message=ERROR_MESSAGE[type(exc)],
        trace_id=uuid4(),
        timestamp=datetime.now(tz=UTC),
        path=request.url.path,
        detail=DETAIL.get(type(exc)),
    )
    return JSONResponse(content=serializer.dump(response), status_code=ERROR_HTTP_CODE[type(exc)])
