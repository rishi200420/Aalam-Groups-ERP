import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Dispatch, DispatchItem, DispatchTimeline, Inventory, Order, OrderItem, OrderStatusHistory, Outlet, Product
from app.repositories.order_repository import OrderRepository
from app.repositories.dispatch_repository import DispatchRepository
from app.schemas.auth import UserRead
from app.schemas.common import PaginatedResponse
from app.schemas.order import (
    ALLOWED_TRANSITIONS,
    OrderCreate,
    OrderRead,
    OrderStatusUpdate,
    OrderSummary,
)
from app.services.notification_service import NotificationService


def _is_founder(user: UserRead) -> bool:
    return "founder" in user.roles or "super_admin" in user.roles


def _is_distributor(user: UserRead) -> bool:
    return "distributor" in user.roles


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = OrderRepository(db)

    def _serialize(self, order: Order) -> OrderRead:
        from app.schemas.order import OrderItemRead, OrderStatusHistoryRead
        from app.schemas.product import ProductRead

        def _product_read(product) -> "ProductRead | None":
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

        return OrderRead(
            id=str(order.id),
            order_number=order.order_number,
            outlet_id=str(order.outlet_id),
            outlet_name=order.outlet.shop_name if order.outlet else "",
            distributor_id=str(order.distributor_id) if order.distributor_id else None,
            distributor_name=order.distributor.full_name if order.distributor else None,
            status=order.status,
            subtotal=order.subtotal,
            total_amount=order.total_amount,
            notes=order.notes,
            stock_deducted=order.stock_deducted,
            cancelled_reason=order.cancelled_reason,
            items=[
                OrderItemRead(
                    id=str(item.id),
                    product_id=str(item.product_id),
                    product=_product_read(item.product),
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=item.line_total,
                )
                for item in order.items
            ],
            status_history=[
                OrderStatusHistoryRead(
                    id=str(entry.id),
                    status=entry.status,
                    notes=entry.notes,
                    changed_by=str(entry.changed_by) if entry.changed_by else None,
                    changed_at=entry.changed_at,
                )
                for entry in sorted(order.status_history, key=lambda item: item.changed_at)
            ],
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

    def _add_history(self, order: Order, status: str, user_id: uuid.UUID | None, notes: str | None = None) -> None:
        self.repo.add_status_history(
            OrderStatusHistory(
                id=uuid.uuid4(),
                order_id=order.id,
                status=status,
                notes=notes,
                changed_by=user_id,
                changed_at=datetime.now(timezone.utc),
            )
        )

    def _create_dispatch_for_order(self, order: Order, user_id: uuid.UUID, notes: str | None = None) -> Dispatch:
        existing_dispatch = self.db.query(Dispatch).filter(Dispatch.order_id == order.id).first()
        if existing_dispatch:
            return existing_dispatch

        dispatch_repo = DispatchRepository(self.db)
        dispatch = Dispatch(
            id=uuid.uuid4(),
            dispatch_number=dispatch_repo.next_dispatch_number(),
            order_id=order.id,
            status="ready",
            notes=notes,
            created_by=user_id,
            updated_by=user_id,
        )
        dispatch.items = [
            DispatchItem(
                id=uuid.uuid4(),
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_total=item.line_total,
            )
            for item in order.items
        ]
        dispatch.timelines = [
            DispatchTimeline(
                id=uuid.uuid4(),
                status="ready",
                notes=notes or "Dispatch created automatically from order approval",
                changed_by=user_id,
                changed_at=datetime.now(timezone.utc),
            )
        ]
        self.db.add(dispatch)
        return dispatch

    def list_orders(
        self,
        *,
        current_user: UserRead,
        page: int,
        page_size: int,
        search: str | None,
        status: str | None,
        outlet_id: str | None,
        distributor_id: str | None,
    ) -> PaginatedResponse[OrderRead]:
        effective_distributor_id = uuid.UUID(distributor_id) if distributor_id else None
        if _is_distributor(current_user) and not _is_founder(current_user):
            effective_distributor_id = uuid.UUID(current_user.id)

        rows, total = self.repo.list(
            page=page,
            page_size=page_size,
            search=search,
            status=status,
            outlet_id=uuid.UUID(outlet_id) if outlet_id else None,
            distributor_id=effective_distributor_id,
        )
        total_pages = (total + page_size - 1) // page_size if total else 0
        return PaginatedResponse(
            success=True,
            message="Orders retrieved",
            data=[self._serialize(row) for row in rows],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def get_order(self, order_id: uuid.UUID, current_user: UserRead) -> OrderRead:
        order = self.repo.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if _is_distributor(current_user) and not _is_founder(current_user):
            if order.distributor_id is None or str(order.distributor_id) != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized to view this order")
        return self._serialize(order)

    def create_order(self, payload: OrderCreate, current_user: UserRead) -> OrderRead:
        outlet = self.db.query(Outlet).filter(Outlet.id == uuid.UUID(payload.outlet_id), Outlet.deleted_at.is_(None)).first()
        if not outlet:
            raise HTTPException(status_code=404, detail="Outlet not found")

        distributor_id = None
        if _is_distributor(current_user) and not _is_founder(current_user):
            if outlet.assigned_distributor_id is None or str(outlet.assigned_distributor_id) != current_user.id:
                raise HTTPException(status_code=403, detail="You can only order for outlets assigned to you")
            distributor_id = uuid.UUID(current_user.id)
        elif payload.distributor_id:
            distributor_id = uuid.UUID(payload.distributor_id)
        elif outlet.assigned_distributor_id:
            distributor_id = outlet.assigned_distributor_id

        items: list[OrderItem] = []
        subtotal = 0
        for item_payload in payload.items:
            product = self.repo.get_product_for_update(uuid.UUID(item_payload.product_id))
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item_payload.product_id} not found")
            if product.status != "active":
                raise HTTPException(status_code=400, detail=f"Product {product.name} is not active")
            line_total = product.distributor_price * item_payload.quantity
            subtotal += line_total
            items.append(
                OrderItem(
                    id=uuid.uuid4(),
                    product_id=product.id,
                    quantity=item_payload.quantity,
                    unit_price=product.distributor_price,
                    line_total=line_total,
                )
            )

        user_id = uuid.UUID(current_user.id)
        order = Order(
            id=uuid.uuid4(),
            order_number=self.repo.next_order_number(),
            outlet_id=outlet.id,
            distributor_id=distributor_id,
            status="pending",
            subtotal=subtotal,
            total_amount=subtotal,
            notes=payload.notes,
            stock_deducted=False,
            created_by=user_id,
            updated_by=user_id,
        )
        order.items = items
        self.repo.create(order)
        self._add_history(order, "pending", user_id, "Order created")
        self.repo.save(order)
        NotificationService(self.db).notify_role(
            "founder",
            type="order_created",
            title="New order received",
            message=f"Order {order.order_number} placed by {outlet.shop_name} for ₹{subtotal}",
            reference_type="order",
            reference_id=str(order.id),
            link=f"/orders/{order.id}",
        )
        return self.get_order(order.id, current_user)

    def update_status(self, order_id: uuid.UUID, payload: OrderStatusUpdate, current_user: UserRead) -> OrderRead:
        order = self.repo.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        allowed = ALLOWED_TRANSITIONS.get(order.status, set())
        if payload.status not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot move order from '{order.status}' to '{payload.status}'",
            )

        # Only founders can approve/reject-equivalent (cancel-from-pending) and manage packing/dispatch progression.
        if payload.status == "approved" and not _is_founder(current_user):
            raise HTTPException(status_code=403, detail="Only founders can approve orders")
        if payload.status in ("packed", "dispatched", "delivered") and not (
            _is_founder(current_user) or "warehouse" in current_user.roles or "distributor" in current_user.roles
        ):
            raise HTTPException(status_code=403, detail="Not authorized to update dispatch status")

        user_id = uuid.UUID(current_user.id)

        if payload.status == "approved":
            for item in order.items:
                product = self.repo.get_product_for_update(item.product_id)
                if not product or product.stock_quantity < item.quantity:
                    name = product.name if product else str(item.product_id)
                    raise HTTPException(status_code=400, detail=f"Insufficient stock for {name}")
                inventory = (
                    self.db.query(Inventory)
                    .filter(Inventory.product_id == product.id, Inventory.warehouse_id == (product.warehouse_id or self.db.query(Inventory.warehouse_id).filter(Inventory.product_id == product.id).first()[0] if self.db.query(Inventory.warehouse_id).filter(Inventory.product_id == product.id).first() else None))
                    .first()
                )
                if not inventory:
                    inventory = (
                        self.db.query(Inventory)
                        .filter(Inventory.product_id == product.id)
                        .order_by(Inventory.created_at.asc())
                        .first()
                    )
                if inventory and inventory.available_stock < item.quantity:
                    raise HTTPException(status_code=400, detail=f"Insufficient available stock for {product.name}")
            for item in order.items:
                product = self.repo.get_product_for_update(item.product_id)
                product.stock_quantity -= item.quantity
                self.db.add(product)
                inventory = (
                    self.db.query(Inventory)
                    .filter(Inventory.product_id == product.id)
                    .order_by(Inventory.created_at.asc())
                    .first()
                )
                if inventory:
                    inventory.available_stock -= item.quantity
                    inventory.reserved_stock += item.quantity
                    inventory.current_stock = inventory.available_stock + inventory.reserved_stock + inventory.dispatched_stock
                    inventory.status = "reserved"
                    self.db.add(inventory)
            self._create_dispatch_for_order(order, user_id, notes="Auto-created from approved order")
            order.stock_deducted = True

        if payload.status == "cancelled" and order.stock_deducted:
            for item in order.items:
                product = self.repo.get_product_for_update(item.product_id)
                if product:
                    product.stock_quantity += item.quantity
                    self.db.add(product)
                inventory = (
                    self.db.query(Inventory)
                    .filter(Inventory.product_id == item.product_id)
                    .order_by(Inventory.created_at.asc())
                    .first()
                )
                if inventory:
                    inventory.available_stock += item.quantity
                    inventory.reserved_stock = max(0, inventory.reserved_stock - item.quantity)
                    inventory.current_stock = inventory.available_stock + inventory.reserved_stock + inventory.dispatched_stock
                    inventory.status = "reserved" if inventory.reserved_stock > 0 else "in_stock"
                    self.db.add(inventory)
            dispatch = self.db.query(Dispatch).filter(Dispatch.order_id == order.id).first()
            if dispatch and dispatch.status in ("ready", "dispatched", "in_transit"):
                dispatch.status = "failed"
                dispatch.notes = payload.notes or dispatch.notes
                dispatch.updated_by = user_id
                self.db.add(dispatch)
                self.db.add(
                    DispatchTimeline(
                        id=uuid.uuid4(),
                        dispatch_id=dispatch.id,
                        status="failed",
                        notes=payload.notes or "Order cancelled",
                        changed_by=user_id,
                        changed_at=datetime.now(timezone.utc),
                    )
                )
            order.stock_deducted = False
            order.cancelled_reason = payload.notes

        order.status = payload.status
        order.updated_by = user_id
        self.repo.save(order)
        self._add_history(order, payload.status, user_id, payload.notes)
        if order.distributor_id and payload.status in ("approved", "cancelled", "delivered"):
            status_labels = {"approved": "approved", "cancelled": "cancelled", "delivered": "delivered"}
            NotificationService(self.db).notify_users(
                [order.distributor_id],
                type=f"order_{payload.status}" if payload.status != "delivered" else "order_delivered",
                title=f"Order {status_labels.get(payload.status, payload.status)}",
                message=f"Order {order.order_number} has been {status_labels.get(payload.status, payload.status)}",
                reference_type="order",
                reference_id=str(order.id),
                link=f"/orders/{order.id}",
            )
        return self.get_order(order.id, current_user)

    def cancel_order(self, order_id: uuid.UUID, reason: str | None, current_user: UserRead) -> OrderRead:
        return self.update_status(
            order_id, OrderStatusUpdate(status="cancelled", notes=reason), current_user
        )

    def assign_distributor(self, order_id: uuid.UUID, distributor_id: str, current_user: UserRead) -> OrderRead:
        if not _is_founder(current_user):
            raise HTTPException(status_code=403, detail="Only founders can reassign orders")
        order = self.repo.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status not in ("pending", "approved"):
            raise HTTPException(status_code=400, detail="Cannot reassign an order that has progressed past approval")
        order.distributor_id = uuid.UUID(distributor_id)
        order.updated_by = uuid.UUID(current_user.id)
        self.repo.save(order)
        self._add_history(order, order.status, uuid.UUID(current_user.id), "Distributor reassigned")
        return self.get_order(order.id, current_user)

    def delete_order(self, order_id: uuid.UUID, current_user: UserRead) -> None:
        if not _is_founder(current_user):
            raise HTTPException(status_code=403, detail="Only founders can delete orders")
        order = self.repo.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status not in ("pending", "rejected", "cancelled"):
            raise HTTPException(
                status_code=409,
                detail="Only pending or cancelled orders can be deleted; cancel active orders first",
            )
        self.db.delete(order)
        self.db.commit()

    def summary(self, current_user: UserRead) -> OrderSummary:
        distributor_id = None
        if _is_distributor(current_user) and not _is_founder(current_user):
            distributor_id = uuid.UUID(current_user.id)
        return OrderSummary(**self.repo.summary(distributor_id=distributor_id))
