from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import SchemaBase

RoleCode = Literal["founder", "distributor", "warehouse", "sales_executive"]
BrandCode = Literal["TASTIQ", "LEMURIA"]


class UserManagementRead(SchemaBase):
    id: str
    email: str
    full_name: str
    phone: str | None = None
    role: str
    is_active: bool
    employee_id: str | None = None
    distributor_code: str | None = None
    territory: str | None = None
    brand: str | None = None
    joining_date: date | None = None
    profile_image_url: str | None = None
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class UserCreateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)
    password: str = Field(min_length=8, max_length=128)
    role: RoleCode = "distributor"
    employee_id: str | None = Field(default=None, max_length=40)
    distributor_code: str | None = Field(default=None, max_length=40)
    territory: str | None = Field(default=None, max_length=120)
    brand: BrandCode | None = None
    joining_date: date | None = None


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    role: RoleCode | None = None
    employee_id: str | None = Field(default=None, max_length=40)
    distributor_code: str | None = Field(default=None, max_length=40)
    territory: str | None = Field(default=None, max_length=120)
    brand: BrandCode | None = None
    joining_date: date | None = None
    is_active: bool | None = None


class PasswordResetRequest(BaseModel):
    new_password: str = Field(min_length=8, max_length=128)
