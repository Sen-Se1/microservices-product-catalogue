from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
import json

from app.models.postgres_models import ProductView, UserActivity, Sale, DailyMetrics
from app.schemas.tracking import ProductViewCreate, UserActivityCreate, SaleCreate
from app.schemas.reports import SalesReportRequest, ProductViewsReportRequest

class AnalyticsService:
    @staticmethod
    def track_product_view(db: Session, view_data: ProductViewCreate):
        """Track a product view"""
        db_view = ProductView(**view_data.dict())
        db.add(db_view)
        db.commit()
        db.refresh(db_view)
        return db_view
    
    @staticmethod
    def track_user_activity(db: Session, activity_data: UserActivityCreate):
        """Track user activity"""
        db_activity = UserActivity(**activity_data.dict())
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity
    
    @staticmethod
    def track_sale(db: Session, sale_data: SaleCreate):
        """Track a sale"""
        # Convert datetime to date if needed
        sale_dict = sale_data.dict()
        if isinstance(sale_dict.get('sale_date'), datetime):
            sale_dict['sale_date'] = sale_dict['sale_date'].date()
        
        db_sale = Sale(**sale_dict)
        db.add(db_sale)
        db.commit()
        db.refresh(db_sale)
        return db_sale
    
    @staticmethod
    def get_sales_report(db: Session, request: SalesReportRequest) -> List[Dict[str, Any]]:
        """Generate sales report"""
        query = db.query(Sale).filter(
            Sale.sale_date >= request.start_date,
            Sale.sale_date <= request.end_date
        )
        
        if request.product_id:
            query = query.filter(Sale.product_id == request.product_id)
        if request.user_id:
            query = query.filter(Sale.user_id == request.user_id)
        
        if request.group_by == "day":
            results = query.with_entities(
                Sale.sale_date,
                func.sum(Sale.amount).label('total_sales'),
                func.count(Sale.id).label('sales_count'),
                func.avg(Sale.amount).label('avg_sale')
            ).group_by(Sale.sale_date).order_by(Sale.sale_date).all()
            
            return [
                {
                    "period": str(result.sale_date),
                    "total_sales": float(result.total_sales or 0),
                    "sales_count": result.sales_count or 0,
                    "average_order_value": float(result.avg_sale or 0)
                }
                for result in results
            ]
        
        elif request.group_by == "product":
            results = query.with_entities(
                Sale.product_id,
                func.sum(Sale.amount).label('total_sales'),
                func.sum(Sale.quantity).label('total_quantity'),
                func.count(Sale.id).label('sales_count')
            ).group_by(Sale.product_id).order_by(desc('total_sales')).all()
            
            return [
                {
                    "period": str(result.product_id),
                    "total_sales": float(result.total_sales or 0),
                    "sales_count": result.sales_count or 0,
                    "total_quantity": result.total_quantity or 0
                }
                for result in results
            ]
        
        return []
    
    @staticmethod
    def get_product_views_report(db: Session, request: ProductViewsReportRequest) -> List[Dict[str, Any]]:
        """Generate product views report"""
        query = db.query(
            ProductView.product_id,
            func.count(ProductView.id).label('view_count'),
            func.count(func.distinct(ProductView.user_id)).label('unique_viewers'),
            func.avg(ProductView.duration_seconds).label('avg_duration')
        ).filter(
            ProductView.viewed_at >= datetime.combine(request.start_date, datetime.min.time()),
            ProductView.viewed_at <= datetime.combine(request.end_date, datetime.max.time())
        ).group_by(ProductView.product_id).order_by(desc('view_count')).limit(request.limit)
        
        if request.product_id:
            query = query.filter(ProductView.product_id == request.product_id)
        
        results = query.all()
        
        return [
            {
                "product_id": result.product_id,
                "view_count": result.view_count or 0,
                "unique_viewers": result.unique_viewers or 0,
                "average_duration": float(result.avg_duration or 0)
            }
            for result in results
        ]
    
    @staticmethod
    def get_user_activities(db: Session, user_id: Optional[UUID] = None, 
                          activity_type: Optional[str] = None, 
                          limit: int = 100) -> List[UserActivity]:
        """Get user activities (admin only)"""
        query = db.query(UserActivity)
        
        if user_id:
            query = query.filter(UserActivity.user_id == user_id)
        if activity_type:
            query = query.filter(UserActivity.activity_type == activity_type)
        
        return query.order_by(desc(UserActivity.created_at)).limit(limit).all()
    
    @staticmethod
    def update_daily_metrics(db: Session, metrics_date: date):
        """Update daily aggregated metrics"""
        # Calculate metrics for the day
        views_query = db.query(
            func.count(ProductView.id).label('total_views'),
            func.count(func.distinct(ProductView.user_id)).label('unique_visitors')
        ).filter(
            func.date(ProductView.viewed_at) == metrics_date
        ).first()
        
        sales_query = db.query(
            func.sum(Sale.amount).label('total_sales'),
            func.count(Sale.id).label('sales_count')
        ).filter(Sale.sale_date == metrics_date).first()
        
        top_products = db.query(
            ProductView.product_id,
            func.count(ProductView.id).label('view_count')
        ).filter(
            func.date(ProductView.viewed_at) == metrics_date
        ).group_by(ProductView.product_id).order_by(desc('view_count')).limit(5).all()
        
        # Update or create daily metrics
        daily_metric = db.query(DailyMetrics).filter(DailyMetrics.date == metrics_date).first()
        
        if not daily_metric:
            daily_metric = DailyMetrics(date=metrics_date)
            db.add(daily_metric)
        
        daily_metric.total_views = views_query.total_views or 0
        daily_metric.unique_visitors = views_query.unique_visitors or 0
        daily_metric.total_sales = float(sales_query.total_sales or 0)
        daily_metric.sales_count = sales_query.sales_count or 0
        daily_metric.top_products = [
            {"product_id": str(product.product_id), "views": product.view_count}
            for product in top_products
        ]
        
        db.commit()
        return daily_metric