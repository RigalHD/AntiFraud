from backend.application.common.gateway.user import UserGateway
from backend.infrastructure.auth.provider import WebUserAuthForm
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
    request: Request,
    # web_register: FromDishka[WebRegister],
    gateway: FromDishka[UserGateway],
) -> JSONResponse:
    form = WebUserAuthForm(**(await request.json()))
    # container: AsyncContextWrapper = AsyncContextWrapper(request.state.dishka_container)

    # controller = WebRegister(
    #     container=container,
    #     web_register=web_register,
    #     gateway=gateway,
    # )

    # await controller.execute(form)
    
    
    
    return serializer.dump(form)