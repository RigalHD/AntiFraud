from dataclasses import dataclass
from typing import dataclass_transform


@dataclass_transform(frozen_default=True)
def interactor[ClsT](cls: type[ClsT]) -> type[ClsT]:
    return dataclass(frozen=True, slots=True)(cls)


@dataclass_transform(frozen_default=True)
def data_structure[ClsT](cls: type[ClsT]) -> type[ClsT]:
    return dataclass(frozen=True, slots=True)(cls)
