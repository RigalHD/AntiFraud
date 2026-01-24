from dataclasses import dataclass
from typing import Any, Protocol


class ASTNode(Protocol):
    left: Any
    operator: str
    right: Any


@dataclass(slots=True, frozen=True)
class Comparison(ASTNode):
    left: str
    operator: str
    right: int | str


@dataclass(slots=True, frozen=True)
class Logical(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode
