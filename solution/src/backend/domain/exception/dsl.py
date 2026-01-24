from dataclasses import dataclass


@dataclass
class DSLError(Exception):
    message: str


@dataclass
class DSLParseError(DSLError):
    message: str
    position: int
    near: str


@dataclass
class DSLInvalidFieldError(DSLError):
    message: str


@dataclass
class DSLInvalidOperatorError(DSLError):
    message: str
