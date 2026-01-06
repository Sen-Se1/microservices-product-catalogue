from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import json


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, max_length=5000)
    sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit")
    category_id: Optional[str] = Field(None, max_length=100, description="Category ID")
    brand: Optional[str] = Field(None, max_length=100, description="Brand name")
    price: Decimal = Field(..., gt=0, le=99999999.99, description="Selling price")
    stock_quantity: int = Field(0, ge=0, description="Available stock")
    low_stock_threshold: Optional[int] = Field(10, ge=0)
    discount_percentage: Optional[Decimal] = Field(0, ge=0, le=100, description="Discount percentage (0-100)")
    tags: List[str] = Field(default_factory=list, description="Product tags")
    product_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_by: Optional[UUID] = Field(None, description="ID of user who created the product")
    
    @validator('price', 'discount_percentage')
    def round_decimal(cls, v):
        if v is not None:
            return round(v, 2)
        return v
    
    @validator('sku')
    def sku_uppercase(cls, v):
        return v.upper()
    
    @validator('tags')
    def validate_tags(cls, v):
        if v is None:
            return []
        # Convert all tags to lowercase for consistency
        return [tag.lower().strip() for tag in v if tag.strip()]


class ProductCreateResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    sku: str
    category_id: Optional[str] = None
    brand: Optional[str] = None
    price: Decimal
    stock_quantity: int = 0
    low_stock_threshold: Optional[int] = 10
    discount_percentage: Optional[Decimal] = 0
    thumbnail: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_by: Optional[UUID] = None
    product_metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    uploaded_files: Dict[str, Any] = Field(default_factory=dict)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    category_id: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)  # ADD THIS LINE
    brand: Optional[str] = Field(None, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0, le=99999999.99)
    stock_quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    thumbnail: Optional[str] = Field(None, max_length=500)
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
    product_metadata: Optional[Dict[str, Any]] = None
    
    @validator('price', 'discount_percentage')
    def round_decimal(cls, v):
        if v is not None:
            return round(v, 2)
        return v


class ProductResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    sku: str
    category_id: Optional[str] = None
    brand: Optional[str] = None
    price: Decimal
    stock_quantity: int = 0
    low_stock_threshold: Optional[int] = 10
    discount_percentage: Optional[Decimal] = 0
    thumbnail: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_by: Optional[UUID] = None
    product_metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    size: int
    pages: int


class StockUpdate(BaseModel):
    quantity: int = Field(..., ge=0, description="New stock quantity")
    operation: str = Field("set", pattern="^(set|add|subtract)$", description="Operation: set, add, or subtract")