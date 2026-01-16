from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from backend.application.exception.base import AccessDeniedError, ApplicationError, InvalidPaginationQueryError
from backend.application.exception.user import UserAlreadyExistsError, UserDoesNotExistError
from backend.infrastructure.exceptions.auth import (
    UnauthenticatedError,
    UnauthorizedError,
)

ERROR_HTTP_CODE = {
    ApplicationError: 500,
    AccessDeniedError: 403,
    UserAlreadyExistsError: 409,
    UserDoesNotExistError: 404,
    UnauthenticatedError: 401,
    UnauthorizedError: 403,
    InvalidPaginationQueryError: 422,
}

ERROR_MESSAGE = {
    ApplicationError: "Unhanded application error",
    AccessDeniedError: "Access denied",
    UserAlreadyExistsError: "User already exists",
    UserDoesNotExistError: "User does not exist",
    UnauthenticatedError: "User is not authenticated",
    UnauthorizedError: "User is not authorized to perform this action",
    InvalidPaginationQueryError: "Limit or offset < 0",
}

ERROR_CODE = {
    ApplicationError: "UNHANDLED",
    AccessDeniedError: "ACCESS_DENIED",
    UserAlreadyExistsError: "USER_ALREADY_EXISTS",
    UserDoesNotExistError: "USER_DOES_NOT_EXIST",
    UnauthenticatedError: "UNAUTHENTICATED",
    UnauthorizedError: "UNAUTHORIZED",
    InvalidPaginationQueryError: "INVALID_PAGINATION_QUERY",
}


async def page_not_found_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse({"error": 404})


async def validation_error_handler(request: Request, exc: ValidationError) -> Response:
    response = Response(exc.json(), status_code=422)
    return response


async def app_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
    content = {
        "description": ERROR_MESSAGE[type(exc)],
        "unique_code": ERROR_CODE[type(exc)],
    }
    response = JSONResponse(content=content, status_code=ERROR_HTTP_CODE[type(exc)])

    return response
