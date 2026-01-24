from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class DSLErrorInfo:
    code: str
    message: str
    position: int | None = None
    near: str | None = None
