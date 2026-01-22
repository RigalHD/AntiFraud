from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.application.forms.user import UserForm
from backend.bootstrap.di.providers.parsed_data import RequestBody
from backend.infrastructure.auth.login import WebLoginForm
from backend.presentation.web.controller.login import WebLogin
from backend.presentation.web.controller.registration import WebRegistration
from backend.presentation.web.serializer import serializer

auth_router = APIRouter(route_class=DishkaRoute)


@auth_router.post("/register")
async def register(
    web_register: FromDishka[WebRegistration],
    web_login: FromDishka[WebLogin],
    form: RequestBody[UserForm],
) -> JSONResponse:
    await web_register.execute(form.data)

    result = await web_login.execute(
        WebLoginForm(
            email=form.data.email,
            password=form.data.password,
        ),
    )

    return JSONResponse(
        content=serializer.dump(result),
        status_code=201,
    )


@auth_router.post("/login")
async def login(
    web_login: FromDishka[WebLogin],
    form: RequestBody[WebLoginForm],
) -> JSONResponse:
    result = await web_login.execute(
        WebLoginForm(
            email=form.data.email,
            password=form.data.password,
        ),
    )

    return JSONResponse(
        content=serializer.dump(result),
        status_code=200,
    )
