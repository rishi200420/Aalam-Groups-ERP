import uuid
from datetime import date, datetime, timezone

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models import Order, OrderItem, OrderStatusHistory, Product


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def next_order_number(self) -> str:
        latest = self.db.query(Order).order_by(Order.order_number.desc()).first()
        if not latest:
            return "ORD000001"
        try:
            number = int(latest.order_number.replace("ORD", "")) + 1
        except ValueError:
            number = self.db.query(func.count(Order.id)).scalar() + 1
        return f"ORD{number:06d}"

    def _base_query(self):
        return self.db.query(Order).options(
            joinedload(Order.outlet),
            joinedload(Order.distributor),
            joinedload(Order.items).joinedload(OrderItem.product),
            joinedload(Order.status_history),
        )

    def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        status: str | None,
        outlet_id: uuid.UUID | None,
        distributor_id: uuid.UUID | None,
    ) -> tuple[list[Order], int]:
        query = self._base_query()

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(Order.order_number.ilike(pattern))
        if status:
            query = query.filter(Order.status == status)
        if outlet_id:
            query = query.filter(Order.outlet_id == outlet_id)
        if distributor_id:
            query = query.filter(Order.distributor_id == distributor_id)

        total = query.count()
        rows = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return rows, total

    def get(self, order_id: uuid.UUID) -> Order | None:
        return self._base_query().filter(Order.id == order_id).first()

    def create(self, order: Order) -> Order:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def save(self, order: Order) -> Order:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def add_status_history(self, entry: OrderStatusHistory) -> None:
        self.db.add(entry)
        self.db.commit()

    def get_product_for_update(self, product_id: uuid.UUID) -> Product | None:
        return self.db.query(Product).filter(Product.id == product_id, Product.deleted_at.is_(None)).first()

    def summary(self, *, distributor_id: uuid.UUID | None = None) -> dict:
        query = self.db.query(Order)
        if distributor_id:
            query = query.filter(Order.distributor_id == distributor_id)

        today = date.today().isoformat()
        dispatched_today = query.filter(
            Order.status.in_(["dispatched", "delivered"]),
            func.date(Order.updated_at) == today,
        ).count()
        delivered_today = query.filter(Order.status == "delivered", func.date(Order.updated_at) == today).count()
        revenue_today = (
            query.filter(Order.status != "cancelled", func.date(Order.created_at) == today)
            .with_entities(func.coalesce(func.sum(Order.total_amount), 0))
            .scalar()
        )
        return {
            "total": query.count(),
            "pending": query.filter(Order.status == "pending").count(),
            "approved": query.filter(Order.status == "approved").count(),
            "dispatched_today": dispatched_today,
            "delivered_today": delivered_today,
            "revenue_today": revenue_today or 0,
        }
