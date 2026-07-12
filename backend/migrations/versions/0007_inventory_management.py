"""Add warehouse and inventory management tables.

This revision is intentionally additive so an existing SQLite database can be
upgraded without being recreated. The product-to-warehouse relationship is
introduced here together with the new inventory ledger tables.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_inventory_management"
down_revision: Union[str, None] = "0006_dispatch_management"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    def has_index(table_name: str, index_name: str) -> bool:
        return any(index["name"] == index_name for index in inspector.get_indexes(table_name))

    if "warehouses" not in tables:
        op.create_table(
            "warehouses",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("code", sa.String(30), nullable=False, unique=True),
            sa.Column("address", sa.Text(), nullable=True),
            sa.Column("contact_person", sa.String(120), nullable=True),
            sa.Column("phone", sa.String(30), nullable=True),
            sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("updated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        tables.add("warehouses")
    if not has_index("warehouses", "ix_warehouses_code"):
        op.create_index("ix_warehouses_code", "warehouses", ["code"])

    product_columns = {column["name"] for column in inspector.get_columns("products")}
    if "warehouse_id" not in product_columns:
        with op.batch_alter_table("products") as batch_op:
            batch_op.add_column(
                sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=True)
            )
            batch_op.create_foreign_key("fk_products_warehouse_id_warehouses", "warehouses", ["warehouse_id"], ["id"], ondelete="SET NULL")
        product_columns.add("warehouse_id")
    if not has_index("products", "ix_products_warehouse_id"):
        op.create_index("ix_products_warehouse_id", "products", ["warehouse_id"])

    if "inventories" not in tables:
        op.create_table(
            "inventories",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
            sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False),
            sa.Column("opening_stock", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("available_stock", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("reserved_stock", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("dispatched_stock", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("returned_stock", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("current_stock", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("minimum_stock", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("maximum_stock", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("purchase_cost", sa.Numeric(10, 2), nullable=False, server_default="0"),
            sa.Column("selling_price", sa.Numeric(10, 2), nullable=False, server_default="0"),
            sa.Column("status", sa.String(20), nullable=False, server_default="in_stock"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("updated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        tables.add("inventories")
    if not has_index("inventories", "ix_inventories_product_id"):
        op.create_index("ix_inventories_product_id", "inventories", ["product_id"])
    if not has_index("inventories", "ix_inventories_warehouse_id"):
        op.create_index("ix_inventories_warehouse_id", "inventories", ["warehouse_id"])

    if "stock_movements" not in tables:
        op.create_table(
            "stock_movements",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("inventory_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inventories.id", ondelete="CASCADE"), nullable=False),
            sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
            sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False),
            sa.Column("quantity", sa.Integer(), nullable=False),
            sa.Column("movement_type", sa.String(30), nullable=False),
            sa.Column("reference", sa.String(80), nullable=True),
            sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        tables.add("stock_movements")
    if not has_index("stock_movements", "ix_stock_movements_inventory_id"):
        op.create_index("ix_stock_movements_inventory_id", "stock_movements", ["inventory_id"])
    if not has_index("stock_movements", "ix_stock_movements_reference"):
        op.create_index("ix_stock_movements_reference", "stock_movements", ["reference"])


def downgrade() -> None:
    op.drop_index("ix_stock_movements_reference", table_name="stock_movements")
    op.drop_index("ix_stock_movements_inventory_id", table_name="stock_movements")
    op.drop_table("stock_movements")
    op.drop_index("ix_inventories_warehouse_id", table_name="inventories")
    op.drop_index("ix_inventories_product_id", table_name="inventories")
    op.drop_table("inventories")
    op.drop_index("ix_products_warehouse_id", table_name="products")
    with op.batch_alter_table("products") as batch_op:
        batch_op.drop_column("warehouse_id")
    op.drop_index("ix_warehouses_code", table_name="warehouses")
    op.drop_table("warehouses")