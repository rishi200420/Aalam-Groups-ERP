import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models import Warehouse
from app.schemas.auth import UserRead
from app.schemas.common import APIResponse, MessageResponse, PaginatedResponse
from app.schemas.inventory import (
    InventoryAdjustRequest,
    InventoryCreate,
    InventoryDashboardRead,
    InventoryRead,
    InventoryTransferRequest,
    InventoryUpdate,
    StockMovementRead,
    WarehouseCreate,
    WarehouseRead,
    WarehouseUpdate,
)
from app.services.inventory_service import InventoryService

router = APIRouter()


@router.get("/status")
async def inventory_module_status():
    return {"module": "inventory", "status": "ready"}


# NOTE: fixed-path routes (dashboard, movements, warehouses) must be declared
# before the "/{inventory_id}" family of routes below, otherwise FastAPI
# matches them against "/{inventory_id}" first and fails UUID validation.


@router.get("/dashboard", response_model=APIResponse[InventoryDashboardRead])
async def inventory_dashboard(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Inventory dashboard retrieved", data=InventoryService(db).dashboard(current_user))


@router.get("/movements", response_model=PaginatedResponse[StockMovementRead])
async def list_stock_movements(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    inventory_id: str | None = None,
):
    return InventoryService(db).list_movements(current_user=current_user, page=page, page_size=page_size, inventory_id=inventory_id)


@router.get("/warehouses", response_model=APIResponse[list[WarehouseRead]])
async def list_warehouses(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Warehouses retrieved", data=InventoryService(db).list_warehouses(current_user))


@router.post("/warehouses", response_model=APIResponse[WarehouseRead], status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    payload: WarehouseCreate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if not ("founder" in current_user.roles or "super_admin" in current_user.roles):
        raise HTTPException(status_code=403, detail="Only founders can manage warehouses")
    warehouse = Warehouse(
        id=uuid.uuid4(),
        name=payload.name,
        code=payload.code,
        address=payload.address,
        contact_person=payload.contact_person,
        phone=payload.phone,
        is_default=payload.is_default,
        is_active=payload.is_active,
        created_by=uuid.UUID(current_user.id),
        updated_by=uuid.UUID(current_user.id),
    )
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return APIResponse(success=True, message="Warehouse created", data=WarehouseRead.model_validate(warehouse))


@router.put("/warehouses/{warehouse_id}", response_model=APIResponse[WarehouseRead])
async def update_warehouse(
    warehouse_id: uuid.UUID,
    payload: WarehouseUpdate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Warehouse updated", data=InventoryService(db).update_warehouse(warehouse_id, payload, current_user))


@router.get("", response_model=PaginatedResponse[InventoryRead])
async def list_inventory(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = None,
    brand: str | None = None,
    category_id: str | None = None,
    warehouse_id: str | None = None,
    status: str | None = None,
):
    return InventoryService(db).list_inventory(
        current_user=current_user,
        page=page,
        page_size=page_size,
        search=search,
        brand=brand,
        category_id=category_id,
        warehouse_id=warehouse_id,
        status=status,
    )


@router.post("", response_model=APIResponse[InventoryRead], status_code=status.HTTP_201_CREATED)
async def create_inventory(
    payload: InventoryCreate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Inventory created", data=InventoryService(db).create_inventory(payload, current_user))


@router.get("/{inventory_id}", response_model=APIResponse[InventoryRead])
async def get_inventory(
    inventory_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Inventory retrieved", data=InventoryService(db).get_inventory(inventory_id, current_user))


@router.put("/{inventory_id}", response_model=APIResponse[InventoryRead])
async def update_inventory(
    inventory_id: uuid.UUID,
    payload: InventoryUpdate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Inventory updated", data=InventoryService(db).update_inventory(inventory_id, payload, current_user))


@router.put("/{inventory_id}/adjust", response_model=APIResponse[InventoryRead])
async def adjust_inventory(
    inventory_id: uuid.UUID,
    payload: InventoryAdjustRequest,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Inventory adjusted", data=InventoryService(db).adjust_inventory(inventory_id, payload, current_user))


@router.put("/{inventory_id}/transfer", response_model=APIResponse[InventoryRead])
async def transfer_inventory(
    inventory_id: uuid.UUID,
    payload: InventoryTransferRequest,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Stock transferred", data=InventoryService(db).transfer_stock(inventory_id, payload, current_user))
