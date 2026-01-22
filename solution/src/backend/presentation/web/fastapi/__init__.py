from json import JSONDecodeError

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from backend.application.exception.base import ApplicationError
from backend.application.exception.user import EmailAlreadyExistsError
from backend.infrastructure.api.exception import InternalServerError
from backend.presentation.web.fastapi.auth import auth_router
from backend.presentation.web.fastapi.exc_handler import (
    app_error_handler,
    email_already_exists_error_handler,
    internal_server_error_handler,
    validation_error_handler,
)
from backend.presentation.web.fastapi.main import main_router


def include_routers(app: FastAPI) -> None:
    app.include_router(main_router, prefix="/api/v1", tags=["main"])
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(InternalServerError, internal_server_error_handler)
    app.add_exception_handler(EmailAlreadyExistsError, email_already_exists_error_handler)  # type: ignore
    app.add_exception_handler(ValidationError, validation_error_handler)  # type: ignore
    app.add_exception_handler(JSONDecodeError, app_error_handler)
    app.add_exception_handler(ApplicationError, app_error_handler)
    app.add_exception_handler(Exception, internal_server_error_handler)


def include_middlewares(app: FastAPI) -> None:
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
