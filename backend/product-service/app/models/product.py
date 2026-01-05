from sqlalchemy import Column, String, Text, Numeric, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.database import Base


# ToDo:
# - Add "created_by" prop.
# - Add "tags" prop.
# - Add "brand" prop.
# - Add "thumbnail" prop.
# - Add "discount_percentage" prop.
# - Change "image_url" to "images" (array).
# - Change "category" to "category_id".
#
# Can be meta data:
# - weight_kg = Column(Numeric(5, 2))
# - dimensions_cm = Column(String(50))
# - cost = Column(Numeric(10, 2))
#
# Can be indexes:
# - CREATE INDEX idx_products_category ON products(category_id);
# - CREATE INDEX idx_products_price ON products(price);
# - CREATE INDEX idx_products_brand ON products(brand);
#
# - File upload (product images).
class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(300), unique=True, nullable=False, index=True)
    description = Column(Text)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(100), index=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, default=10)
    is_active = Column(Boolean, default=True, index=True)
    image_url = Column(String(500))
    product_metadata = Column(JSONB, default=dict)

    # Using Text for simplicity with asyncpg
    created_at = Column(String, default=func.now())
    updated_at = Column(String, default=func.now())
    
    def __repr__(self):
        return f"<Product {self.sku}: {self.name}>"