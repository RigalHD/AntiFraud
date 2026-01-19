from __future__ import annotations

import os
from dataclasses import dataclass

from sqlalchemy.engine import URL


def str_to_bool(string: str) -> bool:
    return string.lower() in ("true", "1")


@dataclass(slots=True)
class DataBaseConfig:
    pg_database: str
    pg_username: str
    pg_password: str | None
    pg_port: int = 5432
    pg_host: str = "localhost"
    debug: bool = False

    driver: str = "asyncpg"
    database_system: str = "postgresql"

    def build_connection_str(self) -> str:
        return URL.create(
            drivername=f"{self.database_system}+{self.driver}",
            username=self.pg_username,
            database=self.pg_database,
            password=self.pg_password,
            port=self.pg_port,
            host=self.pg_host,
        ).render_as_string(hide_password=False)


@dataclass(slots=True)
class RedisConfig:
    redis_port: int
    redis_host: str


@dataclass(frozen=True, slots=True)
class MiscConfig:
    dev_mode: bool


@dataclass(frozen=True, slots=True)
class JWTConfig:
    secret_key: str


@dataclass
class Config:
    db: DataBaseConfig
    redis: RedisConfig
    misc: MiscConfig
    jwt: JWTConfig

    @classmethod
    def load_from_environment(cls: type[Config]) -> Config:
        db = DataBaseConfig(
            pg_database=os.environ["DB_NAME"],
            pg_username=os.environ["DB_USER"],
            pg_password=os.environ.get("DB_PASSWORD"),
            pg_port=int(os.environ.get("DB_PORT", "5432")),
            pg_host=os.environ.get("DB_HOST", "localhost"),
            debug=str_to_bool(os.environ.get("DB_DEBUG", "False")),
        )

        redis = RedisConfig(
            redis_host=os.environ["REDIS_HOST"],
            redis_port=int(os.environ["REDIS_PORT"]),
        )

        jwt = JWTConfig(
            secret_key=os.environ["RANDOM_SECRET"],
        )

        misc = MiscConfig(
            dev_mode=str_to_bool(os.environ.get("DEV_MODE", "False")),
        )

        return cls(db=db, redis=redis, misc=misc, jwt=jwt)
