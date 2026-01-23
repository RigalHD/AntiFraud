from dataclasses import dataclass

from backend.application.exception.base import ApplicationError


@dataclass
class FraudRuleNameAlreadyExistsError(ApplicationError):
    name: str


class FraudRuleDoesNotExistError(ApplicationError): ...


class DSLError(ApplicationError): ...


class DSLParseError(DSLError):
    message: str
    position: int
    near: str


class DSLInvalidFieldError(DSLError):
    message: str
    field: str


class DSLInvalidOperatorError(DSLError):
    operator: str
    type_: str
