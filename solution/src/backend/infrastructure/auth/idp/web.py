from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class WebUserIdProvider(Protocol): ...
