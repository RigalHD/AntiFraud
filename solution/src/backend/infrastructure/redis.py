from __future__ import annotations

from dataclasses import dataclass
from types import TracebackType
from typing import Any, Self

from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from backend.application.common.storage import IStorageClient
from backend.infrastructure.config_loader import RedisConfig


@dataclass(slots=True)
class RedisClient(IStorageClient):
    config: RedisConfig
    _connection_pool: ConnectionPool | None = None
    _redis: Redis | None = None

    @property
    def redis(self) -> Redis | None:
        return self._redis

    async def _ensure_connected(self) -> Redis:
        if self._redis is None:
            self._connection_pool = ConnectionPool(
                host=self.config.redis_host,
                port=self.config.redis_port,
            )
            self._redis = Redis(connection_pool=self._connection_pool)
        return self._redis

    async def get(self, key: str) -> str | None:
        redis = await self._ensure_connected()
        result = await redis.get(key)
        if result is None:
            return None
        return str(result.decode("utf-8"))

    async def set(self, key: str, value: Any, expire: int | None = None) -> bool:
        redis = await self._ensure_connected()
        return bool(await redis.set(key, value, ex=expire))

    async def delete(self, key: str) -> bool:
        redis = await self._ensure_connected()
        return int(await redis.delete(key)) > 0

    async def close(self) -> None:
        if self._redis is not None:
            await self._redis.close()
            self._redis = None
        if self._connection_pool is not None:
            await self._connection_pool.disconnect()
            self._connection_pool = None

    async def __aenter__(self) -> Self:
        await self._ensure_connected()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()
