from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_
from slugify.slugify import slugify as create_slug
from decimal import Decimal
from app.models.product import Product


class CRUDProduct:
    def __init__(self, model: Product):
        self.model = model
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[Product]:
        """Get a single product by ID"""
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_slug(self, db: AsyncSession, slug: str) -> Optional[Product]:
        """Get a single product by slug"""
        result = await db.execute(
            select(self.model).where(self.model.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def get_by_sku(self, db: AsyncSession, sku: str) -> Optional[Product]:
        """Get a single product by SKU"""
        result = await db.execute(
            select(self.model).where(self.model.sku == sku.upper())
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        discount_min: Optional[float] = None,
        discount_max: Optional[float] = None,
        tags: Optional[List[str]] = None,
        in_stock: Optional[bool] = None,
        active_only: bool = True,
        search: Optional[str] = None
    ) -> List[Product]:
        """Get multiple products with optional filters"""
        query = select(self.model)
        
        if active_only:
            query = query.where(self.model.is_active == True)
        
        if category_id:
            query = query.where(self.model.category_id == category_id)
        
        if brand:
            query = query.where(self.model.brand == brand)
        
        if min_price is not None:
            query = query.where(self.model.price >= min_price)
        
        if max_price is not None:
            query = query.where(self.model.price <= max_price)
        
        if discount_min is not None:
            query = query.where(self.model.discount_percentage >= discount_min)
        
        if discount_max is not None:
            query = query.where(self.model.discount_percentage <= discount_max)
        
        if tags:
            for tag in tags:
                query = query.where(self.model.tags.contains([tag.lower()]))
        
        if in_stock is True:
            query = query.where(self.model.stock_quantity > 0)
        elif in_stock is False:
            query = query.where(self.model.stock_quantity == 0)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                (self.model.name.ilike(search_term)) |
                (self.model.description.ilike(search_term)) |
                (self.model.sku.ilike(search_term)) |
                (self.model.brand.ilike(search_term))
            )
        
        query = query.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_count(
        self,
        db: AsyncSession,
        *,
        category_id: Optional[str] = None,
        brand: Optional[str] = None,
        active_only: bool = True
    ) -> int:
        """Count products with optional filters"""
        query = select(func.count()).select_from(self.model)
        
        if active_only:
            query = query.where(self.model.is_active == True)
        
        if category_id:
            query = query.where(self.model.category_id == category_id)
        
        if brand:
            query = query.where(self.model.brand == brand)
        
        result = await db.execute(query)
        return result.scalar()
    
    async def create(
        self,
        db: AsyncSession,
        *,
        name: str,
        sku: str,
        price: Decimal,
        description: Optional[str] = None,
        category_id: Optional[str] = None,
        brand: Optional[str] = None,
        stock_quantity: int = 0,
        low_stock_threshold: int = 10,
        discount_percentage: Decimal = Decimal('0'),
        tags: Optional[List[str]] = None,
        product_metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[UUID] = None,
        thumbnail_url: Optional[str] = None,
        image_urls: Optional[List[str]] = None
    ) -> Product:
        """Create a new product with optional images"""
        # Generate slug from name
        slug = create_slug(name)
        
        # Check if slug exists and make unique
        existing = await self.get_by_slug(db, slug)
        counter = 1
        original_slug = slug
        while existing:
            slug = f"{original_slug}-{counter}"
            existing = await self.get_by_slug(db, slug)
            counter += 1
        
        # Ensure tags are lowercase
        processed_tags = [tag.lower() for tag in (tags or [])]
        
        # Create database object
        db_obj = self.model(
            name=name,
            slug=slug,
            description=description,
            sku=sku.upper(),
            category_id=category_id,
            brand=brand,
            price=price,
            stock_quantity=stock_quantity,
            low_stock_threshold=low_stock_threshold,
            discount_percentage=discount_percentage,
            tags=processed_tags,
            product_metadata=product_metadata or {},
            created_by=created_by,
            thumbnail=thumbnail_url,
            images=image_urls or []
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Product,
        obj_in: Dict[str, Any]
    ) -> Product:
        """Update a product"""
        # Update slug if name is being changed
        if "name" in obj_in and obj_in["name"] != db_obj.name:
            obj_in["slug"] = create_slug(obj_in["name"])
        
        # Update SKU to uppercase if provided
        if "sku" in obj_in:
            obj_in["sku"] = obj_in["sku"].upper()
        
        # Ensure tags are lowercase if updating
        if "tags" in obj_in and obj_in["tags"] is not None:
            obj_in["tags"] = [tag.lower() for tag in obj_in["tags"]]
        
        for field in obj_in:
            setattr(db_obj, field, obj_in[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def remove(self, db: AsyncSession, *, id: UUID) -> Optional[Product]:
        """Delete a product (soft delete by setting is_active=False)"""
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(is_active=False)
            .returning(self.model)
        )
        
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    
    async def update_stock(
        self,
        db: AsyncSession,
        *,
        id: UUID,
        quantity: int,
        operation: str = "set"
    ) -> Optional[Product]:
        """Update product stock quantity"""
        product = await self.get(db, id)
        if not product:
            return None
        
        if operation == "set":
            new_quantity = quantity
        elif operation == "add":
            new_quantity = product.stock_quantity + quantity
        elif operation == "subtract":
            new_quantity = product.stock_quantity - quantity
            if new_quantity < 0:
                new_quantity = 0
        
        product.stock_quantity = new_quantity
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product
    
    async def get_low_stock(self, db: AsyncSession) -> List[Product]:
        """Get products with stock below threshold"""
        query = select(self.model).where(
            and_(
                self.model.stock_quantity <= self.model.low_stock_threshold,
                self.model.is_active == True
            )
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_categories(self, db: AsyncSession) -> List[str]:
        """Get distinct product categories"""
        query = select(self.model.category_id).distinct().where(
            self.model.category_id.is_not(None),
            self.model.is_active == True
        ).order_by(self.model.category_id)
        
        result = await db.execute(query)
        return [row[0] for row in result.all() if row[0]]
    
    async def get_brands(self, db: AsyncSession) -> List[str]:
        """Get distinct product brands"""
        query = select(self.model.brand).distinct().where(
            self.model.brand.is_not(None),
            self.model.is_active == True
        ).order_by(self.model.brand)
        
        result = await db.execute(query)
        return [row[0] for row in result.all() if row[0]]
    
    async def get_tags(self, db: AsyncSession) -> List[str]:
        """Get all unique tags across products"""
        query = select(self.model.tags).where(
            self.model.tags.is_not(None),
            self.model.is_active == True
        )
        
        result = await db.execute(query)
        all_tags = set()
        for row in result.all():
            if row[0]:
                all_tags.update(row[0])
        
        return sorted(list(all_tags))
    
    async def add_images(
        self,
        db: AsyncSession,
        *,
        product_id: UUID,
        thumbnail_url: Optional[str] = None,
        image_urls: List[str] = []
    ) -> Optional[Product]:
        """Add images to an existing product"""
        product = await self.get(db, product_id)
        if not product:
            return None
        
        if thumbnail_url:
            product.thumbnail = thumbnail_url
        
        if image_urls:
            existing_images = product.images or []
            product.images = existing_images + image_urls
        
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product
    
    async def search_by_tags(
        self,
        db: AsyncSession,
        *,
        tags: List[str],
        limit: int = 50
    ) -> List[Product]:
        """Search products by tags (any matching tag)"""
        if not tags:
            return []
        
        tags_lower = [tag.lower() for tag in tags]
        
        query = select(self.model).where(
            and_(
                self.model.is_active == True,
                self.model.tags.overlap(tags_lower)
            )
        ).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()


product = CRUDProduct(Product)