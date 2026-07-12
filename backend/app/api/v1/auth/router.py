from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshTokenRequest,
    UserRead,
)
from app.schemas.common import APIResponse, MessageResponse
from app.schemas.profile import ChangePasswordRequest, ProfileRead, ProfileUpdate
from app.services.auth_service import AuthService

router = APIRouter()

AVATAR_UPLOAD_ROOT = Path(__file__).resolve().parents[4] / "uploads" / "avatars"
ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/login", response_model=APIResponse[LoginResponse], status_code=status.HTTP_200_OK)
async def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    result = AuthService(db).login(payload)
    return APIResponse(success=True, message="Login successful", data=result)


@router.post("/refresh", response_model=APIResponse[LoginResponse])
async def refresh_token(payload: RefreshTokenRequest, db: Annotated[Session, Depends(get_db)]):
    result = AuthService(db).refresh(payload)
    return APIResponse(success=True, message="Token refreshed", data=result)


@router.get("/me", response_model=APIResponse[UserRead])
async def get_me(current_user: Annotated[UserRead, Depends(get_current_user)]):
    return APIResponse(success=True, message="OK", data=current_user)


@router.post("/logout", response_model=APIResponse[MessageResponse])
async def logout(
    payload: LogoutRequest,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    AuthService(db).logout(current_user.id, payload.refresh_token)
    return APIResponse(success=True, message="Logged out successfully", data=MessageResponse(message="Logged out"))


@router.post("/forgot-password", response_model=APIResponse[MessageResponse])
async def forgot_password(payload: ForgotPasswordRequest, db: Annotated[Session, Depends(get_db)]):
    AuthService(db).request_password_reset(payload.email)
    return APIResponse(
        success=True,
        message="If an account exists for this email, password reset instructions have been sent.",
        data=MessageResponse(message="Reset request received"),
    )


@router.get("/status")
async def auth_module_status():
    return {"module": "auth", "status": "ready"}


@router.get("/profile", response_model=APIResponse[ProfileRead])
async def get_profile(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Profile retrieved", data=AuthService(db).get_profile(current_user.id))


@router.patch("/profile", response_model=APIResponse[ProfileRead])
async def update_profile(
    payload: ProfileUpdate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Profile updated", data=AuthService(db).update_profile(current_user.id, payload))


@router.post("/profile/change-password", response_model=APIResponse[MessageResponse])
async def change_password(
    payload: ChangePasswordRequest,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    AuthService(db).change_password(current_user.id, payload)
    return APIResponse(
        success=True,
        message="Password changed. Please log in again.",
        data=MessageResponse(message="Password changed"),
    )


@router.post("/profile/avatar", response_model=APIResponse[ProfileRead])
async def upload_avatar(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
):
    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, and WEBP images are allowed")
    suffix = Path(file.filename or "").suffix.lower() or ".jpg"
    safe_name = f"{uuid.uuid4()}{suffix}"
    target_dir = AVATAR_UPLOAD_ROOT / current_user.id
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / safe_name
    with target.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    avatar_url = f"/uploads/avatars/{current_user.id}/{safe_name}"
    return APIResponse(success=True, message="Avatar updated", data=AuthService(db).set_avatar(current_user.id, avatar_url))
