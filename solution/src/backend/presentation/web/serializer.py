from datetime import datetime, timedelta

from adaptix import Retort, dumper

serializer = Retort(
    recipe=[
        dumper(datetime, lambda x: f"{x.strftime('%Y-%m-%d')}T{x.strftime('%H:%M:%S')}Z"),
    ],
)
