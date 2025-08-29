"""
Custom exceptions for MT4 Parser
Provides specific exception types for different error scenarios.
"""

from typing import Optional, Any


class MT4ProcessingError(Exception):
    """Base exception for MT4 processing errors."""

    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class MT4ValidationError(MT4ProcessingError):
    """Raised when data validation fails."""
    pass


class MT4FileError(MT4ProcessingError):
    """Raised when file operations fail."""
    pass


class MT4ParsingError(MT4ProcessingError):
    """Raised when HTML parsing fails."""
    pass


class MT4CalculationError(MT4ProcessingError):
    """Raised when calculation operations fail."""
    pass


class MT4ConfigurationError(MT4ProcessingError):
    """Raised when configuration is invalid."""
    pass

