from argon2 import PasswordHasher
from backend.infrastructure.auth.idp.token_parser import AccessTokenParser
from backend.infrastructure.auth.idp.web import FastAPITokenParser, WebUserIdProvider
from dishka import AnyOf, Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.common.storage import IStorageClient
from backend.application.common.uow import UoW
from backend.infrastructure.auth.hasher import ArgonHasher, Hasher
from backend.infrastructure.auth.idp.token_processor import AccessTokenProcessor
from backend.infrastructure.config_loader import JWTConfig, RedisConfig
from backend.infrastructure.database.provider import get_async_engine, get_async_session, get_async_sessionmaker
from backend.infrastructure.redis import RedisClient
from backend.application.common.idp import UserIdProvider

class AdapterProvider(Provider):
    hasher = provide(ArgonHasher, scope=Scope.APP, provides=Hasher)
    token_parser = provide(FastAPITokenParser, provides=AccessTokenParser, scope=Scope.REQUEST)
    idp = provide(
        WebUserIdProvider,
        provides=UserIdProvider,
        scope=Scope.REQUEST,
    )
    
    @provide(scope=Scope.APP)
    def argon(self) -> PasswordHasher:
        return PasswordHasher()

    @provide(scope=Scope.APP)
    def token_processor(self, config: JWTConfig) -> AccessTokenProcessor:
        return AccessTokenProcessor(config.secret_key)

    @provide(scope=Scope.APP, provides=AnyOf[IStorageClient, RedisClient])
    def redis_client(self, config: RedisConfig) -> RedisClient:
        return RedisClient(config=config)


def adapter_provider() -> AdapterProvider:
    provider = AdapterProvider()
    provider.provide(get_async_engine, scope=Scope.APP)
    provider.provide(get_async_sessionmaker, scope=Scope.APP)
    provider.provide(get_async_session, provides=AnyOf[AsyncSession, UoW], scope=Scope.REQUEST)

    return provider
