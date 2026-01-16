from datetime import datetime, timedelta

from adaptix import Retort, dumper

serializer = Retort(
    recipe=[
        dumper(datetime, lambda x: x.strftime("%d-%m-%Y %H:%M:%S")),
    ],
)
