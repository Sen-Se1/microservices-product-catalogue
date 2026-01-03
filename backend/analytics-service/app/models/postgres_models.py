from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Date, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.session import Base
import uuid

class ProductView(Base):
    __tablename__ = "product_views"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # Null for anonymous users
    session_id = Column(String, nullable=False)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())
    duration_seconds = Column(Integer, default=0)
    device_info = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String, nullable=True)
    
    __table_args__ = (
        Index('idx_product_view_product', 'product_id'),
        Index('idx_product_view_user', 'user_id'),
        Index('idx_product_view_time', 'viewed_at'),
    )

class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    activity_type = Column(String(50), nullable=False)  # login, logout, view, purchase, search
    activity_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String, nullable=True)
    
    __table_args__ = (
        Index('idx_user_activity_user', 'user_id'),
        Index('idx_user_activity_type', 'activity_type'),
        Index('idx_user_activity_time', 'created_at'),
    )

class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    amount = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    sale_date = Column(Date, nullable=False)
    payment_method = Column(String(50), nullable=True)
    region = Column(String(100), nullable=True)
    
    __table_args__ = (
        Index('idx_sale_product', 'product_id'),
        Index('idx_sale_user', 'user_id'),
        Index('idx_sale_date', 'sale_date'),
    )

class DailyMetrics(Base):
    __tablename__ = "daily_metrics"
    
    date = Column(Date, primary_key=True)
    total_views = Column(Integer, default=0)
    unique_visitors = Column(Integer, default=0)
    total_sales = Column(Float, default=0.0)
    sales_count = Column(Integer, default=0)
    top_products = Column(JSON, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())