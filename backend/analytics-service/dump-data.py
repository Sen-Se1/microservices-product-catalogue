#!/usr/bin/env python3
"""
create_test_data.py
Creates minimal test data for Analytics Service
"""

import sys
import os
from datetime import datetime, timedelta
import uuid
import json
import asyncio
import random

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_header(text):
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def create_postgres_test_data():
    """Create minimal test data in PostgreSQL"""
    try:
        from app.db.session import SessionLocal
        from app.models.postgres_models import ProductView, UserActivity, Sale, DailyMetrics
        
        db = SessionLocal()
        today = datetime.now().date()
        
        print("📊 Creating PostgreSQL test data...")
        
        # Clear existing test data (optional)
        db.query(ProductView).delete()
        db.query(UserActivity).delete()
        db.query(Sale).delete()
        db.query(DailyMetrics).delete()
        db.commit()
        
        # Generate test UUIDs
        test_user_ids = [uuid.uuid4() for _ in range(3)]
        test_product_ids = [uuid.uuid4() for _ in range(5)]
        
        # 1. Product Views (5 records)
        print("  Creating product views...")
        for i in range(5):
            view = ProductView(
                id=uuid.uuid4(),
                product_id=test_product_ids[i % len(test_product_ids)],
                user_id=test_user_ids[i % len(test_user_ids)] if i < 3 else None,  # Some anonymous
                session_id=f"test_session_{i}",
                viewed_at=datetime.now() - timedelta(hours=i*3),
                duration_seconds=random.randint(10, 180),
                device_info={"browser": random.choice(["Chrome", "Firefox", "Safari"]),
                           "os": random.choice(["Windows", "macOS", "Linux"]),
                           "mobile": random.choice([True, False])},
                ip_address=f"192.168.1.{i+10}",
                user_agent=f"Mozilla/5.0 Test Browser {i}"
            )
            db.add(view)
        
        # 2. User Activities (4 records)
        print("  Creating user activities...")
        activity_types = ['login', 'view', 'search', 'logout']
        for i, activity_type in enumerate(activity_types):
            activity = UserActivity(
                id=uuid.uuid4(),
                user_id=test_user_ids[i % len(test_user_ids)],
                activity_type=activity_type,
                activity_data={"test": True, "action": activity_type, "page": f"/product/{i}"},
                created_at=datetime.now() - timedelta(hours=i*2),
                ip_address=f"10.0.0.{i+10}",
                user_agent=f"Test Client {i}"
            )
            db.add(activity)
        
        # 3. Sales (3 records)
        print("  Creating sales records...")
        for i in range(3):
            sale = Sale(
                id=uuid.uuid4(),
                order_id=uuid.uuid4(),
                product_id=test_product_ids[i],
                user_id=test_user_ids[i],
                amount=round(random.uniform(20.0, 150.0), 2),
                quantity=random.randint(1, 3),
                sale_date=today - timedelta(days=i),
                payment_method=random.choice(["credit_card", "paypal", "stripe"]),
                region=random.choice(["US-NY", "US-CA", "GB-LND", "DE-BER"])
            )
            db.add(sale)
        
        # 4. Daily Metrics (3 days)
        print("  Creating daily metrics...")
        for i in range(3):
            metric_date = today - timedelta(days=i)
            metrics = DailyMetrics(
                date=metric_date,
                total_views=random.randint(50, 200),
                unique_visitors=random.randint(10, 50),
                total_sales=round(random.uniform(500.0, 2000.0), 2),
                sales_count=random.randint(5, 20),
                top_products=[
                    {"product_id": str(test_product_ids[0]), "views": random.randint(30, 100)},
                    {"product_id": str(test_product_ids[1]), "views": random.randint(20, 80)},
                    {"product_id": str(test_product_ids[2]), "views": random.randint(10, 50)}
                ]
            )
            db.add(metrics)
        
        db.commit()
        
        # Show counts
        view_count = db.query(ProductView).count()
        activity_count = db.query(UserActivity).count()
        sale_count = db.query(Sale).count()
        metric_count = db.query(DailyMetrics).count()
        
        print(f"✅ PostgreSQL data created:")
        print(f"   • Product Views: {view_count}")
        print(f"   • User Activities: {activity_count}")
        print(f"   • Sales: {sale_count}")
        print(f"   • Daily Metrics: {metric_count}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL data creation failed: {type(e).__name__}: {e}")
        return False

