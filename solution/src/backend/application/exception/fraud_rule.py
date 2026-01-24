from dataclasses import dataclass

from backend.application.exception.base import ApplicationError


@dataclass
class FraudRuleNameAlreadyExistsError(ApplicationError):
    name: str


class FraudRuleDoesNotExistError(ApplicationError): ...
