from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import SchemaBase


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class UserRead(SchemaBase):
    id: str
    email: str
    full_name: str
    phone: str | None = None
    roles: list[str]
    primary_role: str | None = None
    is_active: bool


class TokenData(SchemaBase):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginResponse(SchemaBase):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead


class LogoutRequest(BaseModel):
    refresh_token: str | None = None
