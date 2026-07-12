from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import Order, OrderItem, OrderStatusHistory, Outlet, Product, Role, User, UserRole
from app.schemas.dashboard import (
    DailyCount,
    DailyRevenue,
    DashboardStats,
    DispatchStats,
    RecentActivityRead,
    RecentOrderRead,
    TopProductRead,
)

DISPATCH_STATUSES = ("approved", "packed")
DELAY_THRESHOLD_HOURS = 48


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def _order_query(self, brand: str | None):
        query = self.db.query(Order)
        if brand and brand != "all":
            matching_order_ids = (
                self.db.query(OrderItem.order_id)
                .join(Product, Product.id == OrderItem.product_id)
                .filter(func.lower(Product.brand) == brand.lower())
                .scalar_subquery()
            )
            query = query.filter(Order.id.in_(matching_order_ids))
        return query

    def _daily_order_counts(self, order_query, start: date, end: date) -> list[DailyCount]:
        day_col = func.date(Order.created_at)
        rows = (
            order_query.filter(day_col >= start.isoformat(), day_col <= end.isoformat())
            .with_entities(day_col.label("day"), func.count(Order.id).label("count"))
            .group_by(day_col)
            .all()
        )
        counts = {str(row.day): row.count for row in rows}
        result = []
        cursor = start
        while cursor <= end:
            result.append(DailyCount(date=cursor, count=counts.get(cursor.isoformat(), 0)))
            cursor += timedelta(days=1)
        return result

    def _daily_revenue(self, order_query, start: date, end: date) -> list[DailyRevenue]:
        day_col = func.date(Order.created_at)
        rows = (
            order_query.filter(Order.status != "cancelled", day_col >= start.isoformat(), day_col <= end.isoformat())
            .with_entities(day_col.label("day"), func.coalesce(func.sum(Order.total_amount), 0).label("revenue"))
            .group_by(day_col)
            .all()
        )
        revenues = {str(row.day): row.revenue for row in rows}
        result = []
        cursor = start
        while cursor <= end:
            result.append(DailyRevenue(date=cursor, revenue=revenues.get(cursor.isoformat(), 0)))
            cursor += timedelta(days=1)
        return result

    def get_stats(self, brand: str | None = None) -> DashboardStats:
        brand_filter = (brand or "all").lower()
        today = date.today()
        month_start = today.replace(day=1)
        now = datetime.now(timezone.utc)

        order_query = self._order_query(brand_filter)

        orders_today = order_query.filter(func.date(Order.created_at) == today.isoformat()).count()

        revenue_today = (
            order_query.filter(Order.status != "cancelled", func.date(Order.created_at) == today.isoformat())
            .with_entities(func.coalesce(func.sum(Order.total_amount), 0))
            .scalar()
            or 0
        )
        revenue_mtd = (
            order_query.filter(Order.status != "cancelled", func.date(Order.created_at) >= month_start.isoformat())
            .with_entities(func.coalesce(func.sum(Order.total_amount), 0))
            .scalar()
            or 0
        )

        pending_orders = order_query.filter(Order.status == "pending").count()
        pending_dispatch = order_query.filter(Order.status.in_(DISPATCH_STATUSES)).count()
        delivered_total = order_query.filter(Order.status == "delivered").count()

        completed_today = order_query.filter(
            Order.status.in_(["dispatched", "delivered"]), func.date(Order.updated_at) == today.isoformat()
        ).count()
        delay_cutoff = now - timedelta(hours=DELAY_THRESHOLD_HOURS)
        delayed = order_query.filter(
            Order.status.in_(DISPATCH_STATUSES), Order.updated_at < delay_cutoff
        ).count()
        dispatch = DispatchStats(pending=pending_dispatch, completed_today=completed_today, delayed=delayed)

        product_query = self.db.query(Product).filter(Product.deleted_at.is_(None))
        if brand_filter != "all":
            product_query = product_query.filter(func.lower(Product.brand) == brand_filter)
        total_products = product_query.count()
        low_stock_products = product_query.filter(
            Product.stock_quantity <= Product.low_stock_threshold, Product.stock_quantity > 0
        ).count()
        out_of_stock_products = product_query.filter(Product.stock_quantity <= 0).count()
        inventory_value = (
            product_query.with_entities(
                func.coalesce(func.sum(Product.stock_quantity * Product.distributor_price), 0)
            ).scalar()
            or 0
        )

        outlet_query = self.db.query(Outlet).filter(Outlet.deleted_at.is_(None))
        if brand_filter != "all":
            # Outlet.brands is a JSON list column; filter in Python since JSON containment
            # syntax differs between SQLite (dev) and Postgres (prod).
            outlets_all = outlet_query.all()
            outlets_all = [o for o in outlets_all if brand_filter.upper() in [b.upper() for b in (o.brands or [])]]
            total_outlets = len(outlets_all)
            active_outlets = len([o for o in outlets_all if o.status == "active"])
        else:
            total_outlets = outlet_query.count()
            active_outlets = outlet_query.filter(Outlet.status == "active").count()

        total_distributors = (
            self.db.query(User)
            .join(UserRole)
            .join(Role)
            .filter(Role.code == "distributor", User.is_active.is_(True))
            .distinct()
            .count()
        )

        recent_orders_rows = (
            order_query.options(
                joinedload(Order.outlet),
                joinedload(Order.distributor),
                joinedload(Order.items).joinedload(OrderItem.product),
            )
            .order_by(Order.created_at.desc())
            .limit(10)
            .all()
        )
        recent_orders = []
        for order in recent_orders_rows:
            brands = sorted({item.product.brand for item in order.items if item.product})
            product_summary = ", ".join(
                f"{item.product.name} x{item.quantity}" for item in order.items[:2] if item.product
            )
            if len(order.items) > 2:
                product_summary += f" +{len(order.items) - 2} more"
            recent_orders.append(
                RecentOrderRead(
                    id=str(order.id),
                    order_number=order.order_number,
                    outlet_name=order.outlet.shop_name if order.outlet else "",
                    distributor_name=order.distributor.full_name if order.distributor else None,
                    brands=brands,
                    product_summary=product_summary or "—",
                    status=order.status,
                    total_amount=order.total_amount,
                    created_at=order.created_at,
                )
            )

        top_products_query = (
            self.db.query(
                OrderItem.product_id,
                func.sum(OrderItem.quantity).label("units_sold"),
                func.sum(OrderItem.line_total).label("revenue"),
            )
            .join(Order, Order.id == OrderItem.order_id)
            .join(Product, Product.id == OrderItem.product_id)
            .filter(Order.status != "cancelled")
        )
        if brand_filter != "all":
            top_products_query = top_products_query.filter(func.lower(Product.brand) == brand_filter)
        top_products_rows = (
            top_products_query.group_by(OrderItem.product_id)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(5)
            .all()
        )
        top_products = []
        for product_id, units_sold, revenue in top_products_rows:
            product = self.db.query(Product).filter(Product.id == product_id).first()
            if not product:
                continue
            top_products.append(
                TopProductRead(
                    product_id=str(product_id),
                    name=product.name,
                    sku=product.sku,
                    brand=product.brand,
                    units_sold=int(units_sold or 0),
                    revenue=revenue or 0,
                )
            )

        activity_query = self.db.query(OrderStatusHistory).options(joinedload(OrderStatusHistory.order))
        if brand_filter != "all":
            matching_order_ids = (
                self.db.query(OrderItem.order_id)
                .join(Product, Product.id == OrderItem.product_id)
                .filter(func.lower(Product.brand) == brand_filter)
                .scalar_subquery()
            )
            activity_query = activity_query.filter(OrderStatusHistory.order_id.in_(matching_order_ids))
        activity_rows = activity_query.order_by(OrderStatusHistory.changed_at.desc()).limit(10).all()
        activity_labels = {
            "pending": "Order {} created",
            "approved": "Order {} approved",
            "packed": "Order {} packed",
            "dispatched": "Order {} dispatched",
            "delivered": "Order {} delivered",
            "cancelled": "Order {} cancelled",
        }
        recent_activities = [
            RecentActivityRead(
                type=entry.status,
                message=activity_labels.get(entry.status, "Order {} updated").format(
                    entry.order.order_number if entry.order else ""
                ),
                created_at=entry.changed_at,
            )
            for entry in activity_rows
        ]

        orders_last_7_days = self._daily_order_counts(order_query, today - timedelta(days=6), today)
        revenue_last_30_days = self._daily_revenue(order_query, today - timedelta(days=29), today)

        return DashboardStats(
            brand_filter=brand_filter,
            orders_today=orders_today,
            revenue_today=revenue_today,
            revenue_mtd=revenue_mtd,
            pending_orders=pending_orders,
            pending_dispatch=pending_dispatch,
            delivered_orders_total=delivered_total,
            low_stock_products=low_stock_products,
            out_of_stock_products=out_of_stock_products,
            inventory_value=inventory_value,
            total_products=total_products,
            total_outlets=total_outlets,
            active_outlets=active_outlets,
            total_distributors=total_distributors,
            dispatch=dispatch,
            orders_last_7_days=orders_last_7_days,
            revenue_last_30_days=revenue_last_30_days,
            recent_orders=recent_orders,
            top_selling_products=top_products,
            recent_activities=recent_activities,
        )
