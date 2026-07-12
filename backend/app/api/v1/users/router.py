import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas.auth import UserRead
from app.schemas.common import APIResponse, MessageResponse, PaginatedResponse
from app.schemas.user_management import (
    PasswordResetRequest,
    UserCreateRequest,
    UserManagementRead,
    UserUpdateRequest,
)
from app.services.user_management_service import UserManagementService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[UserManagementRead])
async def list_users(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
):
    return UserManagementService(db).list_users(
        current_user=current_user, page=page, page_size=page_size, search=search, role=role, is_active=is_active
    )


@router.post("", response_model=APIResponse[UserManagementRead], status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="User created", data=UserManagementService(db).create_user(payload, current_user))


@router.get("/{user_id}", response_model=APIResponse[UserManagementRead])
async def get_user(
    user_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="User retrieved", data=UserManagementService(db).get_user(user_id, current_user))


@router.patch("/{user_id}", response_model=APIResponse[UserManagementRead])
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdateRequest,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="User updated", data=UserManagementService(db).update_user(user_id, payload, current_user))


@router.post("/{user_id}/deactivate", response_model=APIResponse[UserManagementRead])
async def deactivate_user(
    user_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="User deactivated", data=UserManagementService(db).deactivate_user(user_id, current_user))


@router.post("/{user_id}/activate", response_model=APIResponse[UserManagementRead])
async def activate_user(
    user_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="User activated", data=UserManagementService(db).activate_user(user_id, current_user))


@router.post("/{user_id}/reset-password", response_model=APIResponse[MessageResponse])
async def reset_password(
    user_id: uuid.UUID,
    payload: PasswordResetRequest,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    UserManagementService(db).reset_password(user_id, payload, current_user)
    return APIResponse(success=True, message="Password reset", data=MessageResponse(message="Password reset"))


@router.delete("/{user_id}", response_model=APIResponse[MessageResponse])
async def delete_user(
    user_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    UserManagementService(db).delete_user(user_id, current_user)
    return APIResponse(success=True, message="User deleted", data=MessageResponse(message="User deleted"))
