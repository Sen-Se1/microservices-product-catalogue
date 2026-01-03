# app/core/config.py
import os
from typing import List

class Settings:
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Analytics Service"
    
    # Load from environment variables with defaults
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://analytics_user:analytics_pass@localhost:5432/analytics_db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "test-secret-key-for-development-only")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    API_PORT: int = int(os.getenv("API_PORT", "8003"))
    
    # CORS - parse from string
    def get_cors_origins(self) -> List[str]:
        cors = os.getenv("CORS_ORIGINS", "")
        if cors.startswith("["):
            import json
            return json.loads(cors)
        elif cors:
            return [origin.strip() for origin in cors.split(",")]
        else:
            return ["http://localhost:3000", "http://localhost:4200"]
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        return self.get_cors_origins()

settings = Settings()