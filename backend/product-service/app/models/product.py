from sqlalchemy import Column, String, Text, Numeric, Integer, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(300), unique=True, nullable=False, index=True)
    description = Column(Text)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(100), index=True)
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2))
    stock_quantity = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, default=10)
    weight_kg = Column(Numeric(5, 2))
    dimensions_cm = Column(String(50))
    is_active = Column(Boolean, default=True, index=True)
    image_url = Column(String(500))
    # metadata = Column(JSON, default={})
    product_metadata = Column(JSON, default={})  # Option 1
    created_at = Column(Text)  # Using Text for simplicity with asyncpg
    updated_at = Column(Text)
    
    def __repr__(self):
        return f"<Product {self.sku}: {self.name}>"