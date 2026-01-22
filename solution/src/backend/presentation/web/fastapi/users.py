from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.application.user.read import ReadUser
from backend.presentation.web.serializer import serializer

users_router = APIRouter(route_class=DishkaRoute)


@users_router.get("/me")
async def read_user(interactor: FromDishka[ReadUser]) -> JSONResponse:
    result = await interactor.execute()

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
