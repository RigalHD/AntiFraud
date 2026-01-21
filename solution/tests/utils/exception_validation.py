import logging
from typing import Any

from pydantic import ValidationError

from backend.application.exception.user import EmailAlreadyExistsError
from backend.infrastructure.api.models import DETAILS, ERROR_CODE, ERROR_MESSAGE, APIResponse
from backend.infrastructure.serialization.base import FieldSkip


def validate_exception[T](api_response: APIResponse[T], exc_type: type[Exception]) -> None:
    error_data = api_response.error_data

    assert error_data is not None
    assert error_data.code == ERROR_CODE[exc_type]
    assert error_data.message == ERROR_MESSAGE[exc_type]
    assert error_data.path == "/api/v1/" + api_response.http_response.url

    if exc_type not in (EmailAlreadyExistsError,):
        assert error_data.details == DETAILS.get(exc_type, FieldSkip.SKIP)

    if exc_type == EmailAlreadyExistsError:
        assert isinstance(error_data.details, dict)
        assert error_data.details == {
            "field": "email",
            "value": error_data.details["value"],
        }


def validate_validation_error[T](
    api_response: APIResponse[T],
    exc_type: type[ValidationError],
    invalid_fields: dict[str, Any],
) -> None:
    validate_exception(api_response, exc_type)

    error_data = api_response.error_data
    logging.critical(invalid_fields.keys())
    assert error_data is not None
    assert isinstance(error_data.field_errors, list)
    assert len(error_data.field_errors) == len(invalid_fields.keys())
    
    
    for field_info in error_data.field_errors:
        value = invalid_fields.get(field_info.field)
        assert value is not None
        assert value == field_info.rejected_value
