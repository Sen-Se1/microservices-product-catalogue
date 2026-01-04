from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.orm import selectinload
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, StockUpdate
import re
from slugify import slugify


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
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: Optional[bool] = None,
        active_only: bool = True,
        search: Optional[str] = None
    ) -> List[Product]:
        """Get multiple products with optional filters"""
        query = select(self.model)
        
        if active_only:
            query = query.where(self.model.is_active == True)
        
        if category:
            query = query.where(self.model.category == category)
        
        if min_price is not None:
            query = query.where(self.model.price >= min_price)
        
        if max_price is not None:
            query = query.where(self.model.price <= max_price)
        
        if in_stock is True:
            query = query.where(self.model.stock_quantity > 0)
        elif in_stock is False:
            query = query.where(self.model.stock_quantity == 0)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                (self.model.name.ilike(search_term)) |
                (self.model.description.ilike(search_term)) |
                (self.model.sku.ilike(search_term))
            )
        
        query = query.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_count(
        self,
        db: AsyncSession,
        *,
        category: Optional[str] = None,
        active_only: bool = True
    ) -> int:
        """Count products with optional filters"""
        query = select(func.count()).select_from(self.model)
        
        if active_only:
            query = query.where(self.model.is_active == True)
        
        if category:
            query = query.where(self.model.category == category)
        
        result = await db.execute(query)
        return result.scalar()
    
    async def create(self, db: AsyncSession, *, obj_in: ProductCreate) -> Product:
        """Create a new product"""
        # Generate slug from name
        slug = slugify(obj_in.name)
        
        # Check if slug exists and make unique
        existing = await self.get_by_slug(db, slug)
        counter = 1
        original_slug = slug
        while existing:
            slug = f"{original_slug}-{counter}"
            existing = await self.get_by_slug(db, slug)
            counter += 1
        
        # Create database object
        db_obj = self.model(
            **obj_in.model_dump(exclude={"slug"}),
            slug=slug
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
        obj_in: ProductUpdate
    ) -> Product:
        """Update a product"""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Update slug if name is being changed
        if "name" in update_data and update_data["name"] != db_obj.name:
            update_data["slug"] = slugify(update_data["name"])
        
        # Update SKU to uppercase if provided
        if "sku" in update_data:
            update_data["sku"] = update_data["sku"].upper()
        
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def remove(self, db: AsyncSession, *, id: UUID) -> Optional[Product]:
        """Delete a product (soft delete by setting is_active=False)"""
        # Soft delete instead of actual delete
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(is_active=False)
            .returning(self.model)
        )
        
        result = await db.execute(stmt)
        await db.commit()
        return result.scalar_one_or_none()
    
    async def hard_delete(self, db: AsyncSession, *, id: UUID) -> bool:
        """Permanently delete a product"""
        stmt = delete(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0
    
    async def update_stock(
        self,
        db: AsyncSession,
        *,
        id: UUID,
        stock_update: StockUpdate
    ) -> Optional[Product]:
        """Update product stock quantity"""
        product = await self.get(db, id)
        if not product:
            return None
        
        if stock_update.operation == "set":
            new_quantity = stock_update.quantity
        elif stock_update.operation == "add":
            new_quantity = product.stock_quantity + stock_update.quantity
        elif stock_update.operation == "subtract":
            new_quantity = product.stock_quantity - stock_update.quantity
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
        query = select(self.model.category).distinct().where(
            self.model.category.is_not(None),
            self.model.is_active == True
        ).order_by(self.model.category)
        
        result = await db.execute(query)
        return [row[0] for row in result.all() if row[0]]


product = CRUDProduct(Product)