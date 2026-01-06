from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
import os

class Settings(BaseSettings):
    # Database configuration
    postgres_host: str = "localhost"
    postgres_port: int = 5433
    postgres_db: str = "products_db"
    postgres_user: str = "products_user"
    postgres_password: str = "products_user"
    
    # Service configuration
    service_port: int = 8001
    environment: str = "development"
    log_level: str = "INFO"
    
    # CORS configuration
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:4200",
        "http://localhost:80",
    ]
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def async_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    class Config:
        # Use global .env file from parent directory
        env_file = str(Path(__file__).parent.parent.parent.parent / ".env")
        case_sensitive = False
        extra = "allow"  # Add this line to allow extra fields

@lru_cache()
def get_settings() -> Settings:
    return Settings()