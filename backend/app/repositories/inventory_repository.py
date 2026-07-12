from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models import Inventory, Product, StockMovement, Warehouse


class InventoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        brand: str | None,
        category_id: uuid.UUID | None,
        warehouse_id: uuid.UUID | None,
        status: str | None,
    ) -> tuple[list[Inventory], int]:
        query = (
            self.db.query(Inventory)
            .options(joinedload(Inventory.product), joinedload(Inventory.warehouse))
            .join(Product, Inventory.product_id == Product.id)
        )

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Product.sku.ilike(pattern),
                    Product.name.ilike(pattern),
                    Product.brand.ilike(pattern),
                    Product.barcode.ilike(pattern),
                )
            )
        if brand:
            query = query.filter(Product.brand == brand)
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        if status:
            query = query.filter(Inventory.status == status)

        total = query.count()
        rows = (
            query.order_by(Inventory.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return rows, total

    def get(self, inventory_id: uuid.UUID) -> Inventory | None:
        return (
            self.db.query(Inventory)
            .options(joinedload(Inventory.product), joinedload(Inventory.warehouse), joinedload(Inventory.movements))
            .filter(Inventory.id == inventory_id)
            .first()
        )

    def get_by_product_and_warehouse(self, product_id: uuid.UUID, warehouse_id: uuid.UUID) -> Inventory | None:
        return (
            self.db.query(Inventory)
            .filter(Inventory.product_id == product_id, Inventory.warehouse_id == warehouse_id)
            .first()
        )

    def create(self, inventory: Inventory) -> Inventory:
        self.db.add(inventory)
        self.db.commit()
        self.db.refresh(inventory)
        return inventory

    def save(self, inventory: Inventory) -> Inventory:
        self.db.add(inventory)
        self.db.commit()
        self.db.refresh(inventory)
        return inventory

    def add_movement(self, movement: StockMovement) -> StockMovement:
        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)
        return movement

    def list_movements(self, *, inventory_id: uuid.UUID | None = None, page: int = 1, page_size: int = 20):
        query = self.db.query(StockMovement).options(joinedload(StockMovement.inventory))
        if inventory_id:
            query = query.filter(StockMovement.inventory_id == inventory_id)
        total = query.count()
        rows = query.order_by(StockMovement.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return rows, total

    def list_warehouses(self) -> list[Warehouse]:
        return self.db.query(Warehouse).order_by(Warehouse.name.asc()).all()

    def get_default_warehouse(self) -> Warehouse | None:
        return self.db.query(Warehouse).filter(Warehouse.is_default.is_(True)).first()

    def get_warehouse(self, warehouse_id: uuid.UUID) -> Warehouse | None:
        return self.db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()

    def save_warehouse(self, warehouse: Warehouse) -> Warehouse:
        self.db.add(warehouse)
        self.db.commit()
        self.db.refresh(warehouse)
        return warehouse

    def dashboard(self) -> dict[str, object]:
        inventory_query = self.db.query(Inventory)
        total_items = inventory_query.count()
        low_stock_items = inventory_query.filter(Inventory.current_stock <= Inventory.minimum_stock, Inventory.current_stock > 0).count()
        critical_stock_items = inventory_query.filter(
            Inventory.current_stock > 0,
            Inventory.minimum_stock > 0,
            Inventory.current_stock <= (Inventory.minimum_stock * 0.5),
        ).count()
        out_of_stock_items = inventory_query.filter(Inventory.current_stock <= 0).count()
        in_stock_items = inventory_query.filter(Inventory.current_stock > 0).count()
        reserved_stock = inventory_query.with_entities(func.coalesce(func.sum(Inventory.reserved_stock), 0)).scalar() or 0
        inventory_value = inventory_query.with_entities(func.coalesce(func.sum(Inventory.current_stock * Inventory.purchase_cost), 0)).scalar() or 0
        warehouses_count = self.db.query(Warehouse).count()
        products_in_stock = inventory_query.filter(Inventory.current_stock > 0).with_entities(func.count(func.distinct(Inventory.product_id))).scalar() or 0
        return {
            "total_inventory_items": total_items,
            "low_stock_items": low_stock_items,
            "critical_stock_items": critical_stock_items,
            "out_of_stock_items": out_of_stock_items,
            "in_stock_items": in_stock_items,
            "reserved_stock": reserved_stock,
            "inventory_value": inventory_value,
            "warehouses_count": warehouses_count,
            "products_in_stock": products_in_stock,
        }
