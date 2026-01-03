from redis.asyncio import Redis
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

class RedisService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def increment_product_view(self, product_id: str, user_id: Optional[str] = None):
        """
        Increment real-time view counter for a product
        
        Args:
            product_id: UUID of the product
            user_id: Optional user ID (if logged in)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Increment today's total views
        await self.redis.incr(f"analytics:daily:views:{today}")
        
        # Increment product-specific views
        product_key = f"analytics:product:{product_id}:views:{today}"
        await self.redis.incr(product_key)
        await self.redis.expire(product_key, 86400)  # 24 hours
        
        # Add user to today's unique visitors set (if logged in)
        if user_id:
            unique_key = f"analytics:daily:unique_visitors:{today}"
            await self.redis.sadd(unique_key, user_id)
            await self.redis.expire(unique_key, 86400)  # 24 hours
        
        # Update real-time active users (with 5-minute expiration)
        if user_id:
            active_users_key = "analytics:realtime:active_users"
            await self.redis.sadd(active_users_key, user_id)
            await self.redis.expire(active_users_key, 300)  # 5 minutes
    
    async def track_sale_realtime(self, product_id: str, amount: float):
        """
        Track sale in real-time counters
        
        Args:
            product_id: UUID of the product
            amount: Sale amount
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Increment today's sales amount
        sales_amount_key = f"analytics:daily:sales:{today}"
        await self.redis.incrbyfloat(sales_amount_key, amount)
        await self.redis.expire(sales_amount_key, 86400)  # 24 hours
        
        # Increment today's sales count
        sales_count_key = f"analytics:daily:sales_count:{today}"
        await self.redis.incr(sales_count_key)
        await self.redis.expire(sales_count_key, 86400)  # 24 hours
        
        # Increment product sales
        product_sales_key = f"analytics:product:{product_id}:sales:{today}"
        await self.redis.incrbyfloat(product_sales_key, amount)
        await self.redis.expire(product_sales_key, 86400)  # 24 hours
    
    async def get_realtime_metrics(self) -> Dict[str, Any]:
        """
        Get real-time metrics from Redis
        
        Returns:
            Dictionary with real-time metrics
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Use pipeline for multiple operations
        async with self.redis.pipeline() as pipe:
            # Today's views
            pipe.get(f"analytics:daily:views:{today}")
            
            # Today's unique visitors count
            pipe.scard(f"analytics:daily:unique_visitors:{today}")
            
            # Today's sales amount
            pipe.get(f"analytics:daily:sales:{today}")
            
            # Today's sales count
            pipe.get(f"analytics:daily:sales_count:{today}")
            
            # Active users (last 5 minutes)
            pipe.scard("analytics:realtime:active_users")
            
            # Execute all commands
            results = await pipe.execute()
        
        # Parse results
        today_views = int(results[0] or 0)
        unique_visitors = results[1] or 0
        today_sales = float(results[2] or 0)
        sales_count = int(results[3] or 0)
        active_users = results[4] or 0
        
        # Calculate conversion rate
        conversion_rate = 0.0
        if today_views > 0:
            conversion_rate = round((sales_count / today_views) * 100, 2)
        
        # Get top products for today (from sorted set)
        top_products_key = f"analytics:daily:top_products:{today}"
        top_products_raw = await self.redis.zrevrangebyscore(
            top_products_key, 
            '+inf', 
            '-inf', 
            start=0, 
            num=5, 
            withscores=True
        )
        
        top_products = []
        for product_id, score in top_products_raw:
            top_products.append({
                "product_id": product_id,
                "views": int(score)
            })
        
        return {
            "active_users": active_users,
            "today_views": today_views,
            "today_sales": today_sales,
            "sales_count": sales_count,
            "conversion_rate": conversion_rate,
            "unique_visitors": unique_visitors,
            "top_products": top_products
        }
    
    async def update_top_products(self, product_id: str, views: int = 1):
        """
        Update top products sorted set
        
        Args:
            product_id: UUID of the product
            views: Number of views to add (default: 1)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        key = f"analytics:daily:top_products:{today}"
        
        # Increment score in sorted set
        await self.redis.zincrby(key, views, product_id)
        await self.redis.expire(key, 86400)  # 24 hours
    
    async def cache_report(self, key: str, data: Any, ttl: int = 300):
        """
        Cache report data in Redis with TTL
        
        Args:
            key: Cache key
            data: Data to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 5 minutes)
        """
        await self.redis.setex(
            f"analytics:cache:{key}",
            ttl,
            json.dumps(data, default=str)
        )
    
    async def get_cached_report(self, key: str) -> Optional[Any]:
        """
        Get cached report data from Redis
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        cached = await self.redis.get(f"analytics:cache:{key}")
        if cached:
            try:
                return json.loads(cached)
            except json.JSONDecodeError:
                return None
        return None
    
    async def invalidate_cache(self, pattern: str = "analytics:cache:*"):
        """
        Invalidate cache entries matching a pattern
        
        Args:
            pattern: Redis key pattern (default: all analytics cache)
            
        Returns:
            Number of keys deleted
        """
        keys = await self.redis.keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0
    
    async def get_daily_stats(self, date_str: str) -> Dict[str, Any]:
        """
        Get daily statistics from Redis
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            Daily statistics
        """
        async with self.redis.pipeline() as pipe:
            pipe.get(f"analytics:daily:views:{date_str}")
            pipe.scard(f"analytics:daily:unique_visitors:{date_str}")
            pipe.get(f"analytics:daily:sales:{date_str}")
            pipe.get(f"analytics:daily:sales_count:{date_str}")
            
            results = await pipe.execute()
        
        return {
            "date": date_str,
            "views": int(results[0] or 0),
            "unique_visitors": results[1] or 0,
            "sales_amount": float(results[2] or 0),
            "sales_count": int(results[3] or 0)
        }
    
    async def get_product_stats(self, product_id: str, date_str: str) -> Dict[str, Any]:
        """
        Get product statistics for a specific date
        
        Args:
            product_id: UUID of the product
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            Product statistics
        """
        views_key = f"analytics:product:{product_id}:views:{date_str}"
        sales_key = f"analytics:product:{product_id}:sales:{date_str}"
        
        views = await self.redis.get(views_key)
        sales = await self.redis.get(sales_key)
        
        return {
            "product_id": product_id,
            "date": date_str,
            "views": int(views or 0),
            "sales": float(sales or 0)
        }
    
    async def flush_all_analytics(self):
        """
        Flush all analytics data from Redis (use with caution!)
        
        Returns:
            Boolean indicating success
        """
        try:
            # Get all analytics keys
            keys = await self.redis.keys("analytics:*")
            if keys:
                await self.redis.delete(*keys)
            return True
        except Exception as e:
            print(f"Error flushing analytics: {e}")
            return False