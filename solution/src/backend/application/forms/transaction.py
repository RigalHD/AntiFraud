from datetime import datetime
from decimal import Decimal
from ipaddress import IPv4Address
from typing import Any, Self

from pydantic import Field, model_validator

from backend.application.exception.transaction import MissingLonOrLatError
from backend.application.forms.base import BaseForm
from backend.domain.misc_types import TransactionChannel, TransactionStatus


class TransactionLocationForm(BaseForm):
    country: str | None = Field(default=None, pattern=r"^[A-Z]{2}$")
    city: str | None = Field(default=None, max_length=128)
    latitude: Decimal | None = Field(ge=Decimal("-90.0"), le=Decimal("90.0"))
    longitude: Decimal | None = Field(ge=Decimal("-180.0"), le=Decimal("180.0"))

    @model_validator(mode="after")
    def check_lat_lon(self) -> Self:
        lat = (self.latitude,)
        lon = self.longitude
        if (lat is None) != (lon is None):
            raise MissingLonOrLatError
        return self


class TransactionForm(BaseForm):
    amount: Decimal = Field(ge=Decimal("0.01"), le=Decimal("999999999.99"))
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    status: TransactionStatus
    merchant_id: str = Field(alias="merchantId", max_length=64)
    merchant_category_code: str = Field(pattern=r"^\d{4}$")
    timestamp: datetime
    ip_address: IPv4Address = Field(alias="ipAddress", max_length=64)
    device_id: str = Field(alias="deviceId", max_length=128)
    channel: TransactionChannel
    location: TransactionLocationForm
    metadata: dict[str, Any] = Field(default={})
