from typing import Any

from pydantic import ValidationError

from backend.application.exception.fraud_rule import FraudRuleNameAlreadyExistsError
from backend.application.exception.user import EmailAlreadyExistsError
from backend.infrastructure.api.models import DETAILS, ERROR_CODE, ERROR_MESSAGE, UnwrappedErrorData
from backend.infrastructure.serialization.base import FieldSkip


def validate_exception(data: UnwrappedErrorData, exc_type: type[Exception]) -> None:
    error_data = data.error_data

    assert error_data is not None
    assert error_data.code == ERROR_CODE[exc_type]
    assert error_data.message == ERROR_MESSAGE[exc_type]
    assert error_data.path == "/api/v1/" + data.http_response.url

    if exc_type not in (EmailAlreadyExistsError, FraudRuleNameAlreadyExistsError):
        assert error_data.details == DETAILS.get(exc_type, FieldSkip.SKIP)

    if exc_type == EmailAlreadyExistsError:
        assert isinstance(error_data.details, dict)
        assert error_data.details == {
            "field": "email",
            "value": error_data.details["value"],
        }

    if exc_type == FraudRuleNameAlreadyExistsError:
        assert isinstance(error_data.details, dict)
        assert error_data.details == {
            "field": "name",
            "value": error_data.details["value"],
        }


def validate_validation_error(
    data: UnwrappedErrorData,
    invalid_fields: dict[str, Any],
) -> None:
    validate_exception(data, ValidationError)

    error_data = data.error_data

    assert error_data is not None
    assert isinstance(error_data.field_errors, list)
    assert len(error_data.field_errors) == len(invalid_fields.keys())

    for field_info in error_data.field_errors:
        value = invalid_fields.get(field_info.field)
        assert value is not None
        assert value == field_info.rejected_value
