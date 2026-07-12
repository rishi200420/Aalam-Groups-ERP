import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas.auth import UserRead
from app.schemas.common import APIResponse, MessageResponse, PaginatedResponse
from app.schemas.product import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    ProductCreate,
    ProductRead,
    ProductSummary,
    ProductUpdate,
    StockAdjustment,
)
from app.services.product_service import CategoryService, ProductService

router = APIRouter()


# ---- Categories ----

@router.get("/categories", response_model=APIResponse[list[CategoryRead]])
async def list_categories(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    is_active: bool | None = None,
):
    return APIResponse(success=True, message="Categories retrieved", data=CategoryService(db).list_categories(is_active=is_active))


@router.post("/categories", response_model=APIResponse[CategoryRead], status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Category created", data=CategoryService(db).create_category(payload, current_user))


@router.patch("/categories/{category_id}", response_model=APIResponse[CategoryRead])
async def update_category(
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Category updated", data=CategoryService(db).update_category(category_id, payload, current_user))


@router.delete("/categories/{category_id}", response_model=APIResponse[MessageResponse])
async def delete_category(
    category_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    CategoryService(db).delete_category(category_id, current_user)
    return APIResponse(success=True, message="Category deleted", data=MessageResponse(message="Category deleted"))


# ---- Products ----

@router.get("", response_model=PaginatedResponse[ProductRead])
async def list_products(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = None,
    category_id: str | None = None,
    brand: str | None = None,
    status: str | None = None,
    low_stock_only: bool = False,
):
    return ProductService(db).list_products(
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        brand=brand,
        status=status,
        low_stock_only=low_stock_only,
    )


@router.get("/summary", response_model=APIResponse[ProductSummary])
async def product_summary(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Product summary", data=ProductService(db).summary())


@router.post("", response_model=APIResponse[ProductRead], status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Product created", data=ProductService(db).create_product(payload, current_user))


@router.get("/{product_id}", response_model=APIResponse[ProductRead])
async def get_product(
    product_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Product retrieved", data=ProductService(db).get_product(product_id))


@router.patch("/{product_id}", response_model=APIResponse[ProductRead])
async def update_product(
    product_id: uuid.UUID,
    payload: ProductUpdate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Product updated", data=ProductService(db).update_product(product_id, payload, current_user))


@router.post("/{product_id}/stock-adjustments", response_model=APIResponse[ProductRead])
async def adjust_stock(
    product_id: uuid.UUID,
    payload: StockAdjustment,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Stock adjusted", data=ProductService(db).adjust_stock(product_id, payload, current_user))


@router.delete("/{product_id}", response_model=APIResponse[MessageResponse])
async def delete_product(
    product_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    ProductService(db).delete_product(product_id, current_user)
    return APIResponse(success=True, message="Product deleted", data=MessageResponse(message="Product deleted"))


@router.post("/{product_id}/images", response_model=APIResponse[ProductRead], status_code=status.HTTP_201_CREATED)
async def upload_product_image(
    product_id: uuid.UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    is_primary: bool = Query(default=False),
    file: UploadFile = File(...),
):
    return APIResponse(success=True, message="Image uploaded", data=ProductService(db).add_image(product_id, file, is_primary, current_user))
