from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.infrastructure.api.exception import InternalServerError

main_router = APIRouter(route_class=DishkaRoute)


@main_router.get("/ping")
async def ping() -> dict[str, str]:
    return {"status": "ok"}


@main_router.get("/")
async def main_page() -> JSONResponse:
    return JSONResponse(content={"foo": "bar"}, status_code=200)


@main_router.get("/error")
async def internal_server_error() -> None:
    raise InternalServerError