async def create_redis_test_data():
    """Create minimal test data in Redis"""
    try:
        from app.db.redis_client import get_async_redis
        from app.services.redis_service import RedisService
        
        print("\n🔴 Creating Redis test data...")
        
        redis_client = await get_async_redis()
        redis_service = RedisService(redis_client)
        
        # Clear existing analytics data
        keys = await redis_client.keys("analytics:*")
        if keys:
            await redis_client.delete(*keys)
            print("  Cleared existing analytics data")
        
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # 1. Today's counters
        print("  Setting today's counters...")
        await redis_client.set(f"analytics:daily:views:{today}", 47)
        await redis_client.set(f"analytics:daily:sales:{today}", 299.97)
        await redis_client.set(f"analytics:daily:sales_count:{today}", 3)
        
        # 2. Yesterday's counters (for date range testing)
        await redis_client.set(f"analytics:daily:views:{yesterday}", 38)
        await redis_client.set(f"analytics:daily:sales:{yesterday}", 450.50)
        await redis_client.set(f"analytics:daily:sales_count:{yesterday}", 4)
        
        # 3. Unique visitors sets
        print("  Creating unique visitor sets...")
        test_users = [f"user_{uuid.uuid4().hex[:8]}" for _ in range(5)]
        for user_id in test_users[:3]:  # 3 visitors today
            await redis_client.sadd(f"analytics:daily:unique_visitors:{today}", user_id)
        for user_id in test_users[2:]:  # 3 visitors yesterday (2 overlapping)
            await redis_client.sadd(f"analytics:daily:unique_visitors:{yesterday}", user_id)
        
        # 4. Active users (real-time)
        print("  Setting active users...")
        await redis_client.sadd("analytics:realtime:active_users", test_users[0])
        await redis_client.sadd("analytics:realtime:active_users", test_users[1])
        await redis_client.expire("analytics:realtime:active_users", 300)  # 5 minutes
        
        # 5. Top products (sorted sets)
        print("  Creating top products ranking...")
        test_products = [f"prod_{uuid.uuid4().hex[:8]}" for _ in range(4)]
        for i, product_id in enumerate(test_products):
            score = (len(test_products) - i) * 15  # 60, 45, 30, 15 views
            await redis_client.zadd(f"analytics:daily:top_products:{today}", {product_id: score})
            # Also add some for yesterday
            await redis_client.zadd(f"analytics:daily:top_products:{yesterday}", {product_id: score//2})
        
        # 6. Product-specific counters
        print("  Setting product-specific counters...")
        for i, product_id in enumerate(test_products[:2]):  # First 2 products
            await redis_client.set(f"analytics:product:{product_id}:views:{today}", 20 + i*10)
            await redis_client.set(f"analytics:product:{product_id}:sales:{today}", 100.0 + i*50)
        
        # 7. Cache some reports (for testing cache functionality)
        print("  Caching sample reports...")
        sample_report = {
            "items": [
                {"period": today, "total_sales": 299.97, "sales_count": 3},
                {"period": yesterday, "total_sales": 450.50, "sales_count": 4}
            ],
            "summary": {
                "total_sales": 750.47,
                "total_orders": 7,
                "average_order_value": 107.21
            }
        }
        await redis_service.cache_report(f"sales_report:{today}:{yesterday}", sample_report, 600)
        
        # Verify
        today_views = await redis_client.get(f"analytics:daily:views:{today}")
        unique_today = await redis_client.scard(f"analytics:daily:unique_visitors:{today}")
        active_users = await redis_client.scard("analytics:realtime:active_users")
        top_products_count = await redis_client.zcard(f"analytics:daily:top_products:{today}")
        
        print(f"✅ Redis data created:")
        print(f"   • Today's views: {today_views}")
        print(f"   • Unique visitors today: {unique_today}")
        print(f"   • Active users now: {active_users}")
        print(f"   • Top products tracked: {top_products_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis data creation failed: {type(e).__name__}: {e}")
        return False

def verify_test_data():
    """Verify the test data was created successfully"""
    print("\n🔍 Verifying test data...")
    
    try:
        from app.db.session import SessionLocal
        from app.models.postgres_models import ProductView, UserActivity, Sale, DailyMetrics
        
        db = SessionLocal()
        
        # Check PostgreSQL
        print("  PostgreSQL:")
        print(f"    • Product Views: {db.query(ProductView).count()}")
        print(f"    • User Activities: {db.query(UserActivity).count()}")
        print(f"    • Sales: {db.query(Sale).count()}")
        print(f"    • Daily Metrics: {db.query(DailyMetrics).count()}")
        
        # Show sample data
        latest_sale = db.query(Sale).order_by(Sale.sale_date.desc()).first()
        if latest_sale:
            print(f"    • Latest sale: ${latest_sale.amount} on {latest_sale.sale_date}")
        
        db.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

async def main():
    """Main function to create test data"""
    import random
    
    print_header("ANALYTICS SERVICE TEST DATA CREATION")
    print("Creating minimal test data for development...")
    
    # Create PostgreSQL data
    pg_success = create_postgres_test_data()
    if not pg_success:
        print("❌ Failed to create PostgreSQL data")
        return False
    
    # Create Redis data
    redis_success = await create_redis_test_data()
    if not redis_success:
        print("❌ Failed to create Redis data")
        return False
    
    # Verify
    verify_test_data()
    
    print_header("✅ TEST DATA CREATION COMPLETE")
    print("\n📋 Test data summary:")
    print("PostgreSQL:")
    print("  • 5 product views (mixed users/devices)")
    print("  • 4 user activities (login, view, search, logout)")
    print("  • 3 sales records ($20-$150 range)")
    print("  • 3 daily metrics entries")
    print("\nRedis:")
    print("  • Today's views: 47")
    print("  • Today's sales: $299.97 (3 orders)")
    print("  • 3 unique visitors today")
    print("  • 2 active users now")
    print("  • 4 top products ranked")
    print("  • Cached sample report")
    
    print("\n🚀 Ready to test:")
    print("1. Start service: python -m app.main")
    print("2. Test endpoints: python test_endpoints.py")
    print("3. View data: http://localhost:8003/docs")
    
    return True

if __name__ == "__main__":
    # Initialize random for consistent test data
    random.seed(42)  # For reproducible test data
    
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)