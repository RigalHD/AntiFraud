from typing import Protocol

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class Hasher(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, raw: str, hashed: str) -> bool: ...


class ArgonHasher(Hasher):
    argon: PasswordHasher

    def hash(self, password: str) -> str:
        return self.argon.hash(password)

    def verify(self, raw: str, hashed: str) -> bool:
        try:
            return self.argon.verify(hashed, raw)
        except VerifyMismatchError:
            return False
