import logging
import sys
from collections.abc import AsyncIterator

import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from backend.bootstrap.di.container import get_async_container
from backend.presentation.web.fastapi import include_exception_handlers, include_middlewares, include_routers

app = FastAPI()

include_routers(app)
include_exception_handlers(app)
include_middlewares(app)

setup_dishka(container=get_async_container(), app=app)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await app.state.dishka_container.close()


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
        port=5000,
        log_level="info",
        proxy_headers=True,
    )


def run_api(argv: list[str] | None = None) -> None:
    main(argv)


if __name__ == "__main__":
    run_api(sys.argv)
