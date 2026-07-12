import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.models import Inventory, Product, Warehouse
from app.schemas.auth import UserRead
from app.services.inventory_service import InventoryService


def _build_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_reserve_dispatch_and_return_stock_flow():
    db = _build_session()
    try:
        warehouse = Warehouse(id=uuid.uuid4(), name="Main Warehouse", code="MAIN", is_default=True)
        product = Product(
            id=uuid.uuid4(),
            sku="INV-001",
            name="Test Product",
            brand="TASTIQ",
            unit="pcs",
            mrp=100,
            distributor_price=90,
            stock_quantity=10,
            low_stock_threshold=3,
            warehouse_id=warehouse.id,
        )
        inventory = Inventory(
            id=uuid.uuid4(),
            product_id=product.id,
            warehouse_id=warehouse.id,
            opening_stock=10,
            available_stock=10,
            reserved_stock=0,
            dispatched_stock=0,
            returned_stock=0,
            current_stock=10,
            minimum_stock=3,
            maximum_stock=50,
            purchase_cost=90,
            selling_price=100,
        )
        db.add(warehouse)
        db.add(product)
        db.add(inventory)
        db.commit()

        current_user = UserRead(
            id=str(uuid.uuid4()),
            email="founder@example.com",
            full_name="Founder",
            roles=["founder"],
            is_active=True,
            created_at=None,
            updated_at=None,
        )
        service = InventoryService(db)

        updated_inventory = service.reserve_stock(inventory, 3, current_user, reference="order-001", notes="Reservation")
        assert updated_inventory.available_stock == 7
        assert updated_inventory.reserved_stock == 3

        updated_inventory = service.dispatch_stock(inventory, 2, current_user, reference="dispatch-001", notes="Dispatch")
        assert updated_inventory.current_stock == 8
        assert updated_inventory.dispatched_stock == 2

        updated_inventory = service.return_stock(inventory, 1, current_user, reference="dispatch-001", notes="Returned")
        assert updated_inventory.current_stock == 9
        assert updated_inventory.dispatched_stock == 1
    finally:
        db.close()


def test_transfer_stock_creates_target_inventory_row():
    from app.schemas.inventory import InventoryTransferRequest

    db = _build_session()
    try:
        source_warehouse = Warehouse(id=uuid.uuid4(), name="Main Warehouse", code="MAIN", is_default=True)
        target_warehouse = Warehouse(id=uuid.uuid4(), name="Secondary Warehouse", code="SEC")
        product = Product(
            id=uuid.uuid4(),
            sku="INV-002",
            name="Transfer Product",
            brand="LEMURIA",
            unit="pcs",
            mrp=50,
            distributor_price=40,
            stock_quantity=20,
            low_stock_threshold=5,
            warehouse_id=source_warehouse.id,
        )
        inventory = Inventory(
            id=uuid.uuid4(),
            product_id=product.id,
            warehouse_id=source_warehouse.id,
            opening_stock=20,
            available_stock=20,
            reserved_stock=0,
            dispatched_stock=0,
            returned_stock=0,
            current_stock=20,
            minimum_stock=5,
            maximum_stock=100,
            purchase_cost=40,
            selling_price=50,
        )
        db.add_all([source_warehouse, target_warehouse, product, inventory])
        db.commit()

        current_user = UserRead(
            id=str(uuid.uuid4()),
            email="founder@example.com",
            full_name="Founder",
            roles=["founder"],
            is_active=True,
            created_at=None,
            updated_at=None,
        )
        service = InventoryService(db)

        result = service.transfer_stock(
            inventory.id,
            InventoryTransferRequest(target_warehouse_id=str(target_warehouse.id), quantity=8, notes="Rebalance"),
            current_user,
        )
        assert result.available_stock == 12
        assert result.current_stock == 12

        target_inventory = service.repo.get_by_product_and_warehouse(product.id, target_warehouse.id)
        assert target_inventory is not None
        assert target_inventory.available_stock == 8
        assert target_inventory.current_stock == 8
    finally:
        db.close()
