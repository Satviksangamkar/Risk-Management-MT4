"""
Utilities module for MT4 HTML statement parser.
"""

from .parsing_utils import (
    parse_numeric_value,
    extract_percentage_and_count,
    extract_consecutive_stats,
    clean_header_name,
    is_numeric_column,
    validate_trade_data,
    format_currency,
    format_percentage,
    safe_get_text,
    safe_find
)

from .logging_utils import (
    setup_logging,
    get_logger,
    LoggerMixin,
    ProgressLogger
)

from .r_multiple_validation import RMultipleValidator

__all__ = [
    # Parsing utilities
    'parse_numeric_value',
    'extract_percentage_and_count',
    'extract_consecutive_stats',
    'clean_header_name',
    'is_numeric_column',
    'validate_trade_data',
    'format_currency',
    'format_percentage',
    'safe_get_text',
    'safe_find',
    # Logging utilities
    'setup_logging',
    'get_logger',
    'LoggerMixin',
    'ProgressLogger',
    # R-Multiple validation
    'RMultipleValidator'
]
