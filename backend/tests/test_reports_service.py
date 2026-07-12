import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import (
    Dispatch,
    DispatchTimeline,
    Inventory,
    Order,
    OrderItem,
    Outlet,
    Product,
    StockMovement,
    Warehouse,
)
from app.schemas.auth import UserRead
from app.services.reports_service import ReportsService


def _build_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def _founder() -> UserRead:
    return UserRead(
        id=str(uuid.uuid4()),
        email="founder@example.com",
        full_name="Founder",
        roles=["founder"],
        is_active=True,
        created_at=None,
        updated_at=None,
    )


def _seed(db):
    warehouse = Warehouse(id=uuid.uuid4(), name="Main WH", code="MAINWH", is_default=True)
    product = Product(
        id=uuid.uuid4(), sku="RPT-1", name="Choco Bites", brand="TASTIQ", unit="pcs",
        mrp=100, distributor_price=80, stock_quantity=50, low_stock_threshold=10, warehouse_id=warehouse.id,
    )
    low_stock_product = Product(
        id=uuid.uuid4(), sku="RPT-2", name="Mango Fizz", brand="LEMURIA", unit="pcs",
        mrp=60, distributor_price=45, stock_quantity=5, low_stock_threshold=10, warehouse_id=warehouse.id,
    )
    db.add_all([warehouse, product, low_stock_product])
    db.commit()

    inventory = Inventory(
        id=uuid.uuid4(), product_id=product.id, warehouse_id=warehouse.id,
        opening_stock=50, available_stock=50, current_stock=50, minimum_stock=10, maximum_stock=100,
        purchase_cost=60, selling_price=80, status="in_stock",
    )
    low_inventory = Inventory(
        id=uuid.uuid4(), product_id=low_stock_product.id, warehouse_id=warehouse.id,
        opening_stock=5, available_stock=5, current_stock=5, minimum_stock=10, maximum_stock=50,
        purchase_cost=35, selling_price=45, status="low_stock",
    )
    db.add_all([inventory, low_inventory])
    db.commit()

    old_movement = StockMovement(
        id=uuid.uuid4(), inventory_id=low_inventory.id, product_id=low_stock_product.id, warehouse_id=warehouse.id,
        quantity=5, movement_type="purchase", reference="PO-OLD",
    )
    db.add(old_movement)
    db.commit()
    # backdate the movement so it qualifies as dead stock
    old_movement.created_at = datetime.now(timezone.utc) - timedelta(days=90)
    db.add(old_movement)
    db.commit()

    outlet = Outlet(
        id=uuid.uuid4(), outlet_id="OUT-1", shop_name="Test Shop", owner_name="Owner", phone_number="9999999999",
        address="Addr", area="Area", city="City", district="Dist", state="State", pincode="600001",
        territory="North", business_type="retail", brands=["TASTIQ"], status="active", qr_code_value="QR1",
    )
    db.add(outlet)
    db.commit()

    order = Order(id=uuid.uuid4(), order_number="ORD-1", outlet_id=outlet.id, status="delivered", subtotal=160, total_amount=160)
    db.add(order)
    db.commit()
    order_item = OrderItem(id=uuid.uuid4(), order_id=order.id, product_id=product.id, quantity=2, unit_price=80, line_total=160)
    db.add(order_item)
    db.commit()

    dispatch = Dispatch(id=uuid.uuid4(), dispatch_number="DSP-1", order_id=order.id, status="delivered")
    db.add(dispatch)
    db.commit()
    timeline = DispatchTimeline(id=uuid.uuid4(), dispatch_id=dispatch.id, status="delivered", changed_at=datetime.now(timezone.utc))
    db.add(timeline)
    db.commit()

    return {"warehouse": warehouse, "product": product, "low_stock_product": low_stock_product, "outlet": outlet, "order": order}


def test_sales_report_totals_match_seeded_order():
    db = _build_session()
    try:
        _seed(db)
        service = ReportsService(db)
        report = service.sales_report(_founder(), None, None, None)
        assert report.total_orders == 1
        assert float(report.total_revenue) == 160
        assert any(day.orders_count == 1 for day in report.daily)
    finally:
        db.close()


def test_inventory_report_computes_value_and_counts():
    db = _build_session()
    try:
        _seed(db)
        service = ReportsService(db)
        report = service.inventory_report(_founder(), None)
        assert report.total_items == 2
        assert report.low_stock_count == 1
        # 50 units * 60 cost + 5 units * 35 cost = 3175
        assert float(report.total_value) == 3175
    finally:
        db.close()


def test_low_stock_report_flags_only_below_minimum():
    db = _build_session()
    try:
        _seed(db)
        service = ReportsService(db)
        report = service.low_stock_report(_founder(), None)
        assert len(report.rows) == 1
        assert report.rows[0].sku == "RPT-2"
        assert report.rows[0].reorder_quantity > 0
    finally:
        db.close()


def test_dead_stock_report_flags_old_movement_item():
    db = _build_session()
    try:
        _seed(db)
        service = ReportsService(db)
        report = service.dead_stock_report(_founder(), threshold_days=30)
        skus = [row.sku for row in report.rows]
        assert "RPT-2" in skus
        assert "RPT-1" not in skus
    finally:
        db.close()


def test_dispatch_report_counts_delivered_status():
    db = _build_session()
    try:
        _seed(db)
        service = ReportsService(db)
        report = service.dispatch_report(_founder(), None, None, None)
        assert report.total_dispatches == 1
        assert report.by_status[0].status == "delivered"
    finally:
        db.close()
