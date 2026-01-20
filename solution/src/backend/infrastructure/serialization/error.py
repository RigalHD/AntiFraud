from datetime import datetime
from enum import Enum

from adaptix import NameStyle, Retort, as_sentinel, dumper, name_mapping


class FieldSkip(Enum):
    SKIP = "SKIP"


error_serializer = Retort(
    recipe=[
        dumper(datetime, lambda x: f"{x.strftime('%Y-%m-%d')}T{x.strftime('%H:%M:%S')}Z"),
        name_mapping(name_style=NameStyle.CAMEL),
        name_mapping(omit_default=True),
        as_sentinel(FieldSkip),
    ],
)
