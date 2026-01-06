from sqlalchemy import Column, String, Text, Numeric, Integer, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(300), unique=True, nullable=False, index=True)
    description = Column(Text)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    category_id = Column(String(100), index=True)
    brand = Column(String(100), index=True)
    price = Column(Numeric(10, 2), nullable=False, index=True)
    stock_quantity = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, default=10)
    discount_percentage = Column(Numeric(5, 2), default=0)
    is_active = Column(Boolean, default=True, index=True)
    thumbnail = Column(String(500))
    images = Column(ARRAY(String), default=[])
    tags = Column(ARRAY(String), default=[])
    created_by = Column(UUID(as_uuid=True), index=True)
    product_metadata = Column(JSONB, default=dict)
    created_at = Column(String, default=func.now())
    updated_at = Column(String, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Product {self.sku}: {self.name}>"