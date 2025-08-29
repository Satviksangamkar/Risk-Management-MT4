"""
Core module for MT4 Parser
Contains main processor, exceptions, and core abstractions.
"""

from .exceptions import (
    MT4ProcessingError,
    MT4ValidationError,
    MT4FileError,
    MT4ParsingError,
    MT4CalculationError
)
from .mt4_processor import MT4Processor
from .interfaces import IParser, ICalculator, IService

__all__ = [
    "MT4ProcessingError",
    "MT4ValidationError",
    "MT4FileError",
    "MT4ParsingError",
    "MT4CalculationError",
    "MT4Processor",
    "IParser",
    "ICalculator",
    "IService"
]

