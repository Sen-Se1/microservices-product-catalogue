import redis

def test_redis_connection():
    try:
        # Connect to Redis
        r = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        
        # Test connection
        response = r.ping()
        if response:
            print("✅ Redis connection successful!")
            
            # Test basic operations
            r.set('test_key', 'test_value')
            value = r.get('test_key')
            print(f"Test key value: {value}")
            
            r.delete('test_key')
            
            # Get Redis info
            info = r.info()
            print(f"Redis version: {info.get('redis_version')}")
            print(f"Used memory: {info.get('used_memory_human')}")
            
            return True
        else:
            print("❌ Redis ping failed")
            return False
            
    except redis.ConnectionError as e:
        print(f"❌ Redis connection failed: {e}")
        return False

if __name__ == "__main__":
    test_redis_connection()