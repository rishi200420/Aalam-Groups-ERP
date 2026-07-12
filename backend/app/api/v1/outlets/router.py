import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas.auth import UserRead
from app.schemas.common import APIResponse, MessageResponse, PaginatedResponse
from app.schemas.outlet import OutletCreate, OutletRead, OutletSummary, OutletUpdate, OutletVisitCreate
from app.services.outlet_service import OutletService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[OutletRead])
async def list_outlets(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = None,
    status: str | None = None,
    territory: str | None = None,
    business_type: str | None = None,
):
    return OutletService(db).list_outlets(
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        territory=territory,
        business_type=business_type,
        current_user=current_user,
    )


@router.get("/summary", response_model=APIResponse[OutletSummary])
async def outlet_summary(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Outlet summary", data=OutletService(db).summary(current_user))


@router.post("", response_model=APIResponse[OutletRead], status_code=status.HTTP_201_CREATED)
async def create_outlet(
    payload: OutletCreate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Outlet created", data=OutletService(db).create_outlet(payload, current_user))


@router.get("/{outlet_id}", response_model=APIResponse[OutletRead])
async def get_outlet(
    outlet_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Outlet retrieved", data=OutletService(db).get_outlet(outlet_id, current_user))


@router.patch("/{outlet_id}", response_model=APIResponse[OutletRead])
async def update_outlet(
    outlet_id: uuid.UUID,
    payload: OutletUpdate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Outlet updated", data=OutletService(db).update_outlet(outlet_id, payload, current_user))


@router.delete("/{outlet_id}", response_model=APIResponse[MessageResponse])
async def delete_outlet(
    outlet_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    OutletService(db).delete_outlet(outlet_id, current_user)
    return APIResponse(success=True, message="Outlet deleted", data=MessageResponse(message="Outlet deleted"))


@router.post("/{outlet_id}/visits", response_model=APIResponse[OutletRead], status_code=status.HTTP_201_CREATED)
async def add_visit(
    outlet_id: uuid.UUID,
    payload: OutletVisitCreate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Visit added", data=OutletService(db).add_visit(outlet_id, payload, current_user))


@router.post("/{outlet_id}/photos", response_model=APIResponse[OutletRead], status_code=status.HTTP_201_CREATED)
async def upload_photo(
    outlet_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    photo_type: str = Query(...),
    file: UploadFile = File(...),
):
    return APIResponse(success=True, message="Photo uploaded", data=OutletService(db).add_photo(outlet_id, photo_type, file, current_user))
