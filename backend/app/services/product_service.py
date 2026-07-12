import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models import Category, Product, ProductImage, Warehouse
from app.repositories.product_repository import CategoryRepository, ProductRepository
from app.schemas.auth import UserRead
from app.schemas.common import PaginatedResponse
from app.schemas.product import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    ProductCreate,
    ProductImageRead,
    ProductRead,
    ProductSummary,
    ProductUpdate,
    StockAdjustment,
)

UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "products"
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _is_founder(user: UserRead) -> bool:
    return "founder" in user.roles or "super_admin" in user.roles


def _is_warehouse(user: UserRead) -> bool:
    return "warehouse" in user.roles


class CategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CategoryRepository(db)

    def _serialize(self, category: Category) -> CategoryRead:
        return CategoryRead(
            id=str(category.id),
            name=category.name,
            code=category.code,
            description=category.description,
            is_active=category.is_active,
            product_count=self.repo.product_count(category.id),
            created_at=category.created_at,
            updated_at=category.updated_at,
        )

    def list_categories(self, *, is_active: bool | None = None) -> list[CategoryRead]:
        return [self._serialize(category) for category in self.repo.list(is_active=is_active)]

    def create_category(self, payload: CategoryCreate, current_user: UserRead) -> CategoryRead:
        if not _is_founder(current_user):
            raise HTTPException(status_code=403, detail="Only founders can manage categories")
        if self.repo.get_by_code(payload.code):
            raise HTTPException(status_code=409, detail="Category code already exists")
        category = Category(
            id=uuid.uuid4(),
            name=payload.name,
            code=payload.code,
            description=payload.description,
            is_active=payload.is_active,
            created_by=uuid.UUID(current_user.id),
            updated_by=uuid.UUID(current_user.id),
        )
        self.repo.create(category)
        return self._serialize(category)

    def update_category(self, category_id: uuid.UUID, payload: CategoryUpdate, current_user: UserRead) -> CategoryRead:
        if not _is_founder(current_user):
            raise HTTPException(status_code=403, detail="Only founders can manage categories")
        category = self.repo.get(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        update_data = payload.model_dump(exclude_unset=True)
        if "code" in update_data:
            existing = self.repo.get_by_code(update_data["code"])
            if existing and existing.id != category.id:
                raise HTTPException(status_code=409, detail="Category code already exists")
        for key, value in update_data.items():
            setattr(category, key, value)
        category.updated_by = uuid.UUID(current_user.id)
        self.repo.save(category)
        return self._serialize(category)

    def delete_category(self, category_id: uuid.UUID, current_user: UserRead) -> None:
        if not _is_founder(current_user):
            raise HTTPException(status_code=403, detail="Only founders can manage categories")
        category = self.repo.get(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        if self.repo.product_count(category_id) > 0:
            raise HTTPException(status_code=409, detail="Cannot delete a category that has products")
        self.repo.delete(category)


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)
        self.category_repo = CategoryRepository(db)

    def _serialize(self, product: Product) -> ProductRead:
        category_read = None
        if product.category:
            category_read = CategoryRead(
                id=str(product.category.id),
                name=product.category.name,
                code=product.category.code,
                description=product.category.description,
                is_active=product.category.is_active,
                product_count=0,
                created_at=product.category.created_at,
                updated_at=product.category.updated_at,
            )
        return ProductRead(
            id=str(product.id),
            sku=product.sku,
            barcode=product.barcode,
            name=product.name,
            description=product.description,
            category_id=str(product.category_id) if product.category_id else None,
            category=category_read,
            brand=product.brand,
            unit=product.unit,
            mrp=product.mrp,
            distributor_price=product.distributor_price,
            stock_quantity=product.stock_quantity,
            low_stock_threshold=product.low_stock_threshold,
            is_low_stock=product.stock_quantity <= product.low_stock_threshold,
            status=product.status,
            images=[
                ProductImageRead.model_validate(image)
                for image in sorted(product.images, key=lambda item: item.created_at, reverse=True)
            ],
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

    def list_products(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        category_id: str | None,
        brand: str | None,
        status: str | None,
        low_stock_only: bool,
    ) -> PaginatedResponse[ProductRead]:
        rows, total = self.repo.list(
            page=page,
            page_size=page_size,
            search=search,
            category_id=uuid.UUID(category_id) if category_id else None,
            brand=brand,
            status=status,
            low_stock_only=low_stock_only,
        )
        total_pages = (total + page_size - 1) // page_size if total else 0
        return PaginatedResponse(
            success=True,
            message="Products retrieved",
            data=[self._serialize(row) for row in rows],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def get_product(self, product_id: uuid.UUID) -> ProductRead:
        product = self.repo.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return self._serialize(product)

    def create_product(self, payload: ProductCreate, current_user: UserRead) -> ProductRead:
        if not (_is_founder(current_user) or _is_warehouse(current_user)):
            raise HTTPException(status_code=403, detail="Cannot create products")
        if self.repo.get_by_sku(payload.sku):
            raise HTTPException(status_code=409, detail="SKU already exists")
        if payload.barcode and self.repo.get_by_barcode(payload.barcode):
            raise HTTPException(status_code=409, detail="Barcode already exists")

        category_id = None
        if payload.category_id:
            category_id = uuid.UUID(payload.category_id)
            if not self.category_repo.get(category_id):
                raise HTTPException(status_code=404, detail="Category not found")

        warehouse_id = None
        if payload.warehouse_id:
            warehouse_id = uuid.UUID(payload.warehouse_id)
            if not self.db.query(Warehouse).filter(Warehouse.id == warehouse_id).first():
                raise HTTPException(status_code=404, detail="Warehouse not found")

        user_id = uuid.UUID(current_user.id)
        product = Product(
            id=uuid.uuid4(),
            sku=payload.sku,
            barcode=payload.barcode,
            name=payload.name,
            description=payload.description,
            category_id=category_id,
            brand=payload.brand,
            warehouse_id=warehouse_id,
            unit=payload.unit,
            mrp=payload.mrp,
            distributor_price=payload.distributor_price,
            stock_quantity=payload.stock_quantity,
            low_stock_threshold=payload.low_stock_threshold,
            status=payload.status,
            created_by=user_id,
            updated_by=user_id,
        )
        self.repo.create(product)
        return self.get_product(product.id)

    def update_product(self, product_id: uuid.UUID, payload: ProductUpdate, current_user: UserRead) -> ProductRead:
        if not (_is_founder(current_user) or _is_warehouse(current_user)):
            raise HTTPException(status_code=403, detail="Cannot edit products")
        product = self.repo.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        update_data = payload.model_dump(exclude_unset=True)
        if "sku" in update_data:
            existing = self.repo.get_by_sku(update_data["sku"])
            if existing and existing.id != product.id:
                raise HTTPException(status_code=409, detail="SKU already exists")
        if update_data.get("barcode"):
            existing = self.repo.get_by_barcode(update_data["barcode"])
            if existing and existing.id != product.id:
                raise HTTPException(status_code=409, detail="Barcode already exists")
        if "category_id" in update_data and update_data["category_id"]:
            category_id = uuid.UUID(update_data["category_id"])
            if not self.category_repo.get(category_id):
                raise HTTPException(status_code=404, detail="Category not found")
            update_data["category_id"] = category_id
        if "warehouse_id" in update_data and update_data["warehouse_id"]:
            warehouse_id = uuid.UUID(update_data["warehouse_id"])
            if not self.db.query(Warehouse).filter(Warehouse.id == warehouse_id).first():
                raise HTTPException(status_code=404, detail="Warehouse not found")
            update_data["warehouse_id"] = warehouse_id

        for key, value in update_data.items():
            setattr(product, key, value)
        product.updated_by = uuid.UUID(current_user.id)
        self.repo.save(product)
        return self.get_product(product.id)

    def adjust_stock(self, product_id: uuid.UUID, payload: StockAdjustment, current_user: UserRead) -> ProductRead:
        if not (_is_founder(current_user) or _is_warehouse(current_user)):
            raise HTTPException(status_code=403, detail="Cannot adjust stock")
        product = self.repo.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        new_quantity = product.stock_quantity + payload.quantity
        if new_quantity < 0:
            raise HTTPException(status_code=400, detail="Stock cannot go below zero")
        product.stock_quantity = new_quantity
        product.updated_by = uuid.UUID(current_user.id)
        self.repo.save(product)
        return self.get_product(product.id)

    def delete_product(self, product_id: uuid.UUID, current_user: UserRead) -> None:
        if not _is_founder(current_user):
            raise HTTPException(status_code=403, detail="Only founders can delete products")
        product = self.repo.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        self.repo.soft_delete(product, uuid.UUID(current_user.id))

    def add_image(self, product_id: uuid.UUID, file: UploadFile, is_primary: bool, current_user: UserRead) -> ProductRead:
        if not (_is_founder(current_user) or _is_warehouse(current_user)):
            raise HTTPException(status_code=403, detail="Cannot upload product images")
        product = self.repo.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=400, detail="Only JPEG, PNG, and WEBP images are allowed")

        suffix = Path(file.filename or "").suffix.lower() or ".jpg"
        safe_name = f"{uuid.uuid4()}{suffix}"
        target_dir = UPLOAD_ROOT / product.sku
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / safe_name
        with target.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        image = ProductImage(
            id=uuid.uuid4(),
            product_id=product.id,
            file_name=safe_name,
            file_url=f"/uploads/products/{product.sku}/{safe_name}",
            content_type=file.content_type,
            size_bytes=target.stat().st_size,
            is_primary=is_primary,
            created_by=uuid.UUID(current_user.id),
            updated_by=uuid.UUID(current_user.id),
        )
        self.repo.add_image(image)
        return self.get_product(product.id)

    def summary(self) -> ProductSummary:
        return ProductSummary(**self.repo.summary())
