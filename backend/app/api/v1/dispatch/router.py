import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas.auth import UserRead
from app.schemas.common import APIResponse
from app.schemas.dispatch import DispatchCreate, DispatchRead, DispatchStatusUpdate
from app.services.dispatch_service import DispatchService

router = APIRouter()


@router.get("", response_model=APIResponse[list[DispatchRead]])
async def list_dispatches(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Dispatches retrieved", data=DispatchService(db).list_dispatches(current_user=current_user))


@router.get("/{dispatch_id}", response_model=APIResponse[DispatchRead])
async def get_dispatch(
    dispatch_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Dispatch retrieved", data=DispatchService(db).get_dispatch(dispatch_id, current_user))


@router.post("", response_model=APIResponse[DispatchRead], status_code=status.HTTP_201_CREATED)
async def create_dispatch(
    payload: DispatchCreate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Dispatch created", data=DispatchService(db).create_dispatch(payload, current_user))


@router.put("/{dispatch_id}", response_model=APIResponse[DispatchRead])
async def update_dispatch(
    dispatch_id: uuid.UUID,
    payload: DispatchCreate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Dispatch updated", data=DispatchService(db).update_dispatch(dispatch_id, payload, current_user))


@router.put("/{dispatch_id}/status", response_model=APIResponse[DispatchRead])
async def update_dispatch_status(
    dispatch_id: uuid.UUID,
    payload: DispatchStatusUpdate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Dispatch status updated", data=DispatchService(db).update_status(dispatch_id, payload, current_user))
