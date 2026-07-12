import uuid
from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import Dispatch, DispatchItem, DispatchTimeline, Order, Product


class DispatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def next_dispatch_number(self) -> str:
        latest = self.db.query(Dispatch).order_by(Dispatch.dispatch_number.desc()).first()
        if not latest:
            return "DSP000001"
        try:
            number = int(latest.dispatch_number.replace("DSP", "")) + 1
        except ValueError:
            number = self.db.query(func.count(Dispatch.id)).scalar() + 1
        return f"DSP{number:06d}"

    def _base_query(self):
        return self.db.query(Dispatch).options(
            joinedload(Dispatch.order),
            joinedload(Dispatch.items).joinedload(DispatchItem.product),
            joinedload(Dispatch.timelines),
        )

    def list(self, *, order_id: uuid.UUID | None = None, status: str | None = None) -> list[Dispatch]:
        query = self._base_query()
        if order_id:
            query = query.filter(Dispatch.order_id == order_id)
        if status:
            query = query.filter(Dispatch.status == status)
        return query.order_by(Dispatch.created_at.desc()).all()

    def get(self, dispatch_id: uuid.UUID) -> Dispatch | None:
        return self._base_query().filter(Dispatch.id == dispatch_id).first()

    def create(self, dispatch: Dispatch) -> Dispatch:
        self.db.add(dispatch)
        self.db.commit()
        self.db.refresh(dispatch)
        return dispatch

    def save(self, dispatch: Dispatch) -> Dispatch:
        self.db.add(dispatch)
        self.db.commit()
        self.db.refresh(dispatch)
        return dispatch

    def add_timeline(self, entry: DispatchTimeline) -> None:
        self.db.add(entry)
        self.db.commit()

    def get_order_for_update(self, order_id: uuid.UUID) -> Order | None:
        return self.db.query(Order).filter(Order.id == order_id).first()

    def get_product_for_update(self, product_id: uuid.UUID) -> Product | None:
        return self.db.query(Product).filter(Product.id == product_id, Product.deleted_at.is_(None)).first()
