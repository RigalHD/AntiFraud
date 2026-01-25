from dataclasses import dataclass

from backend.application.exception.base import ApplicationError


class TransactionDoesNotExistError(ApplicationError): ...


class FromGreaterThanToError(ApplicationError): ...


class DatesTooBigDiffError(ApplicationError): ...


class UserIdMissingError(ApplicationError): ...


@dataclass
class MissingLonOrLatError(ApplicationError):
    field: str
    issue: str
    rejected_value: None = None
