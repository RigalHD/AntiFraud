from abc import abstractmethod
from typing import Protocol

from backend.infrastructure.auth.access_token import AccessToken


class AccessTokenParser(Protocol):
    @abstractmethod
    def parse_token(self) -> AccessToken: ...
