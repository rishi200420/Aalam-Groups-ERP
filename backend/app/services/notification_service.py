from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Notification, NotificationPreference, Role, User, UserRole
from app.repositories.notification_repository import NotificationRepository
from app.schemas.auth import UserRead
from app.schemas.common import PaginatedResponse
from app.schemas.notification import NotificationRead, NotificationSummary

_CATEGORY_PREFIXES: dict[str, str] = {
    "order_": "notify_orders",
    "dispatch_": "notify_dispatch",
    "low_stock": "notify_stock",
    "out_of_stock": "notify_stock",
}


def _preference_field_for_type(notification_type: str) -> str:
    for prefix, field in _CATEGORY_PREFIXES.items():
        if notification_type.startswith(prefix):
            return field
    return "notify_system"


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = NotificationRepository(db)

    def _serialize(self, notification: Notification) -> NotificationRead:
        return NotificationRead.model_validate(notification)

    def list_notifications(self, current_user: UserRead, *, page: int, page_size: int, unread_only: bool = False) -> PaginatedResponse[NotificationRead]:
        rows, total = self.repo.list_for_user(uuid.UUID(current_user.id), page=page, page_size=page_size, unread_only=unread_only)
        total_pages = (total + page_size - 1) // page_size if page_size else 0
        return PaginatedResponse(
            success=True,
            message="Notifications retrieved",
            data=[self._serialize(row) for row in rows],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def unread_count(self, current_user: UserRead) -> NotificationSummary:
        return NotificationSummary(unread_count=self.repo.unread_count(uuid.UUID(current_user.id)))

    def mark_read(self, notification_id: uuid.UUID, current_user: UserRead) -> NotificationRead:
        notification = self.repo.get(notification_id, uuid.UUID(current_user.id))
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        notification = self.repo.mark_read(notification)
        return self._serialize(notification)

    def mark_all_read(self, current_user: UserRead) -> int:
        return self.repo.mark_all_read(uuid.UUID(current_user.id))

    def delete_notification(self, notification_id: uuid.UUID, current_user: UserRead) -> None:
        notification = self.repo.get(notification_id, uuid.UUID(current_user.id))
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        self.repo.delete(notification)

    # --- Internal helpers used by other services to raise notifications ---

    def notify_users(
        self,
        user_ids: list[uuid.UUID],
        *,
        type: str,
        title: str,
        message: str,
        reference_type: str | None = None,
        reference_id: str | None = None,
        link: str | None = None,
    ) -> list[Notification]:
        created = []
        preference_field = _preference_field_for_type(type)
        unique_user_ids = set(user_ids)
        preferences = {
            pref.user_id: pref
            for pref in self.db.query(NotificationPreference).filter(NotificationPreference.user_id.in_(unique_user_ids)).all()
        }
        for user_id in unique_user_ids:
            preference = preferences.get(user_id)
            if preference is not None and getattr(preference, preference_field) is False:
                continue
            notification = Notification(
                id=uuid.uuid4(),
                user_id=user_id,
                type=type,
                title=title,
                message=message,
                reference_type=reference_type,
                reference_id=reference_id,
                link=link,
            )
            created.append(self.repo.create(notification))
        if created:
            self.db.commit()
        return created

    def notify_role(
        self,
        role_code: str,
        *,
        type: str,
        title: str,
        message: str,
        reference_type: str | None = None,
        reference_id: str | None = None,
        link: str | None = None,
    ) -> list[Notification]:
        user_ids = [
            row.id
            for row in self.db.query(User.id)
            .join(UserRole, UserRole.user_id == User.id)
            .join(Role, Role.id == UserRole.role_id)
            .filter(Role.code == role_code, User.is_active.is_(True))
            .distinct()
            .all()
        ]
        return self.notify_users(
            user_ids, type=type, title=title, message=message, reference_type=reference_type, reference_id=reference_id, link=link
        )
