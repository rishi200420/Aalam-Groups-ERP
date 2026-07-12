from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.common import SchemaBase

ReportType = str


class StatusCount(BaseModel):
    status: str
    count: int


class BrandSales(BaseModel):
    brand: str
    orders_count: int
    revenue: Decimal


class DailySales(BaseModel):
    date: date
    orders_count: int
    revenue: Decimal


class SalesReportRead(SchemaBase):
    start_date: date
    end_date: date
    total_orders: int
    total_revenue: Decimal
    average_order_value: Decimal
    by_status: list[StatusCount]
    by_brand: list[BrandSales]
    daily: list[DailySales]


class InventoryReportRow(BaseModel):
    product_name: str
    sku: str
    brand: str | None = None
    warehouse_name: str
    current_stock: int
    reserved_stock: int
    available_stock: int
    minimum_stock: int
    purchase_cost: Decimal
    inventory_value: Decimal
    status: str


class InventoryReportRead(SchemaBase):
    total_items: int
    total_value: Decimal
    low_stock_count: int
    out_of_stock_count: int
    rows: list[InventoryReportRow]


class StockMovementReportRow(BaseModel):
    date: datetime
    product_name: str
    sku: str
    warehouse_name: str
    movement_type: str
    quantity: int
    reference: str | None = None
    notes: str | None = None


class StockMovementReportRead(SchemaBase):
    start_date: date
    end_date: date
    total_movements: int
    rows: list[StockMovementReportRow]


class DispatchReportRow(BaseModel):
    dispatch_number: str
    order_number: str
    outlet_name: str
    status: str
    dispatched_at: datetime
    delivered_at: datetime | None = None
    delivery_hours: float | None = None


class DispatchReportRead(SchemaBase):
    start_date: date
    end_date: date
    total_dispatches: int
    by_status: list[StatusCount]
    average_delivery_hours: float | None = None
    rows: list[DispatchReportRow]


class OrderReportRow(BaseModel):
    order_number: str
    outlet_name: str
    status: str
    total_amount: Decimal
    created_at: datetime


class OrderReportRead(SchemaBase):
    start_date: date
    end_date: date
    total_orders: int
    total_revenue: Decimal
    by_status: list[StatusCount]
    rows: list[OrderReportRow]


class OutletReportRow(BaseModel):
    outlet_name: str
    outlet_id: str
    territory: str
    orders_count: int
    revenue: Decimal
    last_order_at: datetime | None = None


class OutletReportRead(SchemaBase):
    start_date: date
    end_date: date
    rows: list[OutletReportRow]


class WarehouseReportRow(BaseModel):
    warehouse_name: str
    warehouse_code: str
    total_items: int
    total_value: Decimal
    low_stock_count: int
    out_of_stock_count: int


class WarehouseReportRead(SchemaBase):
    rows: list[WarehouseReportRow]


class TopSellingRow(BaseModel):
    product_name: str
    sku: str
    brand: str
    units_sold: int
    revenue: Decimal


class TopSellingRead(SchemaBase):
    start_date: date
    end_date: date
    rows: list[TopSellingRow]


class LowStockReportRow(BaseModel):
    product_name: str
    sku: str
    warehouse_name: str
    current_stock: int
    minimum_stock: int
    reorder_quantity: int
    status: str


class LowStockReportRead(SchemaBase):
    rows: list[LowStockReportRow]


class DeadStockRow(BaseModel):
    product_name: str
    sku: str
    warehouse_name: str
    current_stock: int
    inventory_value: Decimal
    last_movement_at: datetime | None = None
    days_since_movement: int | None = None


class DeadStockRead(SchemaBase):
    threshold_days: int
    rows: list[DeadStockRow]
