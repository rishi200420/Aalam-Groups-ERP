"""Add notifications table.

This revision is intentionally additive so an existing SQLite database can be
upgraded without being recreated.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_notifications"
down_revision: Union[str, None] = "0007_inventory_management"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    def has_index(table_name: str, index_name: str) -> bool:
        return any(index["name"] == index_name for index in inspector.get_indexes(table_name))

    if "notifications" not in tables:
        op.create_table(
            "notifications",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("type", sa.String(30), nullable=False, server_default="system"),
            sa.Column("title", sa.String(200), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("reference_type", sa.String(30), nullable=True),
            sa.Column("reference_id", sa.String(60), nullable=True),
            sa.Column("link", sa.String(255), nullable=True),
            sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        tables.add("notifications")
    if not has_index("notifications", "ix_notifications_user_id"):
        op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    if not has_index("notifications", "ix_notifications_user_id_is_read"):
        op.create_index("ix_notifications_user_id_is_read", "notifications", ["user_id", "is_read"])


def downgrade() -> None:
    op.drop_index("ix_notifications_user_id_is_read", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
