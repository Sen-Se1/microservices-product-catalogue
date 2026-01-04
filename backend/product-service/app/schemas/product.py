from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, max_length=5000)
    sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit")
    category: Optional[str] = Field(None, max_length=100)
    price: Decimal = Field(..., gt=0, le=99999999.99, description="Selling price")
    cost: Optional[Decimal] = Field(None, ge=0, le=99999999.99, description="Cost price")
    stock_quantity: int = Field(0, ge=0, description="Available stock")
    low_stock_threshold: Optional[int] = Field(10, ge=0)
    weight_kg: Optional[Decimal] = Field(None, ge=0, le=999.99)
    dimensions_cm: Optional[str] = Field(None, max_length=50)
    image_url: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('price', 'cost')
    def round_decimal(cls, v):
        if v is not None:
            return round(v, 2)
        return v
    
    @validator('sku')
    def sku_uppercase(cls, v):
        return v.upper()


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    category: Optional[str] = Field(None, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0, le=99999999.99)
    cost: Optional[Decimal] = Field(None, ge=0, le=99999999.99)
    stock_quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    weight_kg: Optional[Decimal] = Field(None, ge=0, le=999.99)
    dimensions_cm: Optional[str] = Field(None, max_length=50)
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class ProductInDB(ProductBase):
    id: UUID
    slug: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductResponse(ProductInDB):
    pass


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    size: int
    pages: int


class StockUpdate(BaseModel):
    quantity: int = Field(..., ge=0, description="New stock quantity")
    operation: str = Field("set", pattern="^(set|add|subtract)$", description="Operation: set, add, or subtract")