from datetime import date, datetime
from decimal import Decimal

from app.schemas.common import SchemaBase


class RecentOrderRead(SchemaBase):
    id: str
    order_number: str
    outlet_name: str
    distributor_name: str | None = None
    brands: list[str] = []
    product_summary: str
    status: str
    total_amount: Decimal
    created_at: datetime


class DispatchStats(SchemaBase):
    pending: int
    completed_today: int
    delayed: int


class TopProductRead(SchemaBase):
    product_id: str
    name: str
    sku: str
    brand: str
    units_sold: int
    revenue: Decimal


class RecentActivityRead(SchemaBase):
    type: str
    message: str
    created_at: datetime


class DailyCount(SchemaBase):
    date: date
    count: int


class DailyRevenue(SchemaBase):
    date: date
    revenue: Decimal


class DashboardStats(SchemaBase):
    brand_filter: str
    orders_today: int
    revenue_today: Decimal
    revenue_mtd: Decimal
    pending_orders: int
    pending_dispatch: int
    delivered_orders_total: int
    low_stock_products: int
    out_of_stock_products: int
    inventory_value: Decimal
    total_products: int
    total_outlets: int
    active_outlets: int
    total_distributors: int
    dispatch: DispatchStats
    orders_last_7_days: list[DailyCount]
    revenue_last_30_days: list[DailyRevenue]
    recent_orders: list[RecentOrderRead]
    top_selling_products: list[TopProductRead]
    recent_activities: list[RecentActivityRead]
