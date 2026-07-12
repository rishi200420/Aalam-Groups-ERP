from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import SchemaBase

ProductBrand = Literal["TASTIQ", "LEMURIA"]
ProductStatus = Literal["active", "inactive", "discontinued"]


class CategoryBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    code: str = Field(min_length=2, max_length=30)
    description: str | None = Field(default=None, max_length=1000)
    is_active: bool = True

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().upper().replace(" ", "_")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    code: str | None = Field(default=None, min_length=2, max_length=30)
    description: str | None = Field(default=None, max_length=1000)
    is_active: bool | None = None


class CategoryRead(SchemaBase):
    id: str
    name: str
    code: str
    description: str | None = None
    is_active: bool
    product_count: int = 0
    created_at: datetime
    updated_at: datetime


class ProductImageRead(SchemaBase):
    id: str
    file_name: str
    file_url: str
    content_type: str | None = None
    size_bytes: int | None = None
    is_primary: bool
    created_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def _coerce_id(cls, value: object) -> str:
        return str(value)


class ProductBase(BaseModel):
    sku: str = Field(min_length=2, max_length=40)
    barcode: str | None = Field(default=None, max_length=60)
    name: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=3000)
    category_id: str | None = None
    brand: ProductBrand
    warehouse_id: str | None = None
    unit: str = Field(default="pcs", max_length=20)
    mrp: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    distributor_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock_quantity: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=10, ge=0)
    status: ProductStatus = "active"

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("distributor_price")
    @classmethod
    def price_not_above_mrp(cls, value: Decimal, info) -> Decimal:
        mrp = info.data.get("mrp")
        if mrp is not None and value > mrp:
            raise ValueError("distributor_price cannot exceed mrp")
        return value


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=2, max_length=40)
    barcode: str | None = Field(default=None, max_length=60)
    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=3000)
    category_id: str | None = None
    brand: ProductBrand | None = None
    warehouse_id: str | None = None
    unit: str | None = Field(default=None, max_length=20)
    mrp: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    distributor_price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock_quantity: int | None = Field(default=None, ge=0)
    low_stock_threshold: int | None = Field(default=None, ge=0)
    status: ProductStatus | None = None


class StockAdjustment(BaseModel):
    quantity: int = Field(description="Positive to add stock, negative to deduct")
    reason: str = Field(min_length=2, max_length=255)


class ProductRead(SchemaBase):
    id: str
    sku: str
    barcode: str | None = None
    name: str
    description: str | None = None
    category_id: str | None = None
    category: CategoryRead | None = None
    brand: str
    warehouse_id: str | None = None
    unit: str
    mrp: Decimal
    distributor_price: Decimal
    stock_quantity: int
    low_stock_threshold: int
    is_low_stock: bool
    status: str
    images: list[ProductImageRead] = []
    created_at: datetime
    updated_at: datetime


class ProductSummary(SchemaBase):
    total: int
    active: int
    low_stock: int
    out_of_stock: int
