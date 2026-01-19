from backend.application.common.gateway.user import UserGateway
from backend.application.forms.user import UserForm
from backend.bootstrap.di.providers.parsed_data import RequestData
from backend.presentation.web.controller.registration import WebRegistration
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from dishka import FromDishka
from backend.presentation.web.serializer import serializer
from dishka.async_container import AsyncContextWrapper
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

auth_router = APIRouter(route_class=DishkaRoute)


@auth_router.post("/register")
async def register(
    # request: Request,
    # web_register: FromDishka[WebRegistration],
    form: RequestData[UserForm],
) -> JSONResponse:
    # form = UserForm(**(await request.json()))
    # container: AsyncContextWrapper = AsyncContextWrapper(request.state.dishka_container)

    # await web_register.execute(form)
    
    
    
    return serializer.dump(form)