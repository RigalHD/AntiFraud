from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.application.forms.user import AdminUserForm, UpdateUserForm
from backend.application.user.create import CreateAdminUser
from backend.application.user.delete import DeleteUser
from backend.application.user.read import ReadUser, ReadUsers
from backend.application.user.update import UpdateUser
from backend.bootstrap.di.providers.parsed_data import RequestBody
from backend.presentation.web.serializer import serializer

users_router = APIRouter(route_class=DishkaRoute)


@users_router.post("/")
async def create_user(
    interactor: FromDishka[CreateAdminUser],
    form: RequestBody[AdminUserForm],
) -> JSONResponse:
    result = await interactor.execute(form.data)

    return JSONResponse(
        content=serializer.dump(result),
        status_code=201,
    )


@users_router.get("/me")
async def read_user(interactor: FromDishka[ReadUser]) -> JSONResponse:
    result = await interactor.execute()

    return JSONResponse(
        content=serializer.dump(result),
        status_code=200,
    )


@users_router.get("/")
async def read_many(
    interactor: FromDishka[ReadUsers],
    page: int = 0,
    size: int = 20,
) -> JSONResponse:
    result = await interactor.execute(page=page, size=size)

    return JSONResponse(
        content=serializer.dump(result),
        status_code=200,
    )


@users_router.get("/{id}")
async def read_user_by_id(
    id: UUID,
    interactor: FromDishka[ReadUser],
) -> JSONResponse:
    result = await interactor.execute(id)

    return JSONResponse(
        content=serializer.dump(result),
        status_code=200,
    )


@users_router.put("/me")
async def update_user(
    form: RequestBody[UpdateUserForm],
    interactor: FromDishka[UpdateUser],
) -> JSONResponse:
    result = await interactor.execute(form=form.data)

    return JSONResponse(
        content=serializer.dump(result),
        status_code=200,
    )


@users_router.put("/{id}")
async def update_user_by_id(
    id: UUID,
    form: RequestBody[UpdateUserForm],
    interactor: FromDishka[UpdateUser],
) -> JSONResponse:
    result = await interactor.execute(form=form.data, id=id)

    return JSONResponse(
        content=serializer.dump(result),
        status_code=200,
    )


@users_router.delete("/{id}", status_code=204)
async def delete_user(id: UUID, interactor: FromDishka[DeleteUser]) -> None:
    await interactor.execute(id)
