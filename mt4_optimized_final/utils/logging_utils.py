"""
Logging utilities for MT4 HTML statement parser.
Provides centralized logging configuration and utilities.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up logging configuration for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log message format
        log_file: Optional log file path

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('mt4_parser')
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, IOError) as e:
            logger.warning(f"Could not create log file {log_file}: {e}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(f'mt4_parser.{name}')


class LoggerMixin:
    """Mixin class to provide logging functionality to other classes."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger instance for this class."""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger

    def log_info(self, message: str, *args, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, *args, **kwargs)

    def log_warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)

    def log_error(self, message: str, *args, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, *args, **kwargs)

    def log_debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)


class ProgressLogger:
    """Utility class for logging progress of long-running operations."""

    def __init__(self, operation_name: str, total_items: Optional[int] = None):
        self.operation_name = operation_name
        self.total_items = total_items
        self.processed_items = 0
        self.logger = get_logger('progress')

    def start(self) -> None:
        """Log the start of an operation."""
        if self.total_items:
            self.logger.info(f"Starting {self.operation_name} (0/{self.total_items})")
        else:
            self.logger.info(f"Starting {self.operation_name}")

    def update(self, increment: int = 1) -> None:
        """Update progress counter."""
        self.processed_items += increment
        if self.total_items and self.processed_items % max(1, self.total_items // 10) == 0:
            self.logger.info(f"Progress: {self.operation_name} ({self.processed_items}/{self.total_items})")

    def complete(self) -> None:
        """Log the completion of an operation."""
        if self.total_items:
            self.logger.info(f"Completed {self.operation_name} ({self.processed_items}/{self.total_items})")
        else:
            self.logger.info(f"Completed {self.operation_name}")

    def log_section(self, section_name: str) -> None:
        """Log the start of a processing section."""
        self.logger.info(f"Processing section: {section_name}")
