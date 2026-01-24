from datetime import UTC, datetime

from adaptix import NameStyle, Retort, as_sentinel, dumper, loader, name_mapping
from pydantic import EmailStr

from backend.infrastructure.serialization.base import FieldSkip

api_dump_serializer = Retort(
    recipe=[
        dumper(datetime, lambda x: x.strftime("%Y-%m-%dT%H:%M:%SZ")),
        dumper(EmailStr, str),
        name_mapping(name_style=NameStyle.CAMEL),
        name_mapping(omit_default=True),
        as_sentinel(FieldSkip),
    ],
)

api_load_serializer = Retort(
    recipe=[
        loader(datetime, lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ").astimezone(tz=UTC)),
        name_mapping(name_style=NameStyle.CAMEL),
    ],
)
