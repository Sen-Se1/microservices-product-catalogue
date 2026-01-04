from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    StockUpdate
)
from app.crud.product import product as crud_product
from app.utils.exceptions import (
    ProductNotFound,
    ProductAlreadyExists,
    InsufficientStock
)

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "products-service",
        "version": "1.0.0"
    }


@router.get("/products", response_model=ProductListResponse)
async def read_products(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
    search: Optional[str] = Query(None, description="Search in name, description, SKU"),
    include_inactive: bool = Query(False, description="Include inactive products")
):
    """
    Retrieve products with optional filtering and pagination.
    """
    try:
        items = await crud_product.get_multi(
            db,
            skip=skip,
            limit=limit,
            category=category,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
            active_only=not include_inactive,
            search=search
        )
        
        total = await crud_product.get_count(
            db,
            category=category,
            active_only=not include_inactive
        )
        
        pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1
        
        return ProductListResponse(
            items=items,
            total=total,
            page=current_page,
            size=len(items),
            pages=pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving products: {str(e)}"
        )


@router.get("/products/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: UUID = Path(..., description="Product ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific product by ID.
    """
    db_product = await crud_product.get(db, id=product_id)
    if db_product is None:
        raise ProductNotFound(f"Product with ID {product_id} not found")
    return db_product


@router.get("/products/slug/{slug}", response_model=ProductResponse)
async def read_product_by_slug(
    slug: str = Path(..., description="Product slug"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific product by slug.
    """
    db_product = await crud_product.get_by_slug(db, slug=slug)
    if db_product is None:
        raise ProductNotFound(f"Product with slug '{slug}' not found")
    return db_product


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    *,
    db: AsyncSession = Depends(get_db),
    product_in: ProductCreate
):
    """
    Create a new product.
    """
    # Check if SKU already exists
    existing = await crud_product.get_by_sku(db, sku=product_in.sku)
    if existing:
        raise ProductAlreadyExists(f"Product with SKU {product_in.sku} already exists")
    
    try:
        db_product = await crud_product.create(db, obj_in=product_in)
        return db_product
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating product: {str(e)}"
        )


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    *,
    db: AsyncSession = Depends(get_db),
    product_id: UUID = Path(..., description="Product ID"),
    product_in: ProductUpdate
):
    """
    Update a product.
    """
    db_product = await crud_product.get(db, id=product_id)
    if db_product is None:
        raise ProductNotFound(f"Product with ID {product_id} not found")
    
    # Check if new SKU conflicts with existing product
    if product_in.sku and product_in.sku != db_product.sku:
        existing = await crud_product.get_by_sku(db, sku=product_in.sku)
        if existing and existing.id != product_id:
            raise ProductAlreadyExists(f"SKU {product_in.sku} already in use")
    
    try:
        db_product = await crud_product.update(
            db, db_obj=db_product, obj_in=product_in
        )
        return db_product
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating product: {str(e)}"
        )


@router.patch("/products/{product_id}/stock", response_model=ProductResponse)
async def update_product_stock(
    *,
    db: AsyncSession = Depends(get_db),
    product_id: UUID = Path(..., description="Product ID"),
    stock_update: StockUpdate
):
    """
    Update product stock quantity.
    Operations: 'set', 'add', or 'subtract'
    """
    db_product = await crud_product.get(db, id=product_id)
    if db_product is None:
        raise ProductNotFound(f"Product with ID {product_id} not found")
    
    # Check if subtract operation would result in negative stock
    if (stock_update.operation == "subtract" and 
        db_product.stock_quantity < stock_update.quantity):
        raise InsufficientStock(
            f"Cannot subtract {stock_update.quantity} from current stock of {db_product.stock_quantity}"
        )
    
    try:
        db_product = await crud_product.update_stock(
            db, id=product_id, stock_update=stock_update
        )
        return db_product
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating stock: {str(e)}"
        )


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    *,
    db: AsyncSession = Depends(get_db),
    product_id: UUID = Path(..., description="Product ID")
):
    """
    Delete a product (soft delete - sets is_active=False).
    """
    db_product = await crud_product.get(db, id=product_id)
    if db_product is None:
        raise ProductNotFound(f"Product with ID {product_id} not found")
    
    try:
        await crud_product.remove(db, id=product_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting product: {str(e)}"
        )


@router.get("/products/categories", response_model=List[str])
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all distinct product categories.
    """
    try:
        categories = await crud_product.get_categories(db)
        return categories
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving categories: {str(e)}"
        )


@router.get("/products/low-stock", response_model=List[ProductResponse])
async def get_low_stock_products(
    db: AsyncSession = Depends(get_db)
):
    """
    Get products with stock below their threshold.
    """
    try:
        products = await crud_product.get_low_stock(db)
        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving low stock products: {str(e)}"
        )