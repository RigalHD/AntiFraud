from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    FIELD = auto()
    NUMBER = auto()
    STRING = auto()
    OP = auto()
    AND = auto()
    OR = auto()
    EOF = auto()
    SKIP = auto()


@dataclass
class Token:
    token_type: TokenType
    value: str
    pos: int


TOKEN_SPECS = [
    (TokenType.AND, r"\bAND\b"),
    (TokenType.OR, r"\bOR\b"),
    (TokenType.OP, r">=|<=|!=|>|<|="),
    (TokenType.NUMBER, r"-?\d+(\.\d+)?"),
    (TokenType.STRING, r"'[^']*'"),
    (TokenType.FIELD, r"[a-zA-Z_.]+"),
    (TokenType.SKIP, r"\s+"),
]
