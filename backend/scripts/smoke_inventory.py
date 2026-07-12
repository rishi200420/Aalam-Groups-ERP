"""Smoke test the repaired SQLite database and inventory flow."""

import sys
import uuid
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models import Product, Warehouse
from app.schemas.auth import UserRead
from app.schemas.inventory import InventoryCreate
from app.services.inventory_service import InventoryService


def main() -> None:
    with TestClient(app) as client:
        health = client.get("/health")
        health.raise_for_status()
        print("health:", health.json())

    db = SessionLocal()
    warehouse_code = f"SMOKE-{uuid.uuid4().hex[:8]}"
    sku = f"SMOKE-{uuid.uuid4().hex[:8]}"
    try:
        warehouse = Warehouse(
            id=uuid.uuid4(),
            name="Smoke Test Warehouse",
            code=warehouse_code,
            is_default=False,
            is_active=True,
        )
        db.add(warehouse)
        db.flush()

        product = Product(
            id=uuid.uuid4(),
            sku=sku,
            name="Smoke Test Product",
            brand="TASTIQ",
            unit="pcs",
            mrp=10,
            distributor_price=8,
            stock_quantity=0,
            low_stock_threshold=1,
            status="active",
            warehouse_id=warehouse.id,
        )
        db.add(product)
        db.commit()

        current_user = UserRead(
            id=str(uuid.uuid4()),
            email="smoke@example.com",
            full_name="Smoke Test User",
            roles=["founder"],
            primary_role="founder",
            is_active=True,
        )
        service = InventoryService(db)
        created = service.create_inventory(
            InventoryCreate(
                product_id=str(product.id),
                warehouse_id=str(warehouse.id),
                opening_stock=5,
                available_stock=5,
                reserved_stock=0,
                dispatched_stock=0,
                returned_stock=0,
                current_stock=5,
                minimum_stock=2,
                maximum_stock=50,
                purchase_cost=5,
                selling_price=7,
                notes="Smoke test inventory",
            ),
            current_user,
        )
        print("product_id:", product.id)
        print("inventory_id:", created.id)
        print("inventory_status:", created.status)
    finally:
        db.query(Product).filter(Product.sku == sku).delete(synchronize_session=False)
        db.query(Warehouse).filter(Warehouse.code == warehouse_code).delete(synchronize_session=False)
        db.commit()
        db.close()


if __name__ == "__main__":
    main()