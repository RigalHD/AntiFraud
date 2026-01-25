from dataclasses import dataclass
from typing import Any


class ApplicationError(Exception): ...


class ForbiddenError(ApplicationError): ...


class NotFoundError(ApplicationError): ...


@dataclass
class CustomValidationError(ApplicationError):
    field: str
    rejected_value: Any
    issue: str


class UnauthorizedError(ApplicationError): ...
