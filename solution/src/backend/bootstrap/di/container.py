from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from backend.bootstrap.di.providers.adapter import adapter_provider
from backend.bootstrap.di.providers.command import CommandProvider
from backend.bootstrap.di.providers.config import ConfigProvider
from backend.bootstrap.di.providers.gateway import GatewayProvider
from backend.bootstrap.di.providers.misc import MiscProvider
from backend.bootstrap.di.providers.parsed_data import ParsedDataProvider


def provider_set() -> list[Provider]:
    return [
        ConfigProvider(),
        FastapiProvider(),
        adapter_provider(),
        CommandProvider(),
        GatewayProvider(),
        MiscProvider(),
        ParsedDataProvider(),
    ]


def get_async_container() -> AsyncContainer:
    return make_async_container(*provider_set())
