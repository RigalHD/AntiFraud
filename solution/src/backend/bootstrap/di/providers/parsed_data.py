from dataclasses import dataclass
from typing import Generic, TypeVar
from backend.application.forms.base import BaseForm
from backend.application.user.create import CreateUser
from backend.application.user.read import ReadUser
from backend.presentation.web.controller.registration import WebRegistration
from dishka import FromDishka, Provider, Scope, provide, provide_all
from fastapi import Request


@dataclass
class ParsedData[T: BaseForm]:
    parsed_data: T


class ParsedDataProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def parse_data[T: BaseForm](self, request: Request, t: type[T]) -> ParsedData[T]:
        return ParsedData[T](t(**(await request.json())))
    
    
T = TypeVar("T", bound=BaseForm)
RequestData = FromDishka[ParsedData[T]]
