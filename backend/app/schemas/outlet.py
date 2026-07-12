from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.auth import UserRead
from app.schemas.common import SchemaBase

BusinessType = Literal["tea_shop", "cafe", "bakery", "restaurant", "hotel", "supermarket", "general_store"]
OutletBrand = Literal["TASTIQ", "LEMURIA"]
OutletStatus = Literal["active", "inactive", "blocked"]
OutletPhotoType = Literal["shop_front", "inside_shop", "name_board"]


class OutletContactCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    role: str | None = Field(default=None, max_length=80)
    phone: str | None = Field(default=None, max_length=20)
    whatsapp: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None


class OutletContactRead(SchemaBase):
    id: str
    name: str
    role: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    email: str | None = None


class OutletPhotoRead(SchemaBase):
    id: str
    photo_type: str
    file_name: str
    file_url: str
    content_type: str | None = None
    size_bytes: int | None = None
    created_at: datetime


class OutletVisitCreate(BaseModel):
    visit_date: datetime | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    photo_url: str | None = None
    notes: str | None = Field(default=None, max_length=3000)
    next_follow_up_date: datetime | None = None


class OutletVisitRead(SchemaBase):
    id: str
    visit_date: datetime
    distributor_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    photo_url: str | None = None
    notes: str | None = None
    next_follow_up_date: datetime | None = None
    created_at: datetime


class OutletBase(BaseModel):
    shop_name: str = Field(min_length=2, max_length=200)
    owner_name: str = Field(min_length=2, max_length=150)
    phone_number: str = Field(min_length=8, max_length=20)
    whatsapp_number: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    gst_number: str | None = Field(default=None, max_length=30)
    address: str = Field(min_length=5, max_length=1000)
    area: str = Field(min_length=2, max_length=120)
    city: str = Field(min_length=2, max_length=120)
    district: str = Field(min_length=2, max_length=120)
    state: str = Field(min_length=2, max_length=120)
    pincode: str = Field(min_length=4, max_length=10)
    territory: str = Field(min_length=2, max_length=120)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    google_maps_url: str | None = None
    business_type: BusinessType
    brands: list[OutletBrand] = Field(min_length=1)
    assigned_distributor_id: str | None = None
    status: OutletStatus = "active"
    notes: str | None = Field(default=None, max_length=3000)
    contacts: list[OutletContactCreate] = []

    @field_validator("brands")
    @classmethod
    def unique_brands(cls, value: list[str]) -> list[str]:
        return list(dict.fromkeys(value))


class OutletCreate(OutletBase):
    pass


class OutletUpdate(BaseModel):
    shop_name: str | None = Field(default=None, min_length=2, max_length=200)
    owner_name: str | None = Field(default=None, min_length=2, max_length=150)
    phone_number: str | None = Field(default=None, min_length=8, max_length=20)
    whatsapp_number: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    gst_number: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, min_length=5, max_length=1000)
    area: str | None = Field(default=None, min_length=2, max_length=120)
    city: str | None = Field(default=None, min_length=2, max_length=120)
    district: str | None = Field(default=None, min_length=2, max_length=120)
    state: str | None = Field(default=None, min_length=2, max_length=120)
    pincode: str | None = Field(default=None, min_length=4, max_length=10)
    territory: str | None = Field(default=None, min_length=2, max_length=120)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    google_maps_url: str | None = None
    business_type: BusinessType | None = None
    brands: list[OutletBrand] | None = None
    assigned_distributor_id: str | None = None
    status: OutletStatus | None = None
    notes: str | None = Field(default=None, max_length=3000)


class OutletRead(SchemaBase):
    id: str
    outlet_id: str
    shop_name: str
    owner_name: str
    phone_number: str
    whatsapp_number: str | None = None
    email: str | None = None
    gst_number: str | None = None
    address: str
    area: str
    city: str
    district: str
    state: str
    pincode: str
    territory: str
    latitude: float | None = None
    longitude: float | None = None
    google_maps_url: str | None = None
    business_type: str
    brands: list[str]
    assigned_distributor_id: str | None = None
    assigned_distributor: UserRead | None = None
    status: str
    notes: str | None = None
    qr_code_value: str
    qr_code_url: str
    visits: list[OutletVisitRead] = []
    photos: list[OutletPhotoRead] = []
    contacts: list[OutletContactRead] = []
    created_at: datetime
    updated_at: datetime


class OutletSummary(SchemaBase):
    total: int
    active: int
    new_this_month: int
    visits_today: int
