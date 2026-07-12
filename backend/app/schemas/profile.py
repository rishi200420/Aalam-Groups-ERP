from datetime import date, datetime

from pydantic import Field

from app.schemas.common import SchemaBase


class ProfileRead(SchemaBase):
    id: str
    email: str
    full_name: str
    phone: str | None = None
    roles: list[str]
    primary_role: str | None = None
    is_active: bool
    employee_id: str | None = None
    distributor_code: str | None = None
    territory: str | None = None
    brand: str | None = None
    joining_date: date | None = None
    profile_image_url: str | None = None
    last_login_at: datetime | None = None
    created_at: datetime


class ProfileUpdate(SchemaBase):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    phone: str | None = None


class ChangePasswordRequest(SchemaBase):
    current_password: str
    new_password: str = Field(min_length=8, max_length=100)
