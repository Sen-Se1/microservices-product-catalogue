#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def init_database():
    # Create database if it doesn't exist
    admin_engine = create_engine(
        settings.DATABASE_URL.replace('/analytics_db', '/postgres')
    )
    
    with admin_engine.connect() as conn:
        conn.execute(text("COMMIT"))
        # Try to create database (will fail if exists, that's OK)
        try:
            conn.execute(text("CREATE DATABASE analytics_db"))
            print("Database created")
        except Exception as e:
            print(f"Database already exists or error: {e}")
    
    # Create tables
    from app.db.session import engine, Base
    from app.models.postgres_models import ProductView, UserActivity, Sale, DailyMetrics
    
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")

if __name__ == "__main__":
    init_database()