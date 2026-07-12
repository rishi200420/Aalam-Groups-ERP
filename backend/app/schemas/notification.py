from datetime import datetime

from pydantic import Field, field_validator

from app.schemas.common import SchemaBase


class NotificationRead(SchemaBase):
    id: str
    type: str
    title: str
    message: str
    reference_type: str | None = None
    reference_id: str | None = None
    link: str | None = None
    is_read: bool
    read_at: datetime | None = None
    created_at: datetime

    @field_validator("id", "reference_id", mode="before")
    @classmethod
    def _coerce_str(cls, value: object) -> object:
        if value is None:
            return value
        return str(value)


class NotificationSummary(SchemaBase):
    unread_count: int


class NotificationMarkReadRequest(SchemaBase):
    notification_ids: list[str] = Field(default_factory=list)
