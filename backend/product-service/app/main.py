from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
from app.config import get_settings
from app.api.v1 import api_router
from app.database import Base, sync_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Products Service...")
    
    # Create database tables (in production, use Alembic migrations)
    if settings.environment == "development":
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=sync_engine)
    
    logger.info(f"Products Service started on port {settings.service_port}")
    yield
    
    # Shutdown
    logger.info("Shutting down Products Service...")


app = FastAPI(
    title="Products Service",
    description="CRUD operations for products management",
    version="1.0.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
    openapi_url="/openapi.json" if settings.environment != "production" else None,
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.environment == "development" else ["example.com"],
)

# Include routers
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "message": "Products Service API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=settings.environment == "development",
    )