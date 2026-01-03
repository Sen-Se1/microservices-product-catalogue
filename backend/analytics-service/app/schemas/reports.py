from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID

class DateRange(BaseModel):
    start_date: date
    end_date: date

class SalesReportRequest(DateRange):
    group_by: Optional[str] = Field("day", pattern="^(day|week|month|product|user)$")
    product_id: Optional[UUID] = None
    user_id: Optional[UUID] = None

class SalesReportItem(BaseModel):
    period: str
    total_sales: float
    sales_count: int
    average_order_value: float

class SalesReportResponse(BaseModel):
    items: List[SalesReportItem]
    summary: Dict[str, Any]

class ProductViewsReportRequest(DateRange):
    product_id: Optional[UUID] = None
    limit: int = Field(10, ge=1, le=100)

class ProductViewItem(BaseModel):
    product_id: UUID
    view_count: int
    unique_viewers: int
    average_duration: float

class ProductViewsReportResponse(BaseModel):
    items: List[ProductViewItem]
    period: DateRange

class UserActivityRequest(DateRange):
    user_id: Optional[UUID] = None
    activity_type: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)

class UserActivityItem(BaseModel):
    id: UUID
    user_id: UUID
    activity_type: str
    created_at: datetime
    ip_address: Optional[str]
    
    class Config:
        from_attributes = True

class RealTimeMetrics(BaseModel):
    active_users: int
    today_views: int
    today_sales: float
    conversion_rate: float
    top_products: List[Dict[str, Any]]