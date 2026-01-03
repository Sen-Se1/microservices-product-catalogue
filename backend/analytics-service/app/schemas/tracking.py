from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class ProductViewCreate(BaseModel):
    product_id: UUID
    user_id: Optional[UUID] = None
    session_id: str = Field(..., min_length=1)
    duration_seconds: int = Field(0, ge=0)
    device_info: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class UserActivityCreate(BaseModel):
    user_id: UUID
    activity_type: str = Field(..., min_length=1)
    activity_data: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class SaleCreate(BaseModel):
    order_id: UUID
    product_id: UUID
    user_id: Optional[UUID] = None
    amount: float = Field(..., gt=0)
    quantity: int = Field(1, gt=0)
    sale_date: datetime
    payment_method: Optional[str] = None
    region: Optional[str] = None

class ProductViewResponse(BaseModel):
    id: UUID
    product_id: UUID
    user_id: Optional[UUID]
    viewed_at: datetime
    
    class Config:
        from_attributes = True