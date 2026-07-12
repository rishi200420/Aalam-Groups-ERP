from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import SchemaBase
from app.schemas.product import ProductRead

DispatchStatus = Literal["ready", "dispatched", "in_transit", "delivered", "failed", "returned"]


class DispatchItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)


class DispatchItemRead(SchemaBase):
    id: str
    product_id: str
    product: ProductRead | None = None
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class DispatchTimelineRead(SchemaBase):
    id: str
    status: str
    notes: str | None = None
    changed_by: str | None = None
    changed_at: datetime


class DispatchCreate(BaseModel):
    order_id: str
    tracking_number: str | None = None
    courier_name: str | None = None
    notes: str | None = Field(default=None, max_length=2000)
    items: list[DispatchItemCreate] = Field(min_length=1)


class DispatchStatusUpdate(BaseModel):
    status: DispatchStatus
    notes: str | None = Field(default=None, max_length=2000)


class DispatchRead(SchemaBase):
    id: str
    dispatch_number: str
    order_id: str
    order_number: str | None = None
    status: str
    tracking_number: str | None = None
    courier_name: str | None = None
    notes: str | None = None
    items: list[DispatchItemRead] = []
    timelines: list[DispatchTimelineRead] = []
    created_at: datetime
    updated_at: datetime
