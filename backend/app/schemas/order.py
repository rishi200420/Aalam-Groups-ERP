from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import SchemaBase
from app.schemas.product import ProductRead

OrderStatus = Literal["pending", "approved", "packed", "dispatched", "delivered", "cancelled"]

# Status transitions a user is allowed to move an order to, keyed by current status.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "pending": {"approved", "cancelled"},
    "approved": {"packed", "cancelled"},
    "packed": {"dispatched", "cancelled"},
    "dispatched": {"delivered"},
    "delivered": set(),
    "cancelled": set(),
}


class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)


class OrderItemRead(SchemaBase):
    id: str
    product_id: str
    product: ProductRead | None = None
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class OrderStatusHistoryRead(SchemaBase):
    id: str
    status: str
    notes: str | None = None
    changed_by: str | None = None
    changed_at: datetime


class OrderCreate(BaseModel):
    outlet_id: str
    distributor_id: str | None = None
    notes: str | None = Field(default=None, max_length=2000)
    items: list[OrderItemCreate] = Field(min_length=1)

    @field_validator("items")
    @classmethod
    def unique_products(cls, items: list[OrderItemCreate]) -> list[OrderItemCreate]:
        seen = set()
        for item in items:
            if item.product_id in seen:
                raise ValueError("Duplicate product in order items")
            seen.add(item.product_id)
        return items


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    notes: str | None = Field(default=None, max_length=2000)


class OrderRead(SchemaBase):
    id: str
    order_number: str
    outlet_id: str
    outlet_name: str
    distributor_id: str | None = None
    distributor_name: str | None = None
    status: str
    subtotal: Decimal
    total_amount: Decimal
    notes: str | None = None
    stock_deducted: bool
    cancelled_reason: str | None = None
    items: list[OrderItemRead] = []
    status_history: list[OrderStatusHistoryRead] = []
    created_at: datetime
    updated_at: datetime


class OrderSummary(SchemaBase):
    total: int
    pending: int
    approved: int
    dispatched_today: int
    delivered_today: int
    revenue_today: Decimal
