from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.db.redis_client import get_async_redis
from app.core.security import verify_token, verify_admin_token
from app.schemas.tracking import ProductViewCreate, UserActivityCreate, SaleCreate, ProductViewResponse
from app.schemas.reports import SalesReportRequest, ProductViewsReportRequest, UserActivityRequest
from app.services.analytics_service import AnalyticsService
from app.services.redis_service import RedisService

router = APIRouter()

@router.post("/track/view", response_model=ProductViewResponse, status_code=status.HTTP_201_CREATED)
async def track_product_view(
    view_data: ProductViewCreate,
    db: Session = Depends(get_db),
    redis_client = Depends(get_async_redis)
    # auth_payload: dict = Depends(verify_token)
):
    """
    Track a product view.
    
    This endpoint should be called when a user views a product.
    Both public website and admin panel can call this.
    """
    # Track in PostgreSQL
    db_view = AnalyticsService.track_product_view(db, view_data)
    
    # Update real-time counters in Redis
    redis_service = RedisService(redis_client)
    await redis_service.increment_product_view(
        str(view_data.product_id),
        str(view_data.user_id) if view_data.user_id else None
    )
    
    return db_view

@router.post("/track/activity", status_code=status.HTTP_201_CREATED)
async def track_user_activity(
    activity_data: UserActivityCreate,
    db: Session = Depends(get_db)
    # auth_payload: dict = Depends(verify_admin_token)  # Admin only
):
    """
    Track user activity.
    
    Admin only endpoint for tracking detailed user activities.
    """
    activity = AnalyticsService.track_user_activity(db, activity_data)
    return {"id": activity.id, "status": "tracked"}

@router.post("/track/sale", status_code=status.HTTP_201_CREATED)
async def track_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    redis_client = Depends(get_async_redis)
    # auth_payload: dict = Depends(verify_token)
):
    """
    Track a sale.
    
    This endpoint should be called when a purchase is completed.
    Both public website and admin panel can call this.
    """
    # Track in PostgreSQL
    db_sale = AnalyticsService.track_sale(db, sale_data)
    
    # Update real-time counters in Redis
    redis_service = RedisService(redis_client)
    await redis_service.track_sale_realtime(
        str(sale_data.product_id),
        sale_data.amount
    )
    
    return {"id": db_sale.id, "status": "tracked"}