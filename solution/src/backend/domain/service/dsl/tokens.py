from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    FIELD = auto()
    NUMBER = auto()
    STRING = auto()
    OP = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOF = auto()
    SKIP = auto()


@dataclass
class Token:
    token_type: TokenType
    value: str
    position: int


TOKEN_SPECS = [
    (TokenType.AND, r"\bAND\b"),
    (TokenType.OR, r"\bOR\b"),
    (TokenType.NOT, r"\bNOT\b"),
    (TokenType.OP, r">=|<=|!=|>|<|="),
    (TokenType.LPAREN, r"\("),
    (TokenType.RPAREN, r"\)"),
    (TokenType.NUMBER, r"\d+(\.\d+)?"),
    (TokenType.STRING, r"'[^']*'"),
    (TokenType.FIELD, r"[a-zA-Z_.]+"),
    (TokenType.SKIP, r"\s+"),
]
