import logging
import sys
from collections.abc import AsyncIterator
from contextlib import suppress
from uuid import uuid4

import uvicorn
from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from sqlalchemy.exc import IntegrityError

from backend.application.common.uow import UoW
from backend.application.forms.user import AdminUserForm
from backend.bootstrap.di.container import get_async_container
from backend.domain.entity.user import User
from backend.domain.misc_types import Role
from backend.infrastructure.auth.hasher import Hasher
from backend.infrastructure.config_loader import AdminConfig
from backend.presentation.web.fastapi import (
    include_exception_handlers,
    include_middlewares,
    include_routers,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    container: AsyncContainer = app.state.dishka_container

    async with container() as r_container:
        cfg = await r_container.get(AdminConfig)
        uow = await r_container.get(UoW)
        hasher = await r_container.get(Hasher)

        form = AdminUserForm(
            email=cfg.admin_email,
            password=cfg.admin_password,
            fullName=cfg.admin_full_name,
            role=Role.ADMIN,
        )

        user = User(
            id=uuid4(),
            email=form.email,
            password=hasher.hash(form.password),
            full_name=form.full_name,
            age=form.age,
            region=form.region,
            gender=form.gender,
            marital_status=form.marital_status,
            role=form.role,
        )
        with suppress(IntegrityError):
            uow.add(user)
            await uow.flush((user,))
            await uow.commit()

    yield
    await container.close()


app = FastAPI(lifespan=lifespan)

include_exception_handlers(app)
include_routers(app)
include_middlewares(app)

setup_dishka(container=get_async_container(), app=app)


def setup_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def main(_args: list[str] | None) -> None:
    setup_logging()

    uvicorn.run(
        "backend.bootstrap.entrypoint.fastapi:app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
        proxy_headers=True,
    )


def run_api(argv: list[str] | None = None) -> None:
    main(argv)


if __name__ == "__main__":
    run_api(sys.argv)
