from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import SchemaBase

InventoryStatus = Literal["in_stock", "low_stock", "out_of_stock", "over_stock", "reserved"]
MovementType = Literal[
    "opening_stock",
    "purchase",
    "adjustment",
    "reservation",
    "dispatch",
    "return",
    "damage",
    "manual_correction",
]


class WarehouseBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    code: str = Field(min_length=2, max_length=30)
    address: str | None = Field(default=None, max_length=1000)
    contact_person: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
    is_default: bool = False
    is_active: bool = True


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    code: str | None = Field(default=None, min_length=2, max_length=30)
    address: str | None = Field(default=None, max_length=1000)
    contact_person: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
    is_default: bool | None = None
    is_active: bool | None = None


class WarehouseRead(SchemaBase):
    id: str
    name: str
    code: str
    address: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def _coerce_id(cls, value: object) -> str:
        return str(value)


class InventoryBase(BaseModel):
    product_id: str
    warehouse_id: str
    opening_stock: int = Field(default=0, ge=0)
    available_stock: int = Field(default=0, ge=0)
    reserved_stock: int = Field(default=0, ge=0)
    dispatched_stock: int = Field(default=0, ge=0)
    returned_stock: int = Field(default=0, ge=0)
    current_stock: int = Field(default=0, ge=0)
    minimum_stock: int = Field(default=0, ge=0)
    maximum_stock: int = Field(default=0, ge=0)
    purchase_cost: Decimal = Field(default=0, ge=0, max_digits=10, decimal_places=2)
    selling_price: Decimal = Field(default=0, ge=0, max_digits=10, decimal_places=2)
    notes: str | None = Field(default=None, max_length=1000)


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    warehouse_id: str | None = None
    opening_stock: int | None = Field(default=None, ge=0)
    available_stock: int | None = Field(default=None, ge=0)
    reserved_stock: int | None = Field(default=None, ge=0)
    dispatched_stock: int | None = Field(default=None, ge=0)
    returned_stock: int | None = Field(default=None, ge=0)
    current_stock: int | None = Field(default=None, ge=0)
    minimum_stock: int | None = Field(default=None, ge=0)
    maximum_stock: int | None = Field(default=None, ge=0)
    purchase_cost: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    selling_price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    notes: str | None = Field(default=None, max_length=1000)


class InventoryAdjustRequest(BaseModel):
    quantity: int = Field(description="Positive to add stock, negative to deduct")
    reason: str = Field(min_length=2, max_length=255)
    movement_type: MovementType = "manual_correction"


class InventoryTransferRequest(BaseModel):
    target_warehouse_id: str
    quantity: int = Field(gt=0)
    notes: str | None = Field(default=None, max_length=1000)


class InventoryRead(SchemaBase):
    id: str
    product_id: str
    product_name: str | None = None
    sku: str | None = None
    brand: str | None = None
    category: str | None = None
    warehouse_id: str
    warehouse_name: str | None = None
    opening_stock: int
    available_stock: int
    reserved_stock: int
    dispatched_stock: int
    returned_stock: int
    current_stock: int
    minimum_stock: int
    maximum_stock: int
    purchase_cost: Decimal
    selling_price: Decimal
    inventory_value: Decimal
    status: InventoryStatus
    reorder_quantity: int = 0
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class StockMovementRead(SchemaBase):
    id: str
    inventory_id: str
    product_id: str
    warehouse_id: str
    quantity: int
    movement_type: str
    reference: str | None = None
    created_by: str | None = None
    notes: str | None = None
    created_at: datetime


class InventoryDashboardRead(SchemaBase):
    total_inventory_items: int
    low_stock_items: int
    critical_stock_items: int
    out_of_stock_items: int
    in_stock_items: int
    reserved_stock: int
    inventory_value: Decimal
    warehouses_count: int
    products_in_stock: int
