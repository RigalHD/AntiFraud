from dataclasses import dataclass

from backend.application.exception.base import ApplicationError


@dataclass
class FraudRuleNameAlreadyExistsError(ApplicationError):
    name: str


class FraudRuleDoesNotExistError(ApplicationError): ...


class DSLError(ApplicationError): ...


class DSLParseError(DSLError): ...


class DSLInvalidFieldError(DSLError): ...


class DSLInvalidOperatorError(DSLError): ...
