import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Inventory, Product, StockMovement, Warehouse
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.auth import UserRead
from app.schemas.common import PaginatedResponse
from app.schemas.inventory import InventoryAdjustRequest, InventoryCreate, InventoryDashboardRead, InventoryRead, InventoryTransferRequest, InventoryUpdate, StockMovementRead, WarehouseCreate, WarehouseRead, WarehouseUpdate
from app.services.notification_service import NotificationService


def _is_founder(user: UserRead) -> bool:
    return "founder" in user.roles or "super_admin" in user.roles


def _is_warehouse(user: UserRead) -> bool:
    return "warehouse" in user.roles


class InventoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InventoryRepository(db)

    def _status(self, inventory: Inventory) -> str:
        if inventory.current_stock <= 0:
            return "out_of_stock"
        if inventory.current_stock <= inventory.minimum_stock:
            return "low_stock"
        if inventory.current_stock >= inventory.maximum_stock:
            return "over_stock"
        if inventory.reserved_stock > 0:
            return "reserved"
        return "in_stock"

    def _reorder_quantity(self, inventory: Inventory) -> int:
        if inventory.current_stock <= inventory.minimum_stock:
            target = inventory.maximum_stock if inventory.maximum_stock > inventory.minimum_stock else inventory.minimum_stock * 2
            return max(0, target - inventory.current_stock)
        return 0

    def _serialize(self, inventory: Inventory) -> InventoryRead:
        return InventoryRead(
            id=str(inventory.id),
            product_id=str(inventory.product_id),
            product_name=inventory.product.name if inventory.product else None,
            sku=inventory.product.sku if inventory.product else None,
            brand=inventory.product.brand if inventory.product else None,
            category=inventory.product.category.name if inventory.product and inventory.product.category else None,
            warehouse_id=str(inventory.warehouse_id),
            warehouse_name=inventory.warehouse.name if inventory.warehouse else None,
            opening_stock=inventory.opening_stock,
            available_stock=inventory.available_stock,
            reserved_stock=inventory.reserved_stock,
            dispatched_stock=inventory.dispatched_stock,
            returned_stock=inventory.returned_stock,
            current_stock=inventory.current_stock,
            minimum_stock=inventory.minimum_stock,
            maximum_stock=inventory.maximum_stock,
            purchase_cost=Decimal(str(inventory.purchase_cost)) if inventory.purchase_cost is not None else Decimal("0"),
            selling_price=Decimal(str(inventory.selling_price)) if inventory.selling_price is not None else Decimal("0"),
            inventory_value=Decimal(str(inventory.current_stock)) * Decimal(str(inventory.purchase_cost or 0)),
            status=self._status(inventory),
            reorder_quantity=self._reorder_quantity(inventory),
            notes=inventory.notes,
            created_at=inventory.created_at,
            updated_at=inventory.updated_at,
        )

    def _serialize_movement(self, movement: StockMovement) -> StockMovementRead:
        return StockMovementRead(
            id=str(movement.id),
            inventory_id=str(movement.inventory_id),
            product_id=str(movement.product_id),
            warehouse_id=str(movement.warehouse_id),
            quantity=movement.quantity,
            movement_type=movement.movement_type,
            reference=movement.reference,
            created_by=str(movement.created_by) if movement.created_by else None,
            notes=movement.notes,
            created_at=movement.created_at,
        )

    def _add_movement(
        self,
        inventory: Inventory,
        *,
        quantity: int,
        movement_type: str,
        reference: str | None,
        created_by: uuid.UUID | None,
        notes: str | None,
    ) -> None:
        self.repo.add_movement(
            StockMovement(
                id=uuid.uuid4(),
                inventory_id=inventory.id,
                product_id=inventory.product_id,
                warehouse_id=inventory.warehouse_id,
                quantity=quantity,
                movement_type=movement_type,
                reference=reference,
                created_by=created_by,
                notes=notes,
            )
        )

    def _refresh_status(self, inventory: Inventory) -> None:
        inventory.status = self._status(inventory)
        self.repo.save(inventory)

    def list_inventory(
        self,
        *,
        current_user: UserRead,
        page: int,
        page_size: int,
        search: str | None,
        brand: str | None,
        category_id: str | None,
        warehouse_id: str | None,
        status: str | None,
    ) -> PaginatedResponse[InventoryRead]:
        if not (_is_founder(current_user) or _is_warehouse(current_user)):
            raise HTTPException(status_code=403, detail="Not authorized to view inventory")
        rows, total = self.repo.list(
            page=page,
            page_size=page_size,
            search=search,
            brand=brand,
            category_id=uuid.UUID(category_id) if category_id else None,
            warehouse_id=uuid.UUID(warehouse_id) if warehouse_id else None,
            status=status,
        )
        total_pages = (total + page_size - 1) // page_size if total else 0
        return PaginatedResponse(
            success=True,
            message="Inventory retrieved",
            data=[self._serialize(row) for row in rows],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def get_inventory(self, inventory_id: uuid.UUID, current_user: UserRead) -> InventoryRead:
        if not (_is_founder(current_user) or _is_warehouse(current_user)):
            raise HTTPException(status_code=403, detail="Not authorized to view inventory")
        inventory = self.repo.get(inventory_id)
        if not inventory:
            raise HTTPException(status_code=404, detail="Inventory not found")
        return self._serialize(inventory)

    def create_inventory(self, payload: InventoryCreate, current_user: UserRead) -> InventoryRead:
        if not _is_founder(current_user):
            raise HTTPException(status_code=403, detail="Only founders can create inventory records")
        product = self.db.query(Product).filter(Product.id == uuid.UUID(payload.product_id)).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        warehouse = self.db.query(Warehouse).filter(Warehouse.id == uuid.UUID(payload.warehouse_id)).first()
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        existing = self.repo.get_by_product_and_warehouse(product.id, warehouse.id)
        if existing:
            raise HTTPException(status_code=409, detail="Inventory already exists for this product and warehouse")
        inventory = Inventory(
            id=uuid.uuid4(),
            product_id=product.id,
            warehouse_id=warehouse.id,
            opening_stock=payload.opening_stock,
            available_stock=payload.available_stock,
            reserved_stock=payload.reserved_stock,
            dispatched_stock=payload.dispatched_stock,
            returned_stock=payload.returned_stock,
            current_stock=payload.current_stock,
            minimum_stock=payload.minimum_stock,
            maximum_stock=payload.maximum_stock,
            purchase_cost=payload.purchase_cost,
            selling_price=payload.selling_price,
            notes=payload.notes,
            created_by=uuid.UUID(current_user.id),
            updated_by=uuid.UUID(current_user.id),
        )
        inventory.status = self._status(inventory)
        self.repo.create(inventory)
        self._add_movement(
            inventory,
            quantity=payload.opening_stock,
            movement_type="opening_stock",
            reference="initial",
            created_by=uuid.UUID(current_user.id),
            notes="Initial inventory setup",
        )
        return self.get_inventory(inventory.id, current_user)

    def update_inventory(self, inventory_id: uuid.UUID, payload: InventoryUpdate, current_user: UserRead) -> InventoryRead:
        if not (_is_founder(current_user) or _is_warehouse(current_user)):
            raise HTTPException(status_code=403, detail="Not authorized to update inventory")
        inventory = self.repo.get(inventory_id)
        if not inventory:
            raise HTTPException(status_code=404, detail="Inventory not found")
        update_data = payload.model_dump(exclude_unset=True)
        if "warehouse_id" in update_data and update_data["warehouse_id"]:
            warehouse = self.db.query(Warehouse).filter(Warehouse.id == uuid.UUID(update_data["warehouse_id"])).first()
            if not warehouse:
                raise HTTPException(status_code=404, detail="Warehouse not found")
        for key, value in update_data.items():
            setattr(inventory, key, value)
        inventory.updated_by = uuid.UUID(current_user.id)
        inventory.status = self._status(inventory)
        self.repo.save(inventory)
        return self.get_inventory(inventory.id, current_user)

    def _maybe_notify_low_stock(self, inventory: Inventory) -> None:
        if inventory.status not in ("low_stock", "out_of_stock"):
            return
        product_name = inventory.product.name if inventory.product else str(inventory.product_id)
        warehouse_name = inventory.warehouse.name if inventory.warehouse else str(inventory.warehouse_id)
        NotificationService(self.db).notify_role(
            "founder",
            type=inventory.status,
            title="Out of stock" if inventory.status == "out_of_stock" else "Low stock warning",
            message=f"{product_name} at {warehouse_name} is {inventory.status.replace('_', ' ')} ({inventory.current_stock} units left)",
            reference_type="inventory",
            reference_id=str(inventory.id),
            link=f"/inventory/{inventory.id}",
        )

    def adjust_inventory(self, inventory_id: uuid.UUID, payload: InventoryAdjustRequest, current_user: UserRead) -> InventoryRead:
        if not (_is_founder(current_user) or _is_warehouse(current_user)):
            raise HTTPException(status_code=403, detail="Not authorized to adjust inventory")
        inventory = self.repo.get(inventory_id)
        if not inventory:
            raise HTTPException(status_code=404, detail="Inventory not found")
        new_quantity = inventory.current_stock + payload.quantity
        if new_quantity < 0:
            raise HTTPException(status_code=400, detail="Stock cannot go below zero")
        inventory.current_stock = new_quantity
        inventory.available_stock = max(0, inventory.available_stock + payload.quantity)
        inventory.updated_by = uuid.UUID(current_user.id)
        inventory.status = self._status(inventory)
        self.repo.save(inventory)
        self._add_movement(
            inventory,
            quantity=payload.quantity,
            movement_type=payload.movement_type,
            reference="manual",
            created_by=uuid.UUID(current_user.id),
            notes=payload.reason,
        )
        self._maybe_notify_low_stock(inventory)
        return self.get_inventory(inventory.id, current_user)

    def reserve_stock(self, inventory: Inventory, quantity: int, current_user: UserRead, *, reference: str | None = None, notes: str | None = None) -> Inventory:
        if quantity < 0:
            raise HTTPException(status_code=400, detail="Reservation quantity must be positive")
        if inventory.available_stock < quantity:
            raise HTTPException(status_code=400, detail="Insufficient available stock")
        inventory.available_stock -= quantity
        inventory.reserved_stock += quantity
        inventory.current_stock = inventory.available_stock + inventory.reserved_stock + inventory.dispatched_stock + inventory.returned_stock
        inventory.updated_by = uuid.UUID(current_user.id)
        inventory.status = self._status(inventory)
        self.repo.save(inventory)
        self._add_movement(inventory, quantity=quantity, movement_type="reservation", reference=reference, created_by=uuid.UUID(current_user.id), notes=notes)
        return inventory

    def dispatch_stock(self, inventory: Inventory, quantity: int, current_user: UserRead, *, reference: str | None = None, notes: str | None = None) -> Inventory:
        if quantity < 0:
            raise HTTPException(status_code=400, detail="Dispatch quantity must be positive")
        if inventory.current_stock < quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock for dispatch")
        inventory.current_stock -= quantity
        inventory.dispatched_stock += quantity
        inventory.available_stock = max(0, inventory.available_stock - quantity)
        inventory.updated_by = uuid.UUID(current_user.id)
        inventory.status = self._status(inventory)
        self.repo.save(inventory)
        self._add_movement(inventory, quantity=quantity, movement_type="dispatch", reference=reference, created_by=uuid.UUID(current_user.id), notes=notes)
        self._maybe_notify_low_stock(inventory)
        return inventory

    def return_stock(self, inventory: Inventory, quantity: int, current_user: UserRead, *, reference: str | None = None, notes: str | None = None) -> Inventory:
        if quantity < 0:
            raise HTTPException(status_code=400, detail="Return quantity must be positive")
        if inventory.dispatched_stock < quantity:
            raise HTTPException(status_code=400, detail="Insufficient dispatched stock")
        inventory.current_stock += quantity
        inventory.dispatched_stock -= quantity
        inventory.returned_stock += quantity
        inventory.updated_by = uuid.UUID(current_user.id)
        inventory.status = self._status(inventory)
        self.repo.save(inventory)
        self._add_movement(inventory, quantity=quantity, movement_type="return", reference=reference, created_by=uuid.UUID(current_user.id), notes=notes)
        return inventory

    def transfer_stock(self, inventory_id: uuid.UUID, payload: InventoryTransferRequest, current_user: UserRead) -> InventoryRead:
        if not (_is_founder(current_user) or _is_warehouse(current_user)):
            raise HTTPException(status_code=403, detail="Not authorized to transfer stock")
        source = self.repo.get(inventory_id)
        if not source:
            raise HTTPException(status_code=404, detail="Inventory not found")
        target_warehouse_id = uuid.UUID(payload.target_warehouse_id)
        if target_warehouse_id == source.warehouse_id:
            raise HTTPException(status_code=400, detail="Target warehouse must be different from source warehouse")
        target_warehouse = self.db.query(Warehouse).filter(Warehouse.id == target_warehouse_id).first()
        if not target_warehouse:
            raise HTTPException(status_code=404, detail="Target warehouse not found")
        if source.available_stock < payload.quantity:
            raise HTTPException(status_code=400, detail="Insufficient available stock for transfer")

        source.available_stock -= payload.quantity
        source.current_stock -= payload.quantity
        source.updated_by = uuid.UUID(current_user.id)
        source.status = self._status(source)
        self.repo.save(source)
        self._add_movement(
            source,
            quantity=payload.quantity,
            movement_type="transfer_out",
            reference=str(target_warehouse.id),
            created_by=uuid.UUID(current_user.id),
            notes=payload.notes,
        )

        target = self.repo.get_by_product_and_warehouse(source.product_id, target_warehouse_id)
        if target:
            target.available_stock += payload.quantity
            target.current_stock += payload.quantity
            target.updated_by = uuid.UUID(current_user.id)
            target.status = self._status(target)
            self.repo.save(target)
        else:
            target = Inventory(
                id=uuid.uuid4(),
                product_id=source.product_id,
                warehouse_id=target_warehouse_id,
                opening_stock=0,
                available_stock=payload.quantity,
                reserved_stock=0,
                dispatched_stock=0,
                returned_stock=0,
                current_stock=payload.quantity,
                minimum_stock=source.minimum_stock,
                maximum_stock=source.maximum_stock,
                purchase_cost=source.purchase_cost,
                selling_price=source.selling_price,
                created_by=uuid.UUID(current_user.id),
                updated_by=uuid.UUID(current_user.id),
            )
            target.status = self._status(target)
            self.repo.create(target)
        self._add_movement(
            target,
            quantity=payload.quantity,
            movement_type="transfer_in",
            reference=str(source.warehouse_id),
            created_by=uuid.UUID(current_user.id),
            notes=payload.notes,
        )
        return self.get_inventory(source.id, current_user)

    def update_warehouse(self, warehouse_id: uuid.UUID, payload: WarehouseUpdate, current_user: UserRead) -> WarehouseRead:
        if not _is_founder(current_user):
            raise HTTPException(status_code=403, detail="Only founders can manage warehouses")
        warehouse = self.repo.get_warehouse(warehouse_id)
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(warehouse, key, value)
        warehouse.updated_by = uuid.UUID(current_user.id)
        self.repo.save_warehouse(warehouse)
        return WarehouseRead.model_validate(warehouse)

    def list_movements(self, *, current_user: UserRead, page: int, page_size: int, inventory_id: str | None = None) -> PaginatedResponse[StockMovementRead]:
        if not (_is_founder(current_user) or _is_warehouse(current_user)):
            raise HTTPException(status_code=403, detail="Not authorized to view stock movements")
        rows, total = self.repo.list_movements(page=page, page_size=page_size, inventory_id=uuid.UUID(inventory_id) if inventory_id else None)
        total_pages = (total + page_size - 1) // page_size if total else 0
        return PaginatedResponse(
            success=True,
            message="Stock movements retrieved",
            data=[self._serialize_movement(row) for row in rows],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def list_warehouses(self, current_user: UserRead) -> list[WarehouseRead]:
        if not (_is_founder(current_user) or _is_warehouse(current_user)):
            raise HTTPException(status_code=403, detail="Not authorized to view warehouses")
        return [WarehouseRead.model_validate(row) for row in self.repo.list_warehouses()]

    def dashboard(self, current_user: UserRead) -> InventoryDashboardRead:
        if not (_is_founder(current_user) or _is_warehouse(current_user)):
            raise HTTPException(status_code=403, detail="Not authorized to view inventory dashboard")
        data = self.repo.dashboard()
        return InventoryDashboardRead(**data)
