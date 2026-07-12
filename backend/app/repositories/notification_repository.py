from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.flush()
        return notification

    def list_for_user(
        self, user_id: uuid.UUID, *, page: int, page_size: int, unread_only: bool = False
    ) -> tuple[list[Notification], int]:
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read.is_(False))
        total = query.count()
        rows = (
            query.order_by(Notification.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return rows, total

    def get(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> Notification | None:
        return (
            self.db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .first()
        )

    def unread_count(self, user_id: uuid.UUID) -> int:
        return (
            self.db.query(func.count(Notification.id))
            .filter(Notification.user_id == user_id, Notification.is_read.is_(False))
            .scalar()
            or 0
        )

    def mark_read(self, notification: Notification) -> Notification:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_all_read(self, user_id: uuid.UUID) -> int:
        rows = self.db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read.is_(False)).all()
        now = datetime.now(timezone.utc)
        for row in rows:
            row.is_read = True
            row.read_at = now
            self.db.add(row)
        self.db.commit()
        return len(rows)

    def delete(self, notification: Notification) -> None:
        self.db.delete(notification)
        self.db.commit()
