"""
Logging configuration for MT4 FastAPI Backend
Structured logging with different handlers for development and production
"""

import sys
import logging
from typing import Dict, Any
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

from app.core.config import settings


def setup_logging() -> None:
    """Setup structured logging for the application"""

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    json_formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
    )

    # Console handler with Rich formatting for development
    if settings.DEBUG:
        console_handler = RichHandler(
            console=Console(),
            show_time=True,
            show_level=True,
            show_path=True,
            enable_link_path=False
        )
        console_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)
    else:
        # Simple console handler for production (Windows-compatible)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(detailed_formatter)
        console_handler.setLevel(logging.INFO)
        # Ensure UTF-8 encoding for Windows compatibility
        if hasattr(console_handler.stream, 'reconfigure'):
            try:
                console_handler.stream.reconfigure(encoding='utf-8', errors='replace')
            except Exception:
                pass  # Fallback to default encoding
        root_logger.addHandler(console_handler)

    # File handler for all logs
    file_handler = logging.FileHandler(logs_dir / "mt4_backend.log")
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)

    # Error file handler
    error_file_handler = logging.FileHandler(logs_dir / "mt4_backend_error.log")
    error_file_handler.setFormatter(detailed_formatter)
    error_file_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_file_handler)

    # JSON structured logging for production
    if not settings.DEBUG:
        json_file_handler = logging.FileHandler(logs_dir / "mt4_backend.json")
        json_file_handler.setFormatter(json_formatter)
        json_file_handler.setLevel(logging.INFO)
        root_logger.addHandler(json_file_handler)

    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("MT4 FastAPI Backend logging initialized")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    logger.info(f"Debug mode: {settings.DEBUG}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)
