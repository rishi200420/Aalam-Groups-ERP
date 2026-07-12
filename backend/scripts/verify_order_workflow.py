import sys
import uuid
from decimal import Decimal
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.database import SessionLocal
from app.models import Dispatch, Order, OrderItem, Outlet, Product
from app.schemas.auth import UserRead
from app.schemas.order import OrderStatusUpdate
from app.services.order_service import OrderService


def founder_user() -> UserRead:
    return UserRead(
        id=str(uuid.uuid4()),
        email="smoke@example.com",
        full_name="Smoke Test User",
        roles=["founder"],
        primary_role="founder",
        is_active=True,
    )


def make_order(session, outlet, product, order_number: str, quantity: int = 1) -> Order:
    order = Order(
        id=uuid.uuid4(),
        order_number=order_number,
        outlet_id=outlet.id,
        status="pending",
        subtotal=Decimal(str(product.distributor_price)) * quantity,
        total_amount=Decimal(str(product.distributor_price)) * quantity,
    )
    session.add(order)
    session.add(
        OrderItem(
            id=uuid.uuid4(),
            order=order,
            product_id=product.id,
            quantity=quantity,
            unit_price=product.distributor_price,
            line_total=Decimal(str(product.distributor_price)) * quantity,
        )
    )
    session.commit()
    return order


def main() -> None:
    session = SessionLocal()
    service = OrderService(session)
    user = founder_user()
    cleanup_order_ids: list[uuid.UUID] = []
    try:
        outlet = session.query(Outlet).first()
        product = session.query(Product).filter(Product.status == "active").first()
        if not outlet or not product:
            raise RuntimeError("Missing outlet or active product for smoke validation")

        approve_order_number = f"SMOKE{uuid.uuid4().hex[:12].upper()}"
        approve_order = make_order(session, outlet, product, approve_order_number)
        cleanup_order_ids.append(approve_order.id)
        approved = service.update_status(approve_order.id, OrderStatusUpdate(status="approved", notes="smoke approve"), user)
        dispatch = session.query(Dispatch).filter(Dispatch.order_id == approve_order.id).first()
        print("approve:", approved.status, "dispatch:", dispatch.status if dispatch else None)

        cancelled = service.cancel_order(approve_order.id, "smoke cancel", user)
        dispatch_after_cancel = session.query(Dispatch).filter(Dispatch.order_id == approve_order.id).first()
        print("cancel:", cancelled.status, cancelled.cancelled_reason, "dispatch:", dispatch_after_cancel.status if dispatch_after_cancel else None)

        reject_order_number = f"SMOKE{uuid.uuid4().hex[:12].upper()}"
        reject_order = make_order(session, outlet, product, reject_order_number)
        cleanup_order_ids.append(reject_order.id)
        rejected = service.cancel_order(reject_order.id, "smoke reject", user)
        print("reject:", rejected.status, rejected.cancelled_reason)

        for order_id in cleanup_order_ids:
            linked_dispatch = session.query(Dispatch).filter(Dispatch.order_id == order_id).first()
            if linked_dispatch:
                session.delete(linked_dispatch)
            order_row = session.query(Order).filter(Order.id == order_id).first()
            if order_row:
                session.delete(order_row)
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    main()
