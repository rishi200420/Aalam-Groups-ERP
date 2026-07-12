"""Create dispatch management tables."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_dispatch_management"
down_revision: Union[str, None] = "0005_order_management"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dispatches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("dispatch_number", sa.String(20), nullable=False, unique=True),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="ready"),
        sa.Column("tracking_number", sa.String(50), nullable=True),
        sa.Column("courier_name", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_dispatches_order_id", "dispatches", ["order_id"])
    op.create_index("ix_dispatches_status", "dispatches", ["status"])
    op.create_index("ix_dispatches_dispatch_number", "dispatches", ["dispatch_number"])

    op.create_table(
        "dispatch_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("dispatch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("dispatches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("order_items.id"), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("line_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_dispatch_items_dispatch_id", "dispatch_items", ["dispatch_id"])

    op.create_table(
        "dispatch_timelines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("dispatch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("dispatches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_dispatch_timelines_dispatch_id", "dispatch_timelines", ["dispatch_id"])


def downgrade() -> None:
    op.drop_index("ix_dispatch_timelines_dispatch_id", table_name="dispatch_timelines")
    op.drop_table("dispatch_timelines")
    op.drop_index("ix_dispatch_items_dispatch_id", table_name="dispatch_items")
    op.drop_table("dispatch_items")
    op.drop_index("ix_dispatches_dispatch_number", table_name="dispatches")
    op.drop_index("ix_dispatches_status", table_name="dispatches")
    op.drop_index("ix_dispatches_order_id", table_name="dispatches")
    op.drop_table("dispatches")
