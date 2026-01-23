import sqlalchemy as sa

from backend.domain.entity.fraud_rule import FraudRule
from backend.infrastructure.database.registry import mapper_registry

metadata = mapper_registry.metadata

fraud_rule_table = sa.Table(
    "fraud_rule_table",
    metadata,
    sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
    sa.Column("name", sa.String(120), nullable=False, unique=True),
    sa.Column("description", sa.String(500), nullable=False),
    sa.Column("dsl_expression", sa.String(2000), nullable=False),
    sa.Column("priority", sa.Integer, nullable=False),
    sa.Column("enabled", sa.Boolean, nullable=False, default=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
)


mapper_registry.map_imperatively(FraudRule, fraud_rule_table)
