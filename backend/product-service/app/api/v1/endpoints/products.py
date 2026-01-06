from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path as FastAPIPath, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.product import (
    ProductCreateResponse,
    ProductResponse,
    ProductListResponse,
    StockUpdate,
    ProductUpdate
)
from app.crud.product import product as crud_product
from app.utils.exceptions import (
    ProductNotFound,
    ProductAlreadyExists,
    InsufficientStock
)
from pathlib import Path
import shutil
import json
import uuid as uuid_lib
from decimal import Decimal
from fastapi.responses import FileResponse

router = APIRouter()

# Configuration for file uploads
UPLOAD_DIR = Path("uploads/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


async def save_uploaded_file(upload_file: UploadFile, directory: FastAPIPath, filename: str) -> str:
    """Save uploaded file and return relative URL"""
    # Validate file type
    if upload_file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {upload_file.content_type}. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    file_path = directory / filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        # Read in chunks for large files
        while chunk := await upload_file.read(8192):
            buffer.write(chunk)
    
    # Reset file pointer for potential reuse
    await upload_file.seek(0)
    
    # Return relative URL
    return f"/uploads/products/{filename}"


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "products-service",
        "version": "1.0.0"
    }


@router.post("/products", response_model=ProductCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    *,
    db: AsyncSession = Depends(get_db),
    # Required fields
    name: str = Form(..., description="Product name"),
    sku: str = Form(..., description="Stock Keeping Unit"),
    price: float = Form(..., gt=0, description="Product price"),
    # Optional fields
    description: Optional[str] = Form(None),
    category_id: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    stock_quantity: int = Form(0, ge=0),
    low_stock_threshold: Optional[int] = Form(10),
    discount_percentage: Optional[float] = Form(0.0, ge=0, le=100),
    created_by: Optional[str] = Form(None),
    tags: Optional[str] = Form("[]", description="JSON array of tags"),
    product_metadata: Optional[str] = Form("{}", description="JSON product_metadata"),
    # File uploads
    thumbnail: Optional[UploadFile] = File(None, description="Thumbnail image"),
    images: List[UploadFile] = File([], description="Product images")
):
    """
    Create a new product with image uploads.
    Uses multipart/form-data format.
    """
    try:
        # Check if SKU already exists
        existing = await crud_product.get_by_sku(db, sku=sku.upper())
        if existing:
            raise ProductAlreadyExists(f"Product with SKU {sku} already exists")
        
        # Parse JSON fields
        tags_list = []
        if tags and tags != "[]":
            try:
                tags_list = json.loads(tags)
                if not isinstance(tags_list, list):
                    tags_list = []
            except json.JSONDecodeError:
                tags_list = []
        
        metadata_dict = {}
        if product_metadata and product_metadata != "{}":
            try:
                metadata_dict = json.loads(product_metadata)
                if not isinstance(metadata_dict, dict):
                    metadata_dict = {}
            except json.JSONDecodeError:
                metadata_dict = {}
        
        # Generate product ID for filenames
        product_uuid = uuid_lib.uuid4()
        uploaded_files = {
            "thumbnail": None,
            "images": []
        }
        
        # Process thumbnail if provided
        thumbnail_url = None
        if thumbnail and thumbnail.filename:
            thumb_filename = f"thumb_{product_uuid}_{thumbnail.filename}"
            thumbnail_url = await save_uploaded_file(thumbnail, UPLOAD_DIR, thumb_filename)
            uploaded_files["thumbnail"] = thumb_filename
        
        # Process product images
        image_urls = []
        for i, image in enumerate(images):
            if image.filename:  # Only process if file was actually uploaded
                img_filename = f"{product_uuid}_{i}_{image.filename}"
                img_url = await save_uploaded_file(image, UPLOAD_DIR, img_filename)
                image_urls.append(img_url)
                uploaded_files["images"].append(img_filename)
        
        # Validate created_by UUID if provided
        created_by_uuid = None
        if created_by:
            try:
                created_by_uuid = UUID(created_by)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid created_by UUID format"
                )
        
        # Create product in database
        db_product = await crud_product.create(
            db,
            name=name,
            sku=sku.upper(),
            price=Decimal(str(price)),
            description=description,
            category_id=category_id,
            brand=brand,
            stock_quantity=stock_quantity,
            low_stock_threshold=low_stock_threshold,
            discount_percentage=Decimal(str(discount_percentage)),
            tags=tags_list,
            product_metadata=metadata_dict,
            created_by=created_by_uuid,
            thumbnail_url=thumbnail_url,
            image_urls=image_urls
        )
        
        # Convert SQLAlchemy model to dict
        product_dict = {
            "id": db_product.id,
            "name": db_product.name,
            "slug": db_product.slug,
            "description": db_product.description,
            "sku": db_product.sku,
            "category_id": db_product.category_id,
            "brand": db_product.brand,
            "price": db_product.price,
            "stock_quantity": db_product.stock_quantity,
            "low_stock_threshold": db_product.low_stock_threshold,
            "discount_percentage": db_product.discount_percentage,
            "thumbnail": db_product.thumbnail,
            "images": db_product.images,
            "tags": db_product.tags,
            "created_by": db_product.created_by,
            "product_metadata": db_product.product_metadata or {},
            "is_active": db_product.is_active,
            "created_at": db_product.created_at,
            "updated_at": db_product.updated_at,
            "uploaded_files": uploaded_files
        }
        
        return ProductCreateResponse(**product_dict)
        
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON in tags or product_metadata: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data format: {str(e)}"
        )
    except Exception as e:
        # Clean up uploaded files if product creation fails
        import traceback
        print(f"Error creating product: {str(e)}")
        print(traceback.format_exc())
        
        # Cleanup uploaded files
        for filename in uploaded_files.get("images", []):
            file_path = UPLOAD_DIR / filename
            if file_path.exists():
                file_path.unlink()
        
        if uploaded_files.get("thumbnail"):
            thumb_path = UPLOAD_DIR / uploaded_files["thumbnail"]
            if thumb_path.exists():
                thumb_path.unlink()
                
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating product: {str(e)}"
        )


