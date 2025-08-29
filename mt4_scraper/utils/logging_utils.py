"""Logging utilities for MT4 Scraper."""

import logging
from mt4_scraper.config.settings import LOG_FORMAT, LOG_LEVEL, LOGGER_NAME


def setup_logging() -> logging.Logger:
    """Setup and configure logging for the application.

    Returns:
        logging.Logger: Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT
    )
    logger = logging.getLogger(LOGGER_NAME)
    return logger


def get_logger(name: str = LOGGER_NAME) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Name of the logger

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)
