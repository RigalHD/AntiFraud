import logging

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from backend.application.exception.user import EmailAlreadyExistsError
from backend.infrastructure.api.exception import InternalServerError
from backend.infrastructure.api.models import ERROR_HTTP_CODE, ApiErrorResponse
from backend.infrastructure.parser.pydantic_error import PydanticErrorInfoParser
from backend.infrastructure.serialization.error import error_serializer


async def page_not_found_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({"error": "Page not found"}, status_code=404)


async def validation_error_handler(
    request: Request,
    exc: ValidationError,
) -> Response:
    response = ApiErrorResponse.generate_default(type(exc), request.url.path)
    response.field_errors = PydanticErrorInfoParser().get_validation_error_info(exc)

    return JSONResponse(
        content=error_serializer.dump(response, ApiErrorResponse),
        status_code=ERROR_HTTP_CODE[type(exc)],
    )


async def email_already_exists_error_handler(request: Request, exc: EmailAlreadyExistsError) -> JSONResponse:
    response = ApiErrorResponse.generate_default(type(exc), request.url.path)
    response.detail = {
        "field": "email",
        "value": exc.email,
    }
    return JSONResponse(content=error_serializer.dump(response), status_code=ERROR_HTTP_CODE[type(exc)])


async def app_error_handler(request: Request, exc: Exception) -> JSONResponse:
    response = ApiErrorResponse.generate_default(type(exc), request.url.path)
    return JSONResponse(content=error_serializer.dump(response), status_code=ERROR_HTTP_CODE[type(exc)])


async def internal_server_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.error(exc)
    response = ApiErrorResponse.generate_default(InternalServerError, request.url.path)
    return JSONResponse(content=error_serializer.dump(response), status_code=ERROR_HTTP_CODE[InternalServerError])
