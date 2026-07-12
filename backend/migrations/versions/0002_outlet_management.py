"""Create outlet management tables."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_outlet_management"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "outlets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("outlet_id", sa.String(20), nullable=False),
        sa.Column("shop_name", sa.String(200), nullable=False),
        sa.Column("owner_name", sa.String(150), nullable=False),
        sa.Column("phone_number", sa.String(20), nullable=False),
        sa.Column("whatsapp_number", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("gst_number", sa.String(30), nullable=True),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("area", sa.String(120), nullable=False),
        sa.Column("city", sa.String(120), nullable=False),
        sa.Column("district", sa.String(120), nullable=False),
        sa.Column("state", sa.String(120), nullable=False),
        sa.Column("pincode", sa.String(10), nullable=False),
        sa.Column("territory", sa.String(120), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("google_maps_url", sa.Text(), nullable=True),
        sa.Column("business_type", sa.String(50), nullable=False),
        sa.Column("brands", sa.JSON(), nullable=False),
        sa.Column("assigned_distributor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("qr_code_value", sa.String(255), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_outlets_outlet_id", "outlets", ["outlet_id"], unique=True)
    op.create_index("ix_outlets_phone_number", "outlets", ["phone_number"])
    op.create_index("ix_outlets_territory", "outlets", ["territory"])
    op.create_index("ix_outlets_shop_name", "outlets", ["shop_name"])
    op.create_index("ix_outlets_area_city", "outlets", ["area", "city"])
    op.create_index("ix_outlets_status", "outlets", ["status"])
    op.create_index("ix_outlets_assigned_distributor_id", "outlets", ["assigned_distributor_id"])

    op.create_table(
        "outlet_visits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("outlet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("outlets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("visit_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("distributor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("next_follow_up_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_outlet_visits_outlet_id", "outlet_visits", ["outlet_id"])
    op.create_index("ix_outlet_visits_distributor_id", "outlet_visits", ["distributor_id"])
    op.create_index("ix_outlet_visits_visit_date", "outlet_visits", ["visit_date"])

    op.create_table(
        "outlet_photos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("outlet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("outlets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("photo_type", sa.String(30), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_url", sa.Text(), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_outlet_photos_outlet_id", "outlet_photos", ["outlet_id"])
    op.create_index("ix_outlet_photos_photo_type", "outlet_photos", ["photo_type"])

    op.create_table(
        "outlet_contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("outlet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("outlets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("role", sa.String(80), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("whatsapp", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_outlet_contacts_outlet_id", "outlet_contacts", ["outlet_id"])


def downgrade() -> None:
    op.drop_index("ix_outlet_contacts_outlet_id", table_name="outlet_contacts")
    op.drop_table("outlet_contacts")
    op.drop_index("ix_outlet_photos_photo_type", table_name="outlet_photos")
    op.drop_index("ix_outlet_photos_outlet_id", table_name="outlet_photos")
    op.drop_table("outlet_photos")
    op.drop_index("ix_outlet_visits_visit_date", table_name="outlet_visits")
    op.drop_index("ix_outlet_visits_distributor_id", table_name="outlet_visits")
    op.drop_index("ix_outlet_visits_outlet_id", table_name="outlet_visits")
    op.drop_table("outlet_visits")
    op.drop_index("ix_outlets_assigned_distributor_id", table_name="outlets")
    op.drop_index("ix_outlets_status", table_name="outlets")
    op.drop_index("ix_outlets_area_city", table_name="outlets")
    op.drop_index("ix_outlets_shop_name", table_name="outlets")
    op.drop_index("ix_outlets_territory", table_name="outlets")
    op.drop_index("ix_outlets_phone_number", table_name="outlets")
    op.drop_index("ix_outlets_outlet_id", table_name="outlets")
    op.drop_table("outlets")
