"""
API Dependencies
FastAPI dependency injection for services
"""

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status

from app.services.mt4_service import MT4Service
from app.core.logging import get_logger

logger = get_logger(__name__)

# Service instances (singletons)
_mt4_service_instance: MT4Service = None


def get_mt4_service() -> MT4Service:
    """Get MT4 service instance (singleton)"""
    global _mt4_service_instance
    if _mt4_service_instance is None:
        _mt4_service_instance = MT4Service()
        logger.info("MT4 service instance created")
    return _mt4_service_instance





def validate_file_upload(file_size: int) -> None:
    """Validate uploaded file size"""
    from app.core.config import settings

    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB"
        )


def validate_content_type(content_type: str) -> None:
    """Validate file content type"""
    allowed_types = [
        "text/html",
        "application/xhtml+xml",
        "text/plain"  # Sometimes HTML files are uploaded as plain text
    ]

    if content_type not in allowed_types:
        # Allow if it contains "html" in the type
        if "html" not in content_type.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {content_type}. Expected HTML file."
            )
