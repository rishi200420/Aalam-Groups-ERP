"""Add system_settings and notification_preferences tables.

Additive migration; existing tables and data are untouched.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009_settings"
down_revision: Union[str, None] = "0008_notifications"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SYSTEM_SETTINGS_ID = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    def has_index(table_name: str, index_name: str) -> bool:
        return any(index["name"] == index_name for index in inspector.get_indexes(table_name))

    if "system_settings" not in tables:
        op.create_table(
            "system_settings",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("business_name", sa.String(200), nullable=False, server_default="Aalam Groups"),
            sa.Column("support_email", sa.String(255), nullable=True),
            sa.Column("support_phone", sa.String(20), nullable=True),
            sa.Column("address", sa.String(500), nullable=True),
            sa.Column("gst_number", sa.String(20), nullable=True),
            sa.Column("default_currency", sa.String(10), nullable=False, server_default="INR"),
            sa.Column("low_stock_default_threshold", sa.Integer(), nullable=False, server_default="10"),
            sa.Column("invoice_footer_note", sa.String(500), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        tables.add("system_settings")
        # Deliberately no seed INSERT here: a raw SQL literal for the fixed id would be
        # stored in whatever text format the driver happens to use (e.g. hyphenated),
        # which can mismatch the app's own UUID column type (compact 32-char hex) and
        # make the row unreachable by SettingsRepository.get_system_settings(). That
        # repository already creates the single row lazily, in the correct format, the
        # first time it's requested -- so we just let it do that instead of seeding here.

    if "notification_preferences" not in tables:
        op.create_table(
            "notification_preferences",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
            sa.Column("notify_orders", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("notify_dispatch", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("notify_stock", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("notify_system", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        tables.add("notification_preferences")
    if not has_index("notification_preferences", "ix_notification_preferences_user_id"):
        op.create_index("ix_notification_preferences_user_id", "notification_preferences", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_notification_preferences_user_id", table_name="notification_preferences")
    op.drop_table("notification_preferences")
    op.drop_table("system_settings")
