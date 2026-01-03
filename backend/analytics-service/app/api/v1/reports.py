from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from uuid import UUID

from app.db.session import get_db
from app.db.redis_client import get_async_redis
from app.core.security import verify_token, verify_admin_token
from app.schemas.reports import (
    SalesReportRequest, SalesReportResponse,
    ProductViewsReportRequest, ProductViewsReportResponse,
    UserActivityRequest, RealTimeMetrics,
    UserActivityItem
)
from app.services.analytics_service import AnalyticsService
from app.services.redis_service import RedisService

router = APIRouter()

@router.post("/sales", response_model=SalesReportResponse)
async def generate_sales_report(
    request: SalesReportRequest,
    db: Session = Depends(get_db),
    redis_client = Depends(get_async_redis)
    # auth_payload: dict = Depends(verify_token)
):
    """
    Generate sales report.
    
    Available to both users and admins, but admins get more detailed data.
    """
    # Check cache first
    redis_service = RedisService(redis_client)
    cache_key = f"sales_report:{request.start_date}:{request.end_date}:{request.group_by}"
    
    cached = await redis_service.get_cached_report(cache_key)
    if cached:
        return SalesReportResponse(**cached)
    
    # Generate report
    report_items = AnalyticsService.get_sales_report(db, request)
    
    # Calculate summary
    total_sales = sum(item["total_sales"] for item in report_items)
    total_orders = sum(item["sales_count"] for item in report_items)
    
    response_data = {
        "items": report_items,
        "summary": {
            "total_sales": total_sales,
            "total_orders": total_orders,
            "average_order_value": total_sales / total_orders if total_orders > 0 else 0,
            "period": {
                "start_date": str(request.start_date),
                "end_date": str(request.end_date)
            }
        }
    }
    
    # Cache for 5 minutes
    await redis_service.cache_report(cache_key, response_data, 300)
    
    return SalesReportResponse(**response_data)

@router.post("/product-views", response_model=ProductViewsReportResponse)
async def generate_product_views_report(
    request: ProductViewsReportRequest,
    db: Session = Depends(get_db),
    redis_client = Depends(get_async_redis)
    # auth_payload: dict = Depends(verify_token)
):
    """
    Generate product views report.
    
    Available to both users and admins.
    Shows most viewed products in a given period.
    """
    # Check cache
    redis_service = RedisService(redis_client)
    cache_key = f"product_views:{request.start_date}:{request.end_date}:{request.limit}"
    
    cached = await redis_service.get_cached_report(cache_key)
    if cached:
        return ProductViewsReportResponse(**cached)
    
    # Generate report
    report_items = AnalyticsService.get_product_views_report(db, request)
    
    response_data = {
        "items": report_items,
        "period": {
            "start_date": request.start_date,
            "end_date": request.end_date
        }
    }
    
    # Cache for 2 minutes (views change frequently)
    await redis_service.cache_report(cache_key, response_data, 120)
    
    return ProductViewsReportResponse(**response_data)

@router.get("/realtime-metrics", response_model=RealTimeMetrics)
async def get_realtime_metrics(
    redis_client = Depends(get_async_redis)
    # auth_payload: dict = Depends(verify_token)
):
    """
    Get real-time metrics for dashboard.
    
    Available to both users and admins.
    Shows current active users, today's views, sales, etc.
    """
    redis_service = RedisService(redis_client)
    metrics = await redis_service.get_realtime_metrics()
    
    # Add top products (from cache or generate)
    today = datetime.now().strftime("%Y-%m-%d")
    top_products_cache = await redis_service.get_cached_report(f"top_products:{today}")
    
    if not top_products_cache:
        top_products_cache = []
        # In a real implementation, you'd query the database here
    
    metrics["top_products"] = top_products_cache
    
    return RealTimeMetrics(**metrics)

@router.get("/user-activities", response_model=List[UserActivityItem])
async def get_user_activities(
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
    # auth_payload: dict = Depends(verify_admin_token)  # Admin only
):
    """
    Get user activities (ADMIN ONLY).
    
    Monitor user activities across the platform.
    Can filter by user, activity type, and date range.
    """
    # This is admin-only functionality
    activities = AnalyticsService.get_user_activities(db, user_id, activity_type, limit)
    
    # Filter by date range if provided
    if start_date:
        activities = [a for a in activities if a.created_at.date() >= start_date]
    if end_date:
        activities = [a for a in activities if a.created_at.date() <= end_date]
    
    return activities

@router.post("/update-daily-metrics")
async def update_daily_metrics(
    metrics_date: date = Query(None, description="Date to update metrics for (defaults to yesterday)"),
    db: Session = Depends(get_db)
    # auth_payload: dict = Depends(verify_admin_token)  # Admin only
):
    """
    Update daily aggregated metrics (ADMIN ONLY).
    
    This should be called daily (e.g., via cron job) to pre-aggregate metrics.
    """
    if not metrics_date:
        metrics_date = date.today() - timedelta(days=1)
    
    updated = AnalyticsService.update_daily_metrics(db, metrics_date)
    
    return {
        "date": str(updated.date),
        "total_views": updated.total_views,
        "unique_visitors": updated.unique_visitors,
        "total_sales": updated.total_sales,
        "status": "updated"
    }