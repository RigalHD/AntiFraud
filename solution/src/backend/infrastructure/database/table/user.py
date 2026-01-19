import sqlalchemy as sa

from backend.domain.entity.user import User
from backend.domain.misc_types import Gender, MaritalStatus, Role
from backend.infrastructure.database.registry import mapper_registry

metadata = mapper_registry.metadata

user_table = sa.Table(
    "user_table",
    metadata,
    sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
    sa.Column("email", sa.String(254), nullable=False, unique=True),
    sa.Column("password", sa.Text, nullable=False),
    sa.Column("full_name", sa.String(200), nullable=False),
    sa.Column("age", sa.Integer, nullable=True),
    sa.Column("region", sa.String(32), nullable=True),
    sa.Column("gender", sa.Enum(Gender), nullable=True),
    sa.Column("marital_status", sa.Enum(MaritalStatus), nullable=True),
    sa.Column("role", sa.Enum(Role), nullable=False),
    sa.Column("is_active", sa.Boolean, nullable=False, default=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
)


mapper_registry.map_imperatively(User, user_table)
