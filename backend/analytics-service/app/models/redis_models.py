from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

class RedisProductView(BaseModel):
    """Model for product view data in Redis"""
    product_id: str
    timestamp: float  # Unix timestamp
    user_id: Optional[str] = None
    session_id: str
    duration: int = 0
    
    def to_redis_hash(self) -> Dict[str, str]:
        """Convert to Redis hash format"""
        return {
            "product_id": self.product_id,
            "timestamp": str(self.timestamp),
            "user_id": self.user_id or "",
            "session_id": self.session_id,
            "duration": str(self.duration)
        }
    
    @classmethod
    def from_redis_hash(cls, data: Dict[str, str]) -> "RedisProductView":
        """Create from Redis hash"""
        return cls(
            product_id=data["product_id"],
            timestamp=float(data["timestamp"]),
            user_id=data["user_id"] if data["user_id"] else None,
            session_id=data["session_id"],
            duration=int(data["duration"])
        )

class RedisSession(BaseModel):
    """Model for user session tracking in Redis"""
    session_id: str
    user_id: Optional[str] = None
    created_at: float
    last_activity: float
    page_views: List[str] = Field(default_factory=list)  # List of product IDs viewed
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    def add_page_view(self, product_id: str):
        """Add a page view to the session"""
        self.page_views.append(product_id)
        self.last_activity = datetime.now().timestamp()
    
    def to_redis_hash(self) -> Dict[str, str]:
        """Convert to Redis hash format"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id or "",
            "created_at": str(self.created_at),
            "last_activity": str(self.last_activity),
            "page_views": ",".join(self.page_views),
            "ip_address": self.ip_address or "",
            "user_agent": self.user_agent or ""
        }
    
    @classmethod
    def from_redis_hash(cls, data: Dict[str, str]) -> "RedisSession":
        """Create from Redis hash"""
        page_views = data.get("page_views", "").split(",") if data.get("page_views") else []
        return cls(
            session_id=data["session_id"],
            user_id=data["user_id"] if data["user_id"] else None,
            created_at=float(data["created_at"]),
            last_activity=float(data["last_activity"]),
            page_views=page_views,
            ip_address=data["ip_address"] if data["ip_address"] else None,
            user_agent=data["user_agent"] if data["user_agent"] else None
        )

class RedisDailyMetrics(BaseModel):
    """Model for daily metrics in Redis"""
    date: str  # YYYY-MM-DD
    total_views: int = 0
    unique_visitors: int = 0
    total_sales: float = 0.0
    sales_count: int = 0
    top_products: List[Dict[str, Any]] = Field(default_factory=list)
    updated_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    
    def to_redis_hash(self) -> Dict[str, str]:
        """Convert to Redis hash format"""
        import json
        return {
            "date": self.date,
            "total_views": str(self.total_views),
            "unique_visitors": str(self.unique_visitors),
            "total_sales": str(self.total_sales),
            "sales_count": str(self.sales_count),
            "top_products": json.dumps(self.top_products),
            "updated_at": str(self.updated_at)
        }
    
    @classmethod
    def from_redis_hash(cls, data: Dict[str, str]) -> "RedisDailyMetrics":
        """Create from Redis hash"""
        import json
        top_products = json.loads(data.get("top_products", "[]"))
        return cls(
            date=data["date"],
            total_views=int(data.get("total_views", "0")),
            unique_visitors=int(data.get("unique_visitors", "0")),
            total_sales=float(data.get("total_sales", "0")),
            sales_count=int(data.get("sales_count", "0")),
            top_products=top_products,
            updated_at=float(data.get("updated_at", "0"))
        )

class RedisCacheEntry(BaseModel):
    """Model for cached data in Redis"""
    key: str
    data: Any
    ttl: int  # Time to live in seconds
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        current_time = datetime.now().timestamp()
        return (current_time - self.created_at) > self.ttl
    
    def to_redis_string(self) -> str:
        """Convert to Redis string format"""
        import json
        cache_data = {
            "data": self.data,
            "ttl": self.ttl,
            "created_at": self.created_at
        }
        return json.dumps(cache_data, default=str)
    
    @classmethod
    def from_redis_string(cls, key: str, data_str: str) -> "RedisCacheEntry":
        """Create from Redis string"""
        import json
        cache_data = json.loads(data_str)
        return cls(
            key=key,
            data=cache_data["data"],
            ttl=cache_data["ttl"],
            created_at=cache_data["created_at"]
        )

# Redis Key Patterns as constants
class RedisKeys:
    """Constants for Redis key patterns"""
    
    # Daily metrics
    DAILY_VIEWS = "analytics:daily:views:{date}"
    DAILY_UNIQUE_VISITORS = "analytics:daily:unique_visitors:{date}"
    DAILY_SALES = "analytics:daily:sales:{date}"
    DAILY_SALES_COUNT = "analytics:daily:sales_count:{date}"
    
    # Product-specific
    PRODUCT_VIEWS = "analytics:product:{product_id}:views:{date}"
    PRODUCT_SALES = "analytics:product:{product_id}:sales:{date}"
    
    # Real-time
    REALTIME_ACTIVE_USERS = "analytics:realtime:active_users"
    REALTIME_SESSIONS = "analytics:session:{session_id}"
    
    # Top products (sorted set)
    TOP_PRODUCTS = "analytics:daily:top_products:{date}"
    
    # Cache
    CACHE_PREFIX = "analytics:cache:{key}"
    
    @classmethod
    def format_key(cls, pattern: str, **kwargs) -> str:
        """Format a Redis key pattern with values"""
        return pattern.format(**kwargs)