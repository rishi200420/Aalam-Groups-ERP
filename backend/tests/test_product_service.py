import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import Product, ProductImage
from app.services.product_service import ProductService


def _build_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_product_with_image_serializes_without_uuid_validation_error():
    """Regression test: ProductImageRead.model_validate() previously crashed
    with a ResponseValidationError because `id` was typed as strict `str`
    while the ORM column is a UUID. Any product with an uploaded image would
    500 on every list/detail request."""
    db = _build_session()
    try:
        product = Product(
            id=uuid.uuid4(), sku="IMG-1", name="Image Test", brand="TASTIQ", unit="pcs",
            mrp=100, distributor_price=80, stock_quantity=10, low_stock_threshold=5, status="active",
        )
        db.add(product)
        db.commit()

        image = ProductImage(id=uuid.uuid4(), product_id=product.id, file_name="test.jpg", file_url="/uploads/test.jpg", is_primary=True)
        db.add(image)
        db.commit()
        db.refresh(product)

        result = ProductService(db)._serialize(product)
        assert len(result.images) == 1
        assert result.images[0].id == str(image.id)
        assert isinstance(result.images[0].id, str)
    finally:
        db.close()