@router.get("/products", response_model=ProductListResponse)
async def read_products(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    discount_min: Optional[float] = Query(None, ge=0, le=100, description="Minimum discount percentage"),
    discount_max: Optional[float] = Query(None, ge=0, le=100, description="Maximum discount percentage"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
    search: Optional[str] = Query(None, description="Search in name, description, SKU, brand"),
    include_inactive: bool = Query(False, description="Include inactive products")
):
    """
    Retrieve products with optional filtering and pagination.
    """
    try:
        # Parse tags from comma-separated string
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        items = await crud_product.get_multi(
            db,
            skip=skip,
            limit=limit,
            category_id=category_id,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            discount_min=discount_min,
            discount_max=discount_max,
            tags=tag_list,
            in_stock=in_stock,
            active_only=not include_inactive,
            search=search
        )
        
        total = await crud_product.get_count(
            db,
            category_id=category_id,
            brand=brand,
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
    product_id: UUID = FastAPIPath(..., description="Product ID"),
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
    slug: str = FastAPIPath(..., description="Product slug"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific product by slug.
    """
    db_product = await crud_product.get_by_slug(db, slug=slug)
    if db_product is None:
        raise ProductNotFound(f"Product with slug '{slug}' not found")
    return db_product


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    *,
    db: AsyncSession = Depends(get_db),
    product_id: UUID = FastAPIPath(..., description="Product ID"),
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
        # Convert Pydantic model to dict
        update_data = product_in.model_dump(exclude_unset=True)
        db_product = await crud_product.update(
            db, db_obj=db_product, obj_in=update_data
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
    product_id: UUID = FastAPIPath(..., description="Product ID"),
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
            db,
            id=product_id,
            quantity=stock_update.quantity,
            operation=stock_update.operation
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
    product_id: UUID = FastAPIPath(..., description="Product ID")
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


@router.get("/products/brands", response_model=List[str])
async def get_brands(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all distinct product brands.
    """
    try:
        brands = await crud_product.get_brands(db)
        return brands
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving brands: {str(e)}"
        )


@router.get("/products/tags", response_model=List[str])
async def get_tags(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all unique tags across products.
    """
    try:
        tags = await crud_product.get_tags(db)
        return tags
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving tags: {str(e)}"
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


@router.get("/uploads/products/{filename}")
async def get_uploaded_image(filename: str):
    """
    Serve uploaded product images.
    """
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)


@router.get("/products/search/tags", response_model=List[ProductResponse])
async def search_products_by_tags(
    tags: str = Query(..., description="Comma-separated tags to search for"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search products by tags.
    """
    try:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if not tag_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one tag is required"
            )
        
        products = await crud_product.search_by_tags(
            db,
            tags=tag_list,
            limit=limit
        )
        return products
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching products: {str(e)}"
        )