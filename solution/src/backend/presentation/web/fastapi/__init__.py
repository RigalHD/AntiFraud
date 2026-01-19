from json import JSONDecodeError

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from backend.application.exception.base import ApplicationError, ForbiddenError
from backend.application.exception.user import InactiveUserError
from backend.presentation.web.fastapi.auth import auth_router
from backend.presentation.web.fastapi.exc_handler import (
    app_error_handler,
    inactive_user_error_handler,
    json_decode_error_handler,
    page_not_found_exception_handler,
    validation_error_handler,
)
from backend.presentation.web.fastapi.main import main_router


def include_routers(app: FastAPI) -> None:
    app.include_router(main_router, prefix="/api/v1", tags=["main"])
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(404, page_not_found_exception_handler)  # type: ignore
    app.add_exception_handler(405, page_not_found_exception_handler)  # type: ignore
    app.add_exception_handler(422, validation_error_handler)  # type: ignore
    app.add_exception_handler(ForbiddenError, page_not_found_exception_handler)  # type: ignore
    app.add_exception_handler(JSONDecodeError, json_decode_error_handler)  # type: ignore
    app.add_exception_handler(InactiveUserError, inactive_user_error_handler)  # type: ignore
    app.add_exception_handler(ValidationError, validation_error_handler)  # type: ignore
    app.add_exception_handler(ApplicationError, app_error_handler)  # type: ignore


def include_middlewares(app: FastAPI) -> None:
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
