import logging

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from backend.application.exception.base import CustomValidationError
from backend.application.exception.fraud_rule import FraudRuleNameAlreadyExistsError
from backend.application.exception.transaction import MissingLonOrLatError
from backend.application.exception.user import EmailAlreadyExistsError
from backend.infrastructure.api.exception import InternalServerError
from backend.infrastructure.api.models import ERROR_HTTP_CODE, ApiErrorResponse
from backend.infrastructure.parser.pydantic_error import FieldErrorInfo, PydanticErrorInfoParser
from backend.infrastructure.serialization.error import error_serializer


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


async def email_already_exists_error_handler(
    request: Request,
    exc: EmailAlreadyExistsError,
) -> JSONResponse:
    response = ApiErrorResponse.generate_default(type(exc), request.url.path)
    response.details = {
        "field": "email",
        "value": exc.email,
    }
    return JSONResponse(
        content=error_serializer.dump(response),
        status_code=ERROR_HTTP_CODE[type(exc)],
    )


async def fraud_rule_name_already_exists_error_handler(
    request: Request,
    exc: FraudRuleNameAlreadyExistsError,
) -> JSONResponse:
    response = ApiErrorResponse.generate_default(type(exc), request.url.path)
    response.details = {
        "field": "name",
        "value": exc.name,
    }
    return JSONResponse(
        content=error_serializer.dump(response),
        status_code=ERROR_HTTP_CODE[type(exc)],
    )


async def missing_lon_or_lat_error_handler(
    request: Request,
    exc: MissingLonOrLatError,
) -> JSONResponse:
    response = ApiErrorResponse.generate_default(ValidationError, request.url.path)

    error_info = FieldErrorInfo(
        field=exc.field,
        issue=exc.issue,
        rejected_value=exc.rejected_value,
    )
    response.field_errors = [error_info]

    return JSONResponse(
        content=error_serializer.dump(response),
        status_code=ERROR_HTTP_CODE[ValidationError],
    )


async def custom_validation_error_handler(
    request: Request,
    exc: CustomValidationError,
) -> JSONResponse:
    response = ApiErrorResponse.generate_default(ValidationError, request.url.path)

    error_info = FieldErrorInfo(
        field=exc.field,
        issue=exc.issue,
        rejected_value=exc.rejected_value,
    )
    response.field_errors = [error_info]

    return JSONResponse(
        content=error_serializer.dump(response),
        status_code=ERROR_HTTP_CODE[ValidationError],
    )


async def app_error_handler(request: Request, exc: Exception) -> JSONResponse:
    response = ApiErrorResponse.generate_default(type(exc), request.url.path)
    return JSONResponse(
        content=error_serializer.dump(response),
        status_code=ERROR_HTTP_CODE[type(exc)],
    )


async def internal_server_error_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, InternalServerError):
        logging.error(exc)

    response = ApiErrorResponse.generate_default(InternalServerError, request.url.path)
    return JSONResponse(
        content=error_serializer.dump(response),
        status_code=ERROR_HTTP_CODE[InternalServerError],
    )
