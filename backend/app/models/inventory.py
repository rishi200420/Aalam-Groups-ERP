import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.warehouse import Warehouse


class Inventory(BaseModel):
    __tablename__ = "inventories"
    __table_args__ = (
        Index("ix_inventories_product_id", "product_id"),
        Index("ix_inventories_warehouse_id", "warehouse_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False
    )
    opening_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    available_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reserved_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dispatched_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    returned_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    minimum_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    maximum_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    purchase_cost: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    selling_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="in_stock", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)

    product: Mapped["Product"] = relationship("Product", back_populates="inventories")
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="inventories")
    movements: Mapped[list["StockMovement"]] = relationship(
        "StockMovement", back_populates="inventory", cascade="all, delete-orphan"
    )


class StockMovement(BaseModel):
    __tablename__ = "stock_movements"
    __table_args__ = (
        Index("ix_stock_movements_inventory_id", "inventory_id"),
        Index("ix_stock_movements_reference", "reference"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    inventory_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("inventories.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    movement_type: Mapped[str] = mapped_column(String(30), nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    inventory: Mapped["Inventory"] = relationship("Inventory", back_populates="movements")


from app.models.product import Product  # noqa: E402
from app.models.user import User  # noqa: E402
