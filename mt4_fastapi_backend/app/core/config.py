"""
Core configuration for MT4 FastAPI Backend
Uses Pydantic settings for configuration management
"""

from typing import List, Optional, Union
from pathlib import Path

from pydantic import AnyHttpUrl, field_validator, ValidationInfo
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Project Information
    PROJECT_NAME: str = "MT4 FastAPI Backend"
    PROJECT_DESCRIPTION: str = "Production-ready FastAPI backend for MT4 statement analysis and comprehensive trading calculations"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Server Configuration
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALLOWED_HOSTS: List[str] = ["*"]

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:5501",  # MT4 Frontend (same port)
        "http://127.0.0.1:5501",
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Vue dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        """Parse CORS origins from environment variable"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Redis Configuration (Optional)
    REDIS_URL: Optional[str] = None
    REDIS_CACHE_TTL: int = 3600  # 1 hour

    # File Upload Configuration
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: Path = Path("./uploads")
    ALLOWED_EXTENSIONS: List[str] = [".htm", ".html"]

    # Calculation Configuration
    MAX_TRADES_PER_REQUEST: int = 10000
    CALCULATION_TIMEOUT: int = 300  # 5 minutes

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # MT4 Processing Configuration
    DEFAULT_HTML_FILE: Path = Path(r"D:\D Drive\ULTIMATE CALCULATOR\10.htm")
    PROCESSING_BATCH_SIZE: int = 100

    # Security Configuration
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    JWT_SECRET_KEY: str = "your-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"

    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
