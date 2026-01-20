from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError
from pydantic_core import ErrorDetails

OPERATOR_MAPPING = {
    "ge": ">=",
    "le": "<=",
    "gt": ">",
    "lt": "<",
    "eq": "==",
    "ne": "!=",
}


@dataclass(slots=True, frozen=True)
class FieldErrorInfo:
    field: str
    issue: str
    rejected_value: Any


class PydanticErrorInfoParser:
    def _parse_field_error_info(self, details: ErrorDetails) -> FieldErrorInfo:
        field = str(details["loc"][0])
        rejected_value = details["input"]
        issue = details["msg"]

        result = FieldErrorInfo(
            field=field,
            issue=issue,
            rejected_value=rejected_value,
        )

        return result

    def get_validation_error_info(self, exc: ValidationError) -> list[FieldErrorInfo]:
        return [self._parse_field_error_info(error) for error in exc.errors()]
