import sqlalchemy as sa
from sqlalchemy.orm import relationship

from backend.domain.entity.transaction import Transaction, TransactionLocation
from backend.domain.misc_types import TransactionChannel, TransactionStatus
from backend.infrastructure.database.registry import mapper_registry

metadata = mapper_registry.metadata

transaction_location_table = sa.Table(
    "transaction_location_table",
    metadata,
    sa.Column("id", sa.UUID(as_uuid=True), sa.ForeignKey("transaction_table.id"), primary_key=True),
    sa.Column("country", sa.String(2), nullable=True),
    sa.Column("city", sa.String(128), nullable=True),
    sa.Column("latitude", sa.Numeric(), nullable=True),
    sa.Column("longitude", sa.Numeric(), nullable=True),
)

transaction_table = sa.Table(
    "transaction_table",
    metadata,
    sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
    sa.Column("user_id", sa.UUID(as_uuid=True), sa.ForeignKey("user_table.id"), nullable=False),
    sa.Column("amount", sa.Numeric(scale=2), nullable=False),
    sa.Column("currency", sa.String(3), nullable=False),
    sa.Column("status", sa.Enum(TransactionStatus), nullable=False),
    sa.Column("merchant_id", sa.String(64), nullable=True),
    sa.Column("merchant_category_code", sa.String(4), nullable=True),
    sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    sa.Column("ip_address", sa.String(64), nullable=True),
    sa.Column("device_id", sa.String(128), nullable=True),
    sa.Column("channel", sa.Enum(TransactionChannel), nullable=True),
    sa.Column("is_fraud", sa.Boolean, nullable=False, default=False),
    sa.Column("metadata", sa.JSON, nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)

mapper_registry.map_imperatively(TransactionLocation, transaction_location_table)
mapper_registry.map_imperatively(
    Transaction,
    transaction_table,
    properties={
        "location": relationship(
            TransactionLocation,
            uselist=False,
            cascade="all, delete-orphan",
            lazy="selectin",
        ),
    },
)
