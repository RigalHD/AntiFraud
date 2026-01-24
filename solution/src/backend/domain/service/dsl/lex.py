import re
from dataclasses import dataclass

from backend.domain.exception.dsl import DSLParseError
from backend.domain.service.dsl.tokens import TOKEN_SPECS, Token, TokenType


@dataclass(slots=True)
class Lexer:
    text: str
    pos: int = 0

    def _next_token(self) -> Token | None:
        for token_type, pattern in TOKEN_SPECS:
            mtch = re.compile(pattern, re.IGNORECASE).match(self.text, self.pos)

            if mtch is None:
                continue

            value = mtch.group()
            position = self.pos
            self.pos = mtch.end()

            if token_type == TokenType.SKIP:
                return None

            if token_type in (TokenType.AND, TokenType.OR, TokenType.NOT):
                value = value.upper()

            return Token(token_type=token_type, value=value, position=position)

        raise DSLParseError(
            message="Ошибка при парсинге DSL",
            position=self.pos,
            near=self.text[self.pos : self.pos + 10],
        )

    def tokenize(self) -> list[Token]:
        tokens = []

        while self.pos < len(self.text):
            token = self._next_token()
            if token:
                tokens.append(token)

        tokens.append(Token(TokenType.EOF, "", self.pos))
        return tokens
