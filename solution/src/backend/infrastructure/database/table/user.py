import sqlalchemy as sa
from sqlalchemy.orm import relationship

from backend.domain.entity.user import User
from backend.infrastructure.auth.user import WebUser
from backend.infrastructure.database.registry import mapper_registry

metadata = mapper_registry.metadata

user_table = sa.Table(
    "user",
    metadata,
    sa.Column("user_id", sa.UUID(as_uuid=True), primary_key=True),
)

web_user_table = sa.Table(
    "web_user",
    metadata,
    sa.Column("web_user_id", sa.UUID(as_uuid=True), primary_key=True),
    sa.Column(
        "user_id",
        sa.UUID(as_uuid=True),
        sa.ForeignKey("user.user_id", ondelete="CASCADE"),
        nullable=False,
    ),
)

mapper_registry.map_imperatively(
    User,
    user_table,
)

mapper_registry.map_imperatively(
    WebUser,
    web_user_table,
    properties={
        "user": relationship("User", lazy="selectin"),
    },
)
