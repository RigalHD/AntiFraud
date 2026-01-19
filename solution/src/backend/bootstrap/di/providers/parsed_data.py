from dataclasses import dataclass
from typing import TypeVar

from dishka import FromDishka, Provider, Scope, provide
from fastapi import Request

from backend.application.forms.base import BaseForm

T = TypeVar("T", bound=BaseForm)


@dataclass
class ParsedData[T: BaseForm]:
    data: T


class ParsedDataProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def parse_data(self, request: Request, t: type[T]) -> ParsedData[T]:
        return ParsedData(t(**(await request.json())))


RequestData = FromDishka[ParsedData[T]]
