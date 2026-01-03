import redis
from redis.asyncio import Redis as AsyncRedis
from redis.exceptions import ConnectionError, TimeoutError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Synchronous Redis client (for background tasks, Celery, etc.)
try:
    redis_client = redis.Redis.from_url(
        settings.REDIS_URL, 
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    
    # Test connection
    redis_client.ping()
    logger.info("✅ Synchronous Redis connection established")
    
except (ConnectionError, TimeoutError) as e:
    logger.error(f"❌ Failed to connect to Redis (sync): {e}")
    redis_client = None

# Async Redis client (for FastAPI endpoints)
try:
    async_redis_client = AsyncRedis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    
    # Note: Can't test async connection in sync context
    logger.info("✅ Asynchronous Redis client initialized")
    
except Exception as e:
    logger.error(f"❌ Failed to initialize async Redis client: {e}")
    async_redis_client = None

def get_redis():
    """
    Get synchronous Redis client
    
    Returns:
        Redis client instance or None if connection failed
    """
    if redis_client is None:
        raise ConnectionError("Redis connection not available")
    return redis_client

async def get_async_redis():
    """
    Get asynchronous Redis client
    
    Returns:
        AsyncRedis client instance or None if connection failed
    """
    if async_redis_client is None:
        raise ConnectionError("Async Redis connection not available")
    
    # Test connection
    try:
        await async_redis_client.ping()
        return async_redis_client
    except Exception as e:
        logger.error(f"Redis connection test failed: {e}")
        raise ConnectionError(f"Redis connection failed: {e}")

async def check_redis_health() -> bool:
    """
    Check Redis health status
    
    Returns:
        Boolean indicating if Redis is healthy
    """
    try:
        if async_redis_client:
            await async_redis_client.ping()
            return True
    except Exception:
        pass
    return False

def get_redis_info() -> dict:
    """
    Get Redis server information
    
    Returns:
        Dictionary with Redis info or error message
    """
    try:
        if redis_client:
            info = redis_client.info()
            return {
                "version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "uptime_days": info.get("uptime_in_days"),
                "status": "connected"
            }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e)
        }
    return {"status": "unknown"}