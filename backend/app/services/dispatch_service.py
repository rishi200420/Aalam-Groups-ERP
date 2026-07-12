import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models import Dispatch, DispatchItem, DispatchTimeline, Inventory, Order, OrderStatusHistory, Product
from app.repositories.dispatch_repository import DispatchRepository
from app.schemas.auth import UserRead
from app.schemas.dispatch import DispatchCreate, DispatchRead, DispatchStatusUpdate
from app.services.notification_service import NotificationService

DISPATCH_TRANSITIONS = {
    "ready": {"dispatched", "failed", "returned"},
    "dispatched": {"in_transit", "failed", "returned"},
    "in_transit": {"delivered", "failed", "returned"},
    "delivered": set(),
    "failed": set(),
    "returned": set(),
}


class DispatchService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DispatchRepository(db)

    @staticmethod
    def validate_transition(current_status: str, new_status: str) -> bool:
        return new_status in DISPATCH_TRANSITIONS.get(current_status, set())

    def _is_founder(self, user: UserRead) -> bool:
        return "founder" in user.roles or "super_admin" in user.roles

    def _is_distributor(self, user: UserRead) -> bool:
        return "distributor" in user.roles

    def _serialize(self, dispatch: Dispatch) -> DispatchRead:
        from app.schemas.dispatch import DispatchItemRead, DispatchTimelineRead
        from app.schemas.product import ProductRead

        def _product_read(product: Product | None) -> ProductRead | None:
            if not product:
                return None
            return ProductRead(
                id=str(product.id),
                sku=product.sku,
                barcode=product.barcode,
                name=product.name,
                description=product.description,
                category_id=str(product.category_id) if product.category_id else None,
                category=None,
                brand=product.brand,
                unit=product.unit,
                mrp=product.mrp,
                distributor_price=product.distributor_price,
                stock_quantity=product.stock_quantity,
                low_stock_threshold=product.low_stock_threshold,
                is_low_stock=product.stock_quantity <= product.low_stock_threshold,
                status=product.status,
                images=[],
                created_at=product.created_at,
                updated_at=product.updated_at,
            )

        return DispatchRead(
            id=str(dispatch.id),
            dispatch_number=dispatch.dispatch_number,
            order_id=str(dispatch.order_id),
            order_number=dispatch.order.order_number if dispatch.order else None,
            status=dispatch.status,
            tracking_number=dispatch.tracking_number,
            courier_name=dispatch.courier_name,
            notes=dispatch.notes,
            items=[
                DispatchItemRead(
                    id=str(item.id),
                    product_id=str(item.product_id),
                    product=_product_read(item.product),
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=item.line_total,
                )
                for item in dispatch.items
            ],
            timelines=[
                DispatchTimelineRead(
                    id=str(entry.id),
                    status=entry.status,
                    notes=entry.notes,
                    changed_by=str(entry.changed_by) if entry.changed_by else None,
                    changed_at=entry.changed_at,
                )
                for entry in sorted(dispatch.timelines, key=lambda item: item.changed_at)
            ],
            created_at=dispatch.created_at,
            updated_at=dispatch.updated_at,
        )

    def _add_timeline(self, dispatch: Dispatch, status: str, user_id: uuid.UUID | None, notes: str | None = None) -> None:
        self.repo.add_timeline(
            DispatchTimeline(
                id=uuid.uuid4(),
                dispatch_id=dispatch.id,
                status=status,
                notes=notes,
                changed_by=user_id,
                changed_at=datetime.now(timezone.utc),
            )
        )

    def _map_order_status(self, dispatch_status: str) -> str:
        mapping = {
            "ready": "approved",
            "dispatched": "dispatched",
            "in_transit": "dispatched",
            "delivered": "delivered",
            "failed": "approved",
            "returned": "approved",
        }
        return mapping.get(dispatch_status, "approved")

    def _update_order_status(self, order: Order, dispatch_status: str) -> None:
        new_status = self._map_order_status(dispatch_status)
        if order.status != new_status:
            order.status = new_status
            self.db.add(order)
            self.db.add(
                OrderStatusHistory(
                    id=uuid.uuid4(),
                    order_id=order.id,
                    status=new_status,
                    notes=f"Dispatch status updated to {dispatch_status}",
                    changed_by=order.updated_by,
                    changed_at=datetime.now(timezone.utc),
                )
            )

    def list_dispatches(self, *, current_user: UserRead) -> list[DispatchRead]:
        if self._is_distributor(current_user) and not self._is_founder(current_user):
            rows = self.repo.list(order_id=None, status=None)
            filtered = [row for row in rows if row.order and str(row.order.distributor_id) == current_user.id]
            return [self._serialize(row) for row in filtered]
        rows = self.repo.list(order_id=None, status=None)
        return [self._serialize(row) for row in rows]

    def get_dispatch(self, dispatch_id: uuid.UUID, current_user: UserRead) -> DispatchRead:
        dispatch = self.repo.get(dispatch_id)
        if not dispatch:
            raise HTTPException(status_code=404, detail="Dispatch not found")
        if self._is_distributor(current_user) and not self._is_founder(current_user):
            if not dispatch.order or str(dispatch.order.distributor_id) != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized to view this dispatch")
        return self._serialize(dispatch)

    def create_dispatch(self, payload: DispatchCreate, current_user: UserRead) -> DispatchRead:
        if self._is_distributor(current_user) and not self._is_founder(current_user):
            raise HTTPException(status_code=403, detail="Only founders can create dispatches")

        order = self.repo.get_order_for_update(uuid.UUID(payload.order_id))
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status != "approved":
            raise HTTPException(status_code=400, detail="Dispatch can only be created from approved orders")
        if order.status == "cancelled":
            raise HTTPException(status_code=400, detail="Cancelled orders cannot be dispatched")

        dispatch = Dispatch(
            id=uuid.uuid4(),
            dispatch_number=self.repo.next_dispatch_number(),
            order_id=order.id,
            status="ready",
            tracking_number=payload.tracking_number,
            courier_name=payload.courier_name,
            notes=payload.notes,
            created_by=uuid.UUID(current_user.id),
            updated_by=uuid.UUID(current_user.id),
        )
        items: list[DispatchItem] = []
        for item_payload in payload.items:
            product = self.repo.get_product_for_update(uuid.UUID(item_payload.product_id))
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item_payload.product_id} not found")
            items.append(
                DispatchItem(
                    id=uuid.uuid4(),
                    dispatch_id=dispatch.id,
                    product_id=product.id,
                    quantity=item_payload.quantity,
                    unit_price=product.distributor_price,
                    line_total=product.distributor_price * item_payload.quantity,
                )
            )
        dispatch.items = items
        self.repo.create(dispatch)
        self._add_timeline(dispatch, "ready", uuid.UUID(current_user.id), "Dispatch created")
        logger.info("Dispatch created: %s", dispatch.dispatch_number)
        return self.get_dispatch(dispatch.id, current_user)

    def update_dispatch(self, dispatch_id: uuid.UUID, payload: DispatchCreate, current_user: UserRead) -> DispatchRead:
        dispatch = self.repo.get(dispatch_id)
        if not dispatch:
            raise HTTPException(status_code=404, detail="Dispatch not found")
        if self._is_distributor(current_user) and not self._is_founder(current_user):
            raise HTTPException(status_code=403, detail="Only founders can update dispatches")
        dispatch.tracking_number = payload.tracking_number
        dispatch.courier_name = payload.courier_name
        dispatch.notes = payload.notes
        dispatch.updated_by = uuid.UUID(current_user.id)
        self.repo.save(dispatch)
        logger.info("Dispatch updated: %s", dispatch.dispatch_number)
        return self.get_dispatch(dispatch.id, current_user)

    def update_status(self, dispatch_id: uuid.UUID, payload: DispatchStatusUpdate, current_user: UserRead) -> DispatchRead:
        dispatch = self.repo.get(dispatch_id)
        if not dispatch:
            raise HTTPException(status_code=404, detail="Dispatch not found")
        if self._is_distributor(current_user) and not self._is_founder(current_user):
            raise HTTPException(status_code=403, detail="Only founders can update dispatch status")
        if not self.validate_transition(dispatch.status, payload.status):
            raise HTTPException(status_code=400, detail=f"Cannot move dispatch from '{dispatch.status}' to '{payload.status}'")
        dispatch.status = payload.status
        dispatch.updated_by = uuid.UUID(current_user.id)
        self.repo.save(dispatch)
        if payload.status == "returned":
            for item in dispatch.items:
                inventory = (
                    self.db.query(Inventory)
                    .filter(Inventory.product_id == item.product_id)
                    .order_by(Inventory.created_at.asc())
                    .first()
                )
                if inventory:
                    inventory.current_stock += item.quantity
                    inventory.dispatched_stock = max(0, inventory.dispatched_stock - item.quantity)
                    inventory.returned_stock += item.quantity
                    inventory.status = "reserved" if inventory.reserved_stock > 0 else "in_stock"
                    self.db.add(inventory)
        if payload.status == "delivered":
            low_stock_alerts: list[Inventory] = []
            for item in dispatch.items:
                inventory = (
                    self.db.query(Inventory)
                    .filter(Inventory.product_id == item.product_id)
                    .order_by(Inventory.created_at.asc())
                    .first()
                )
                if inventory:
                    if inventory.current_stock < item.quantity:
                        raise HTTPException(status_code=400, detail=f"Insufficient stock to deliver {item.product.name if item.product else item.product_id}")
                    inventory.current_stock -= item.quantity
                    inventory.reserved_stock = max(0, inventory.reserved_stock - item.quantity)
                    inventory.dispatched_stock = max(0, inventory.dispatched_stock - item.quantity)
                    inventory.available_stock = max(0, inventory.current_stock - inventory.reserved_stock - inventory.dispatched_stock)
                    inventory.status = "low_stock" if inventory.current_stock <= inventory.minimum_stock and inventory.current_stock > 0 else "out_of_stock" if inventory.current_stock == 0 else "in_stock"
                    self.db.add(inventory)
                    if inventory.status in ("low_stock", "out_of_stock"):
                        low_stock_alerts.append(inventory)
        self._add_timeline(dispatch, payload.status, uuid.UUID(current_user.id), payload.notes)
        self._update_order_status(dispatch.order, payload.status)
        if payload.status in ("delivered", "failed"):
            NotificationService(self.db).notify_role(
                "founder",
                type=f"dispatch_{payload.status}",
                title=f"Dispatch {payload.status}",
                message=f"Dispatch {dispatch.dispatch_number} {payload.status}" + (f": {payload.notes}" if payload.notes else ""),
                reference_type="dispatch",
                reference_id=str(dispatch.id),
                link=f"/dispatch/{dispatch.id}",
            )
        if payload.status == "delivered" and low_stock_alerts:
            notifier = NotificationService(self.db)
            for inventory in low_stock_alerts:
                product_name = inventory.product.name if inventory.product else str(inventory.product_id)
                notifier.notify_role(
                    "founder",
                    type=inventory.status,
                    title="Out of stock" if inventory.status == "out_of_stock" else "Low stock warning",
                    message=f"{product_name} is {inventory.status.replace('_', ' ')} ({inventory.current_stock} units left)",
                    reference_type="inventory",
                    reference_id=str(inventory.id),
                    link=f"/inventory/{inventory.id}",
                )
        logger.info("Dispatch status updated: %s -> %s", dispatch.dispatch_number, payload.status)
        return self.get_dispatch(dispatch.id, current_user)
