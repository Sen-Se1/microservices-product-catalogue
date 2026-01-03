#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from app.db.redis_client import get_async_redis, check_redis_health
from app.services.redis_service import RedisService

async def test_redis_connection():
    """Test Redis connection and basic operations"""
    print("🔍 Testing Redis connection...")
    
    # Test connection
    healthy = await check_redis_health()
    if not healthy:
        print("❌ Redis connection failed")
        return False
    
    print("✅ Redis connection successful")
    
    # Get Redis client
    redis_client = await get_async_redis()
    redis_service = RedisService(redis_client)
    
    # Test basic operations
    try:
        # Test increment
        await redis_service.increment_product_view("test-product-123", "test-user-456")
        print("✅ Product view tracking works")
        
        # Test sales tracking
        await redis_service.track_sale_realtime("test-product-123", 99.99)
        print("✅ Sales tracking works")
        
        # Test metrics
        metrics = await redis_service.get_realtime_metrics()
        print(f"✅ Real-time metrics: {metrics}")
        
        # Test caching
        test_data = {"test": "data", "number": 123}
        await redis_service.cache_report("test_report", test_data, 60)
        cached = await redis_service.get_cached_report("test_report")
        
        if cached == test_data:
            print("✅ Caching works")
        else:
            print("❌ Caching failed")
        
        # Clean up test data
        await redis_service.invalidate_cache("analytics:cache:test_report")
        
        print("\n🎉 All Redis tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run async test
    success = asyncio.run(test_redis_connection())
    sys.exit(0 if success else 1)