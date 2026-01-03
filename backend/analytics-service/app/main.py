from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.db.session import engine, Base
from app.db.redis_client import check_redis_health, get_redis_info
from app.api.v1.tracking import router as tracking_router
from app.api.v1.reports import router as reports_router

import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    print("🚀 Starting Analytics Service...")
    Base.metadata.create_all(bind=engine)
    
    # Check Redis connection
    redis_healthy = await check_redis_health()
    if redis_healthy:
        print("✅ Redis connection established")
    else:
        print("⚠️  Redis connection failed - some features may be limited")
    
    print("📊 Database tables created/verified")
    
    yield
    
    # Shutdown
    print("🛑 Analytics Service stopped")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tracking_router, prefix=f"{settings.API_V1_STR}/analytics")
app.include_router(reports_router, prefix=f"{settings.API_V1_STR}/analytics")

# Health check endpoint with Redis status
@app.get("/health")
async def health_check():
    redis_healthy = await check_redis_health()
    redis_info = get_redis_info()
    
    return {
        "status": "healthy" if redis_healthy else "degraded",
        "service": "analytics",
        "version": "1.0.0",
        "redis": {
            "status": "connected" if redis_healthy else "disconnected",
            "info": redis_info
        },
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/")
async def root():
    return {
        "message": "Analytics Service",
        "docs": "/docs",
        "health": "/health",
        "api": {
            "tracking": f"{settings.API_V1_STR}/analytics/track",
            "reports": f"{settings.API_V1_STR}/analytics/reports"
        }
    }

# Redis status endpoint
@app.get("/redis/status")
async def redis_status():
    """Get detailed Redis status information"""
    redis_healthy = await check_redis_health()
    redis_info = get_redis_info()
    
    return {
        "healthy": redis_healthy,
        "info": redis_info,
        "connection_url": settings.REDIS_URL,
        "timestamp": datetime.datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )