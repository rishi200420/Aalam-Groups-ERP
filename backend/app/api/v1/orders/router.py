import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas.auth import UserRead
from app.schemas.common import APIResponse, MessageResponse, PaginatedResponse
from app.schemas.order import OrderCreate, OrderRead, OrderStatusUpdate, OrderSummary
from app.services.order_service import OrderService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[OrderRead])
async def list_orders(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = None,
    status: str | None = None,
    outlet_id: str | None = None,
    distributor_id: str | None = None,
):
    return OrderService(db).list_orders(
        current_user=current_user,
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        outlet_id=outlet_id,
        distributor_id=distributor_id,
    )


@router.get("/summary", response_model=APIResponse[OrderSummary])
async def order_summary(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Order summary", data=OrderService(db).summary(current_user))


@router.post("", response_model=APIResponse[OrderRead], status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Order created", data=OrderService(db).create_order(payload, current_user))


@router.get("/{order_id}", response_model=APIResponse[OrderRead])
async def get_order(
    order_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Order retrieved", data=OrderService(db).get_order(order_id, current_user))


@router.post("/{order_id}/status", response_model=APIResponse[OrderRead])
async def update_order_status(
    order_id: uuid.UUID,
    payload: OrderStatusUpdate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Order status updated", data=OrderService(db).update_status(order_id, payload, current_user))


@router.post("/{order_id}/approve", response_model=APIResponse[OrderRead])
async def approve_order(
    order_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    payload = OrderStatusUpdate(status="approved", notes="Order approved")
    return APIResponse(success=True, message="Order approved", data=OrderService(db).update_status(order_id, payload, current_user))


@router.post("/{order_id}/reject", response_model=APIResponse[OrderRead])
async def reject_order(
    order_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    reason: str = Query(default="Order rejected"),
):
    return APIResponse(success=True, message="Order rejected", data=OrderService(db).cancel_order(order_id, reason, current_user))


@router.post("/{order_id}/cancel", response_model=APIResponse[OrderRead])
async def cancel_order(
    order_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    reason: str = Query(default="Order cancelled"),
):
    return APIResponse(success=True, message="Order cancelled", data=OrderService(db).cancel_order(order_id, reason, current_user))


@router.post("/{order_id}/assign-distributor", response_model=APIResponse[OrderRead])
async def assign_distributor(
    order_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    distributor_id: str = Query(...),
):
    return APIResponse(success=True, message="Distributor assigned", data=OrderService(db).assign_distributor(order_id, distributor_id, current_user))


@router.delete("/{order_id}", response_model=APIResponse[MessageResponse])
async def delete_order(
    order_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    OrderService(db).delete_order(order_id, current_user)
    return APIResponse(success=True, message="Order deleted", data=MessageResponse(message="Order deleted"))
