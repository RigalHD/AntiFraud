from datetime import datetime

from adaptix import NameStyle, Retort, dumper, name_mapping

serializer = Retort(
    recipe=[
        dumper(datetime, lambda x: f"{x.strftime('%Y-%m-%d')}T{x.strftime('%H:%M:%S')}Z"),
        name_mapping(name_style=NameStyle.CAMEL),
    ],
)
