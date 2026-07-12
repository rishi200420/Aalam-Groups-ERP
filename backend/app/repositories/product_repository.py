import uuid
from datetime import datetime, timezone

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models import Category, Product, ProductImage


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, *, is_active: bool | None = None) -> list[Category]:
        query = self.db.query(Category)
        if is_active is not None:
            query = query.filter(Category.is_active == is_active)
        return query.order_by(Category.name.asc()).all()

    def get(self, category_id: uuid.UUID) -> Category | None:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_by_code(self, code: str) -> Category | None:
        return self.db.query(Category).filter(Category.code == code).first()

    def product_count(self, category_id: uuid.UUID) -> int:
        return (
            self.db.query(func.count(Product.id))
            .filter(Product.category_id == category_id, Product.deleted_at.is_(None))
            .scalar()
        )

    def create(self, category: Category) -> Category:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def save(self, category: Category) -> Category:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category: Category) -> None:
        self.db.delete(category)
        self.db.commit()


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        category_id: uuid.UUID | None,
        brand: str | None,
        status: str | None,
        low_stock_only: bool,
    ) -> tuple[list[Product], int]:
        query = (
            self.db.query(Product)
            .options(joinedload(Product.category), joinedload(Product.images))
            .filter(Product.deleted_at.is_(None))
        )

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Product.sku.ilike(pattern),
                    Product.name.ilike(pattern),
                    Product.barcode.ilike(pattern),
                )
            )
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if brand:
            query = query.filter(Product.brand == brand)
        if status:
            query = query.filter(Product.status == status)
        if low_stock_only:
            query = query.filter(Product.stock_quantity <= Product.low_stock_threshold)

        total = query.count()
        rows = (
            query.order_by(Product.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return rows, total

    def get(self, product_id: uuid.UUID) -> Product | None:
        return (
            self.db.query(Product)
            .options(joinedload(Product.category), joinedload(Product.images))
            .filter(Product.id == product_id, Product.deleted_at.is_(None))
            .first()
        )

    def get_by_sku(self, sku: str) -> Product | None:
        return self.db.query(Product).filter(Product.sku == sku, Product.deleted_at.is_(None)).first()

    def get_by_barcode(self, barcode: str) -> Product | None:
        return self.db.query(Product).filter(Product.barcode == barcode, Product.deleted_at.is_(None)).first()

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def save(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def soft_delete(self, product: Product, user_id: uuid.UUID) -> None:
        product.deleted_at = datetime.now(timezone.utc)
        product.updated_by = user_id
        self.db.add(product)
        self.db.commit()

    def add_image(self, image: ProductImage) -> ProductImage:
        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)
        return image

    def summary(self) -> dict[str, int]:
        query = self.db.query(Product).filter(Product.deleted_at.is_(None))
        return {
            "total": query.count(),
            "active": query.filter(Product.status == "active").count(),
            "low_stock": query.filter(Product.stock_quantity <= Product.low_stock_threshold, Product.stock_quantity > 0).count(),
            "out_of_stock": query.filter(Product.stock_quantity <= 0).count(),
        }
