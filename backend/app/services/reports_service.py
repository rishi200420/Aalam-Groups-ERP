from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Dispatch,
    Inventory,
    Order,
    OrderItem,
    Outlet,
    Product,
    StockMovement,
    Warehouse,
)
from app.schemas.auth import UserRead
from app.schemas.reports import (
    BrandSales,
    DailySales,
    DeadStockRead,
    DeadStockRow,
    DispatchReportRead,
    DispatchReportRow,
    InventoryReportRead,
    InventoryReportRow,
    LowStockReportRead,
    LowStockReportRow,
    OrderReportRead,
    OrderReportRow,
    OutletReportRead,
    OutletReportRow,
    SalesReportRead,
    StatusCount,
    StockMovementReportRead,
    StockMovementReportRow,
    TopSellingRead,
    TopSellingRow,
    WarehouseReportRead,
    WarehouseReportRow,
)


def _is_founder(user: UserRead) -> bool:
    return "founder" in user.roles or "super_admin" in user.roles


def _default_range(start_date: date | None, end_date: date | None) -> tuple[date, date]:
    end = end_date or date.today()
    start = start_date or (end - timedelta(days=29))
    if start > end:
        raise HTTPException(status_code=400, detail="start_date must be on or before end_date")
    return start, end


class ReportsService:
    def __init__(self, db: Session):
        self.db = db

    def _require_founder(self, current_user: UserRead) -> None:
        if not _is_founder(current_user):
            raise HTTPException(status_code=403, detail="Only founders can view reports")

    def sales_report(self, current_user: UserRead, start_date: date | None, end_date: date | None, brand: str | None) -> SalesReportRead:
        self._require_founder(current_user)
        start, end = _default_range(start_date, end_date)

        base_query = self.db.query(Order).filter(
            func.date(Order.created_at) >= start.isoformat(),
            func.date(Order.created_at) <= end.isoformat(),
        )
        if brand and brand != "all":
            matching_order_ids = (
                self.db.query(OrderItem.order_id)
                .join(Product, Product.id == OrderItem.product_id)
                .filter(func.lower(Product.brand) == brand.lower())
                .scalar_subquery()
            )
            base_query = base_query.filter(Order.id.in_(matching_order_ids))

        revenue_query = base_query.filter(Order.status != "cancelled")
        total_orders = base_query.count()
        total_revenue = revenue_query.with_entities(func.coalesce(func.sum(Order.total_amount), 0)).scalar() or 0
        average_order_value = (Decimal(str(total_revenue)) / total_orders) if total_orders else Decimal("0")

        status_rows = base_query.with_entities(Order.status, func.count(Order.id)).group_by(Order.status).all()
        by_status = [StatusCount(status=status, count=count) for status, count in status_rows]

        brand_rows = (
            self.db.query(Product.brand, func.count(func.distinct(Order.id)), func.coalesce(func.sum(OrderItem.line_total), 0))
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
            .filter(
                Order.status != "cancelled",
                func.date(Order.created_at) >= start.isoformat(),
                func.date(Order.created_at) <= end.isoformat(),
            )
            .group_by(Product.brand)
            .all()
        )
        by_brand = [BrandSales(brand=b, orders_count=count, revenue=revenue or 0) for b, count, revenue in brand_rows]

        day_col = func.date(Order.created_at)
        daily_rows = (
            revenue_query.with_entities(
                day_col.label("day"),
                func.count(Order.id).label("orders_count"),
                func.coalesce(func.sum(Order.total_amount), 0).label("revenue"),
            )
            .group_by(day_col)
            .all()
        )
        daily_map = {str(row.day): (row.orders_count, row.revenue) for row in daily_rows}
        daily: list[DailySales] = []
        cursor = start
        while cursor <= end:
            orders_count, revenue = daily_map.get(cursor.isoformat(), (0, 0))
            daily.append(DailySales(date=cursor, orders_count=orders_count, revenue=revenue or 0))
            cursor += timedelta(days=1)

        return SalesReportRead(
            start_date=start,
            end_date=end,
            total_orders=total_orders,
            total_revenue=total_revenue,
            average_order_value=average_order_value,
            by_status=by_status,
            by_brand=by_brand,
            daily=daily,
        )

    def inventory_report(self, current_user: UserRead, warehouse_id: str | None) -> InventoryReportRead:
        self._require_founder(current_user)
        query = self.db.query(Inventory).options(joinedload(Inventory.product), joinedload(Inventory.warehouse))
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        rows = query.all()

        report_rows = [
            InventoryReportRow(
                product_name=row.product.name if row.product else "Unknown",
                sku=row.product.sku if row.product else "",
                brand=row.product.brand if row.product else None,
                warehouse_name=row.warehouse.name if row.warehouse else "Unknown",
                current_stock=row.current_stock,
                reserved_stock=row.reserved_stock,
                available_stock=row.available_stock,
                minimum_stock=row.minimum_stock,
                purchase_cost=Decimal(str(row.purchase_cost or 0)),
                inventory_value=Decimal(str(row.current_stock)) * Decimal(str(row.purchase_cost or 0)),
                status=row.status,
            )
            for row in rows
        ]
        total_value = sum((r.inventory_value for r in report_rows), Decimal("0"))
        low_stock_count = sum(1 for r in rows if r.current_stock > 0 and r.current_stock <= r.minimum_stock)
        out_of_stock_count = sum(1 for r in rows if r.current_stock <= 0)

        return InventoryReportRead(
            total_items=len(report_rows),
            total_value=total_value,
            low_stock_count=low_stock_count,
            out_of_stock_count=out_of_stock_count,
            rows=report_rows,
        )

    def stock_movement_report(
        self, current_user: UserRead, start_date: date | None, end_date: date | None, warehouse_id: str | None, movement_type: str | None
    ) -> StockMovementReportRead:
        self._require_founder(current_user)
        start, end = _default_range(start_date, end_date)
        query = self.db.query(StockMovement).options(
            joinedload(StockMovement.inventory).joinedload(Inventory.product),
            joinedload(StockMovement.inventory).joinedload(Inventory.warehouse),
        )
        day_col = func.date(StockMovement.created_at)
        query = query.filter(day_col >= start.isoformat(), day_col <= end.isoformat())
        if warehouse_id:
            query = query.filter(StockMovement.warehouse_id == warehouse_id)
        if movement_type:
            query = query.filter(StockMovement.movement_type == movement_type)
        rows = query.order_by(StockMovement.created_at.desc()).limit(500).all()

        report_rows = [
            StockMovementReportRow(
                date=row.created_at,
                product_name=row.inventory.product.name if row.inventory and row.inventory.product else "Unknown",
                sku=row.inventory.product.sku if row.inventory and row.inventory.product else "",
                warehouse_name=row.inventory.warehouse.name if row.inventory and row.inventory.warehouse else "Unknown",
                movement_type=row.movement_type,
                quantity=row.quantity,
                reference=row.reference,
                notes=row.notes,
            )
            for row in rows
        ]
        return StockMovementReportRead(start_date=start, end_date=end, total_movements=len(report_rows), rows=report_rows)

    def dispatch_report(self, current_user: UserRead, start_date: date | None, end_date: date | None, status: str | None) -> DispatchReportRead:
        self._require_founder(current_user)
        start, end = _default_range(start_date, end_date)
        query = self.db.query(Dispatch).options(
            joinedload(Dispatch.order).joinedload(Order.outlet),
            joinedload(Dispatch.timelines),
        )
        day_col = func.date(Dispatch.created_at)
        query = query.filter(day_col >= start.isoformat(), day_col <= end.isoformat())
        if status:
            query = query.filter(Dispatch.status == status)
        rows = query.order_by(Dispatch.created_at.desc()).all()

        status_counts: dict[str, int] = {}
        report_rows = []
        delivery_hours: list[float] = []
        for row in rows:
            status_counts[row.status] = status_counts.get(row.status, 0) + 1
            delivered_entry = next((t for t in sorted(row.timelines, key=lambda t: t.changed_at) if t.status == "delivered"), None)
            delivered_at = delivered_entry.changed_at if delivered_entry else None
            hours = None
            if delivered_at:
                dispatched_at = row.created_at
                if dispatched_at.tzinfo is None:
                    dispatched_at = dispatched_at.replace(tzinfo=timezone.utc)
                delivered_at_aware = delivered_at if delivered_at.tzinfo else delivered_at.replace(tzinfo=timezone.utc)
                hours = round((delivered_at_aware - dispatched_at).total_seconds() / 3600, 1)
                delivery_hours.append(hours)
            report_rows.append(
                DispatchReportRow(
                    dispatch_number=row.dispatch_number,
                    order_number=row.order.order_number if row.order else "",
                    outlet_name=row.order.outlet.shop_name if row.order and row.order.outlet else "",
                    status=row.status,
                    dispatched_at=row.created_at,
                    delivered_at=delivered_at,
                    delivery_hours=hours,
                )
            )

        average_delivery_hours = round(sum(delivery_hours) / len(delivery_hours), 1) if delivery_hours else None
        by_status = [StatusCount(status=k, count=v) for k, v in status_counts.items()]

        return DispatchReportRead(
            start_date=start,
            end_date=end,
            total_dispatches=len(report_rows),
            by_status=by_status,
            average_delivery_hours=average_delivery_hours,
            rows=report_rows,
        )

    def order_report(self, current_user: UserRead, start_date: date | None, end_date: date | None, status: str | None) -> OrderReportRead:
        self._require_founder(current_user)
        start, end = _default_range(start_date, end_date)
        query = self.db.query(Order).options(joinedload(Order.outlet))
        day_col = func.date(Order.created_at)
        query = query.filter(day_col >= start.isoformat(), day_col <= end.isoformat())
        if status:
            query = query.filter(Order.status == status)
        rows = query.order_by(Order.created_at.desc()).all()

        report_rows = [
            OrderReportRow(
                order_number=row.order_number,
                outlet_name=row.outlet.shop_name if row.outlet else "",
                status=row.status,
                total_amount=Decimal(str(row.total_amount or 0)),
                created_at=row.created_at,
            )
            for row in rows
        ]
        status_counts: dict[str, int] = {}
        for row in rows:
            status_counts[row.status] = status_counts.get(row.status, 0) + 1
        total_revenue = sum((Decimal(str(row.total_amount or 0)) for row in rows if row.status != "cancelled"), Decimal("0"))

        return OrderReportRead(
            start_date=start,
            end_date=end,
            total_orders=len(report_rows),
            total_revenue=total_revenue,
            by_status=[StatusCount(status=k, count=v) for k, v in status_counts.items()],
            rows=report_rows,
        )

    def outlet_report(self, current_user: UserRead, start_date: date | None, end_date: date | None) -> OutletReportRead:
        self._require_founder(current_user)
        start, end = _default_range(start_date, end_date)
        day_col = func.date(Order.created_at)
        rows = (
            self.db.query(
                Outlet.id,
                Outlet.shop_name,
                Outlet.outlet_id,
                Outlet.territory,
                func.count(Order.id),
                func.coalesce(func.sum(Order.total_amount), 0),
                func.max(Order.created_at),
            )
            .join(Order, Order.outlet_id == Outlet.id)
            .filter(Order.status != "cancelled", day_col >= start.isoformat(), day_col <= end.isoformat())
            .group_by(Outlet.id)
            .order_by(func.coalesce(func.sum(Order.total_amount), 0).desc())
            .all()
        )
        report_rows = [
            OutletReportRow(
                outlet_name=shop_name,
                outlet_id=outlet_id,
                territory=territory,
                orders_count=orders_count,
                revenue=revenue or 0,
                last_order_at=last_order_at,
            )
            for _, shop_name, outlet_id, territory, orders_count, revenue, last_order_at in rows
        ]
        return OutletReportRead(start_date=start, end_date=end, rows=report_rows)

    def warehouse_report(self, current_user: UserRead) -> WarehouseReportRead:
        self._require_founder(current_user)
        warehouses = self.db.query(Warehouse).order_by(Warehouse.name.asc()).all()
        report_rows = []
        for warehouse in warehouses:
            inventories = self.db.query(Inventory).filter(Inventory.warehouse_id == warehouse.id).all()
            total_value = sum(
                (Decimal(str(inv.current_stock)) * Decimal(str(inv.purchase_cost or 0)) for inv in inventories), Decimal("0")
            )
            low_stock_count = sum(1 for inv in inventories if inv.current_stock > 0 and inv.current_stock <= inv.minimum_stock)
            out_of_stock_count = sum(1 for inv in inventories if inv.current_stock <= 0)
            report_rows.append(
                WarehouseReportRow(
                    warehouse_name=warehouse.name,
                    warehouse_code=warehouse.code,
                    total_items=len(inventories),
                    total_value=total_value,
                    low_stock_count=low_stock_count,
                    out_of_stock_count=out_of_stock_count,
                )
            )
        return WarehouseReportRead(rows=report_rows)

    def top_selling_report(self, current_user: UserRead, start_date: date | None, end_date: date | None, limit: int = 20) -> TopSellingRead:
        self._require_founder(current_user)
        start, end = _default_range(start_date, end_date)
        day_col = func.date(Order.created_at)
        rows = (
            self.db.query(
                Product.id,
                Product.name,
                Product.sku,
                Product.brand,
                func.sum(OrderItem.quantity).label("units_sold"),
                func.sum(OrderItem.line_total).label("revenue"),
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
            .filter(Order.status != "cancelled", day_col >= start.isoformat(), day_col <= end.isoformat())
            .group_by(Product.id)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
            .all()
        )
        report_rows = [
            TopSellingRow(product_name=name, sku=sku, brand=brand, units_sold=int(units_sold or 0), revenue=revenue or 0)
            for _, name, sku, brand, units_sold, revenue in rows
        ]
        return TopSellingRead(start_date=start, end_date=end, rows=report_rows)

    def low_stock_report(self, current_user: UserRead, warehouse_id: str | None) -> LowStockReportRead:
        self._require_founder(current_user)
        query = self.db.query(Inventory).options(joinedload(Inventory.product), joinedload(Inventory.warehouse)).filter(
            Inventory.current_stock <= Inventory.minimum_stock
        )
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        rows = query.all()
        report_rows = []
        for row in rows:
            target = row.maximum_stock if row.maximum_stock > row.minimum_stock else row.minimum_stock * 2
            reorder_quantity = max(0, target - row.current_stock)
            status = "out_of_stock" if row.current_stock <= 0 else "low_stock"
            report_rows.append(
                LowStockReportRow(
                    product_name=row.product.name if row.product else "Unknown",
                    sku=row.product.sku if row.product else "",
                    warehouse_name=row.warehouse.name if row.warehouse else "Unknown",
                    current_stock=row.current_stock,
                    minimum_stock=row.minimum_stock,
                    reorder_quantity=reorder_quantity,
                    status=status,
                )
            )
        return LowStockReportRead(rows=report_rows)

    def dead_stock_report(self, current_user: UserRead, threshold_days: int = 60) -> DeadStockRead:
        self._require_founder(current_user)
        cutoff = datetime.now(timezone.utc) - timedelta(days=threshold_days)
        inventories = (
            self.db.query(Inventory)
            .options(joinedload(Inventory.product), joinedload(Inventory.warehouse))
            .filter(Inventory.current_stock > 0)
            .all()
        )
        report_rows = []
        for inv in inventories:
            last_movement = (
                self.db.query(StockMovement)
                .filter(StockMovement.inventory_id == inv.id)
                .order_by(StockMovement.created_at.desc())
                .first()
            )
            last_movement_at = last_movement.created_at if last_movement else None
            reference_time = last_movement_at or inv.created_at
            reference_time_aware = reference_time if reference_time.tzinfo else reference_time.replace(tzinfo=timezone.utc)
            if reference_time_aware > cutoff:
                continue
            days_since = (datetime.now(timezone.utc) - reference_time_aware).days
            report_rows.append(
                DeadStockRow(
                    product_name=inv.product.name if inv.product else "Unknown",
                    sku=inv.product.sku if inv.product else "",
                    warehouse_name=inv.warehouse.name if inv.warehouse else "Unknown",
                    current_stock=inv.current_stock,
                    inventory_value=Decimal(str(inv.current_stock)) * Decimal(str(inv.purchase_cost or 0)),
                    last_movement_at=last_movement_at,
                    days_since_movement=days_since,
                )
            )
        report_rows.sort(key=lambda r: r.days_since_movement or 0, reverse=True)
        return DeadStockRead(threshold_days=threshold_days, rows=report_rows)

    def export_csv(
        self,
        current_user: UserRead,
        report: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        brand: str | None = None,
        warehouse_id: str | None = None,
        status: str | None = None,
        movement_type: str | None = None,
        threshold_days: int = 60,
    ) -> tuple[str, list[str], list[list[object]]]:
        """Returns (filename, header, rows) for the requested report type."""
        self._require_founder(current_user)

        if report == "sales":
            data = self.sales_report(current_user, start_date, end_date, brand)
            header = ["Date", "Orders", "Revenue"]
            rows = [[d.date.isoformat(), d.orders_count, str(d.revenue)] for d in data.daily]
        elif report == "inventory":
            data = self.inventory_report(current_user, warehouse_id)
            header = ["Product", "SKU", "Brand", "Warehouse", "Current Stock", "Reserved", "Available", "Min Stock", "Purchase Cost", "Inventory Value", "Status"]
            rows = [
                [r.product_name, r.sku, r.brand or "", r.warehouse_name, r.current_stock, r.reserved_stock, r.available_stock, r.minimum_stock, str(r.purchase_cost), str(r.inventory_value), r.status]
                for r in data.rows
            ]
        elif report == "stock-movements":
            data = self.stock_movement_report(current_user, start_date, end_date, warehouse_id, movement_type)
            header = ["Date", "Product", "SKU", "Warehouse", "Movement Type", "Quantity", "Reference", "Notes"]
            rows = [
                [r.date.isoformat(), r.product_name, r.sku, r.warehouse_name, r.movement_type, r.quantity, r.reference or "", r.notes or ""]
                for r in data.rows
            ]
        elif report == "dispatch":
            data = self.dispatch_report(current_user, start_date, end_date, status)
            header = ["Dispatch #", "Order #", "Outlet", "Status", "Dispatched At", "Delivered At", "Delivery Hours"]
            rows = [
                [r.dispatch_number, r.order_number, r.outlet_name, r.status, r.dispatched_at.isoformat(), r.delivered_at.isoformat() if r.delivered_at else "", r.delivery_hours or ""]
                for r in data.rows
            ]
        elif report == "orders":
            data = self.order_report(current_user, start_date, end_date, status)
            header = ["Order #", "Outlet", "Status", "Total Amount", "Created At"]
            rows = [[r.order_number, r.outlet_name, r.status, str(r.total_amount), r.created_at.isoformat()] for r in data.rows]
        elif report == "outlets":
            data = self.outlet_report(current_user, start_date, end_date)
            header = ["Outlet", "Outlet ID", "Territory", "Orders", "Revenue", "Last Order"]
            rows = [
                [r.outlet_name, r.outlet_id, r.territory, r.orders_count, str(r.revenue), r.last_order_at.isoformat() if r.last_order_at else ""]
                for r in data.rows
            ]
        elif report == "warehouses":
            data = self.warehouse_report(current_user)
            header = ["Warehouse", "Code", "Total Items", "Total Value", "Low Stock", "Out of Stock"]
            rows = [[r.warehouse_name, r.warehouse_code, r.total_items, str(r.total_value), r.low_stock_count, r.out_of_stock_count] for r in data.rows]
        elif report == "top-selling":
            data = self.top_selling_report(current_user, start_date, end_date)
            header = ["Product", "SKU", "Brand", "Units Sold", "Revenue"]
            rows = [[r.product_name, r.sku, r.brand, r.units_sold, str(r.revenue)] for r in data.rows]
        elif report == "low-stock":
            data = self.low_stock_report(current_user, warehouse_id)
            header = ["Product", "SKU", "Warehouse", "Current Stock", "Min Stock", "Reorder Qty", "Status"]
            rows = [[r.product_name, r.sku, r.warehouse_name, r.current_stock, r.minimum_stock, r.reorder_quantity, r.status] for r in data.rows]
        elif report == "dead-stock":
            data = self.dead_stock_report(current_user, threshold_days)
            header = ["Product", "SKU", "Warehouse", "Current Stock", "Inventory Value", "Last Movement", "Days Since Movement"]
            rows = [
                [r.product_name, r.sku, r.warehouse_name, r.current_stock, str(r.inventory_value), r.last_movement_at.isoformat() if r.last_movement_at else "", r.days_since_movement or ""]
                for r in data.rows
            ]
        else:
            raise HTTPException(status_code=400, detail=f"Unknown report type: {report}")

        filename = f"{report}-report-{date.today().isoformat()}.csv"
        return filename, header, rows
