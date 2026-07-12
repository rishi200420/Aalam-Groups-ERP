import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas.auth import UserRead
from app.schemas.common import APIResponse, MessageResponse, PaginatedResponse
from app.schemas.notification import NotificationRead, NotificationSummary
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("/status")
async def notifications_module_status():
    return {"module": "notifications", "status": "ready"}


@router.get("/unread-count", response_model=APIResponse[NotificationSummary])
async def unread_count(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Unread count retrieved", data=NotificationService(db).unread_count(current_user))


@router.put("/mark-all-read", response_model=MessageResponse)
async def mark_all_read(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    count = NotificationService(db).mark_all_read(current_user)
    return MessageResponse(message=f"Marked {count} notification(s) as read")


@router.get("", response_model=PaginatedResponse[NotificationRead])
async def list_notifications(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    unread_only: bool = Query(default=False),
):
    return NotificationService(db).list_notifications(current_user, page=page, page_size=page_size, unread_only=unread_only)


@router.put("/{notification_id}/read", response_model=APIResponse[NotificationRead])
async def mark_read(
    notification_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Notification marked as read", data=NotificationService(db).mark_read(notification_id, current_user))


@router.delete("/{notification_id}", response_model=MessageResponse)
async def delete_notification(
    notification_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    NotificationService(db).delete_notification(notification_id, current_user)
    return MessageResponse(message="Notification deleted")
