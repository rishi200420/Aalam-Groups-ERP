from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "OK"
    data: Optional[T] = None


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "OK"
    data: list[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 0


class MessageResponse(SchemaBase):
    message: str


class ErrorDetail(SchemaBase):
    field: Optional[str] = None
    message: str


class ErrorResponse(SchemaBase):
    success: bool = False
    message: str
    data: Optional[Any] = None
