import sqlalchemy as sa

from backend.domain.entity.fraud_rule import FraudRule, FraudRuleEvaluationResult
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

fraud_rule_evaluation_result_table = sa.Table(
    "fraud_rule_evaluation_result_table",
    metadata,
    sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
    sa.Column(
        "transaction_id",
        sa.UUID(as_uuid=True),
        sa.ForeignKey("transaction_table.id"),
        nullable=False,
    ),
    sa.Column(
        "rule_id",
        sa.UUID(as_uuid=True),
        sa.ForeignKey("fraud_rule_table.id"),
        nullable=False,
    ),
    sa.Column("rule_name", sa.String(120), nullable=False),
    sa.Column("priority", sa.Integer, nullable=False),
    sa.Column("matched", sa.Boolean, nullable=False),
    sa.Column("description", sa.Text, nullable=False),
)

mapper_registry.map_imperatively(FraudRule, fraud_rule_table)
mapper_registry.map_imperatively(FraudRuleEvaluationResult, fraud_rule_evaluation_result_table)
