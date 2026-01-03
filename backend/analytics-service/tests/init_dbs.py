#!/usr/bin/env python3
"""
Initialize database schema for Analytics Service
"""

import sys
import os
import asyncio

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def initialize_database():
    """Create database tables"""
    print("Initializing Analytics Service Database...")
    
    try:
        from app.db.session import engine, Base
        from app.models.postgres_models import ProductView, UserActivity, Sale, DailyMetrics
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        print("\nCreated tables:")
        print("  - product_views")
        print("  - user_activities")
        print("  - sales")
        print("  - daily_metrics")
        
        # Verify table creation
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n✅ Found {len(tables)} tables in database:")
        for table in tables:
            print(f"  - {table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_test_data():
    """Create sample test data"""
    print("\nCreating test data...")
    
    try:
        from app.db.session import SessionLocal
        from app.models.postgres_models import ProductView, UserActivity, Sale
        from datetime import datetime, timedelta
        import uuid
        
        db = SessionLocal()
        
        # Create test product views
        for i in range(5):
            view = ProductView(
                id=uuid.uuid4(),
                product_id=uuid.uuid4(),
                user_id=uuid.uuid4() if i % 2 == 0 else None,
                session_id=f"session_{i}",
                duration_seconds=i * 30,
                device_info={"browser": "Chrome", "os": "Windows"},
                ip_address=f"192.168.1.{i}",
                user_agent="Mozilla/5.0"
            )
            db.add(view)
        
        # Create test user activities
        activity_types = ['login', 'logout', 'view', 'search', 'purchase']
        for i, activity_type in enumerate(activity_types):
            activity = UserActivity(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                activity_type=activity_type,
                activity_data={"test": True, "iteration": i},
                ip_address=f"10.0.0.{i}",
                user_agent="Test Agent"
            )
            db.add(activity)
        
        # Create test sales
        for i in range(3):
            sale = Sale(
                id=uuid.uuid4(),
                order_id=uuid.uuid4(),
                product_id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                amount=99.99 * (i + 1),
                quantity=i + 1,
                sale_date=datetime.now().date() - timedelta(days=i),
                payment_method="credit_card",
                region="US"
            )
            db.add(sale)
        
        db.commit()
        print("✅ Test data created successfully!")
        
        # Verify counts
        view_count = db.query(ProductView).count()
        activity_count = db.query(UserActivity).count()
        sale_count = db.query(Sale).count()
        
        print(f"\nData counts:")
        print(f"  - Product Views: {view_count}")
        print(f"  - User Activities: {activity_count}")
        print(f"  - Sales: {sale_count}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Test data creation failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("   ANALYTICS SERVICE DATABASE INITIALIZATION")
    print("="*60)
    
    # Step 1: Create tables
    if not initialize_database():
        print("\n❌ Failed to initialize database")
        sys.exit(1)
    
    # Step 2: Create test data (optional)
    create_test = input("\nCreate test data? (y/n): ").lower().strip()
    if create_test == 'y':
        create_test_data()
    
    print("\n" + "="*60)
    print("✅ DATABASE INITIALIZATION COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Start the service: python -m app.main")
    print("2. Access API docs: http://localhost:8003/docs")
    print("3. Test endpoints with: python test_endpoints.py")