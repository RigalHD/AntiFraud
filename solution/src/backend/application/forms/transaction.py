from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Self
from uuid import UUID

from pydantic import Field, model_validator

from backend.application.exception.transaction import MissingLonOrLatError
from backend.application.forms.base import BaseForm
from backend.domain.entity.transaction import MetaDataJSON
from backend.domain.misc_types import TransactionChannel, TransactionStatus


class TransactionLocationForm(BaseForm):
    country: str | None = Field(default=None, pattern=r"^[A-Z]{2}$")
    city: str | None = Field(default=None, max_length=128)
    latitude: Decimal | None = Field(default=None, ge=Decimal("-90.0"), le=Decimal("90.0"))
    longitude: Decimal | None = Field(default=None, ge=Decimal("-180.0"), le=Decimal("180.0"))

    @model_validator(mode="after")
    def check_lat_lon(self) -> Self:
        lat = self.latitude
        lon = self.longitude

        if (lat is None) and (lon is not None):
            raise MissingLonOrLatError(field="location.latitude", issue="Долгота указана, а широта отсутствует")
        if (lon is None) and (lat is not None):
            raise MissingLonOrLatError(field="location.longitude", issue="Широта указана, а долгота отсутствует")

        return self


class TransactionForm(BaseForm):
    user_id: UUID | None = Field(default=None, alias="userId")
    amount: Decimal = Field(ge=Decimal("0.01"), le=Decimal("999999999.99"))
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    merchant_id: str | None = Field(default=None, alias="merchantId", max_length=64)
    merchant_category_code: str | None = Field(default=None, alias="merchantCategoryCode", pattern=r"^\d{4}$")
    timestamp: datetime
    ip_address: str | None = Field(default=None, alias="ipAddress", max_length=64)
    device_id: str | None = Field(default=None, alias="deviceId", max_length=128)
    channel: TransactionChannel | None = Field(default=None)
    location: TransactionLocationForm | None = Field(default=None)
    metadata: MetaDataJSON | None = Field(default=None)


class AdminTransactionForm(BaseForm):
    user_id: UUID = Field(alias="userId")
    amount: Decimal = Field(ge=Decimal("0.01"), le=Decimal("999999999.99"))
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    merchant_id: str | None = Field(default=None, alias="merchantId", max_length=64)
    merchant_category_code: str | None = Field(default=None, alias="merchantCategoryCode", pattern=r"^\d{4}$")
    timestamp: datetime
    ip_address: str | None = Field(default=None, alias="ipAddress", max_length=64)
    device_id: str | None = Field(default=None, alias="deviceId", max_length=128)
    channel: TransactionChannel | None = Field(default=None)
    location: TransactionLocationForm | None = Field(default=None)
    metadata: MetaDataJSON | None = Field(default=None)


class ManyTransactionReadForm(BaseForm):
    page: int = Field(default=0, ge=0)
    size: int = Field(default=20, ge=1, le=100)

    user_id: UUID | None = Field(alias="userId", default=None)

    status: TransactionStatus | None = Field(default=None)
    is_fraud: bool | None = Field(alias="isFraud", default=None)
    from_: datetime = Field(alias="from", default_factory=lambda: datetime.now(tz=UTC) - timedelta(days=90))
    to: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
