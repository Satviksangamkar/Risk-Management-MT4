
"""
Utility functions for parsing MT4 HTML statements.
Contains optimized parsing functions with proper error handling and type hints.
"""

import re
import logging
from typing import Union, Tuple, Optional, Any
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)


def parse_numeric_value(text: Union[str, int, float, None]) -> float:
    """
    Parse numeric value from text, handling various formats including spaces as thousands separators.

    Args:
        text: Input text to parse

    Returns:
        float: Parsed numeric value, 0.0 if parsing fails
    """
    if not text or str(text).strip() == '':
        return 0.0

    try:
        # Convert to string and clean
        text_str = str(text).strip()

        # Remove parentheses and extract the numeric part
        # Handle cases like "1 379.89 (7)" -> extract "1 379.89"
        if '(' in text_str:
            text_str = text_str.split('(')[0].strip()

        # Remove currency symbols and other non-numeric characters except dots, spaces, commas, and minus
        cleaned = re.sub(r'[^\d\s.,-]', '', text_str)

        # Replace spaces with empty string (for thousands separator like "1 237.30")
        cleaned = cleaned.replace(' ', '')

        # Replace comma with dot for decimal separator
        cleaned = cleaned.replace(',', '.')

        # Handle multiple dots (keep only the last one as decimal separator)
        if cleaned.count('.') > 1:
            parts = cleaned.split('.')
            cleaned = ''.join(parts[:-1]) + '.' + parts[-1]

        # Handle empty or just decimal point
        if not cleaned or cleaned == '.' or cleaned == '-':
            return 0.0

        # Use Decimal for precision, then convert to float
        try:
            return float(Decimal(cleaned))
        except InvalidOperation:
            return 0.0

    except (ValueError, AttributeError, TypeError) as e:
        logger.warning(f"Could not parse numeric value '{text}': {e}")
        return 0.0


def extract_percentage_and_count(text: Union[str, None]) -> Tuple[int, float]:
    """
    Extract percentage and count from text like "8 (80.00%)" or "5 (80.00%)".

    Args:
        text: Input text to parse

    Returns:
        Tuple[int, float]: (count, percentage) or (0, 0.0) if parsing fails
    """
    if not text:
        return 0, 0.0

    # Pattern to match "number (percentage%)"
    match = re.search(r'(\d+)\s*\((\d+\.?\d*)%\)', str(text))
    if match:
        count = int(match.group(1))
        percentage = float(match.group(2))
        return count, percentage

    # If no match, try to extract just the number
    return int(parse_numeric_value(text)), 0.0


def extract_consecutive_stats(text: Union[str, None]) -> Tuple[int, float]:
    """
    Extract consecutive statistics from text like "7 (1 379.89)" or "1 379.89 (7)".
    Returns tuple (count, amount) or (amount, count) based on format.

    Args:
        text: Input text to parse

    Returns:
        Tuple[int, float]: (count, amount) or (0, 0.0) if parsing fails
    """
    if not text:
        return 0, 0.0

    text_str = str(text)

    # Pattern to match "count (amount)" like "7 (1 379.89)"
    match1 = re.search(r'(\d+)\s*\(([\d\s.-]+)\)', text_str)
    if match1:
        count = int(match1.group(1))
        amount = parse_numeric_value(match1.group(2))
        return count, amount

    # Pattern to match "amount (count)" like "1 379.89 (7)"
    match2 = re.search(r'([\d\s.-]+)\s*\((\d+)\)', text_str)
    if match2:
        amount = parse_numeric_value(match2.group(1))
        count = int(match2.group(2))
        return count, amount

    return 0, 0.0


def clean_header_name(header: str) -> str:
    """
    Clean header name for dictionary key usage.

    Args:
        header: Original header text

    Returns:
        str: Cleaned header key
    """
    if not header:
        return ""

    # Convert to lowercase and replace special characters
    cleaned = header.lower().replace(' ', '_').replace('/', '_').replace('&nbsp;', 'current_price')

    # Handle special cases
    if 's_' in cleaned and '_l' in cleaned:
        cleaned = 's_l'  # Stop Loss
    elif 't_' in cleaned and '_p' in cleaned:
        cleaned = 't_p'  # Take Profit

    # Remove any remaining special characters
    cleaned = re.sub(r'[^\w_]', '', cleaned)

    return cleaned


def is_numeric_column(header: str, numeric_columns: list) -> bool:
    """
    Check if a column should be parsed as numeric.

    Args:
        header: Column header
        numeric_columns: List of numeric column names

    Returns:
        bool: True if column should be numeric
    """
    return any(col in header for col in numeric_columns)


def validate_trade_data(trade_data: dict) -> bool:
    """
    Validate trade data dictionary.

    Args:
        trade_data: Trade data dictionary to validate

    Returns:
        bool: True if trade data is valid
    """
    required_fields = ['ticket', 'type', 'size', 'item']

    # Check required fields exist and are not empty
    for field in required_fields:
        if field not in trade_data or not trade_data[field]:
            return False

    # Validate ticket number
    if not str(trade_data.get('ticket', '')).isdigit():
        return False

    # Validate trade type
    valid_types = ['buy', 'sell', 'balance']
    if trade_data.get('type', '').lower() not in valid_types:
        return False

    return True


def format_currency(value: Union[int, float], currency_symbol: str = "$") -> str:
    """
    Format numeric value as currency.

    Args:
        value: Numeric value to format
        currency_symbol: Currency symbol to use

    Returns:
        str: Formatted currency string
    """
    try:
        return f"{currency_symbol}{value:,.2f}"
    except (ValueError, TypeError):
        return f"{currency_symbol}0.00"


def format_percentage(value: Union[int, float]) -> str:
    """
    Format numeric value as percentage.

    Args:
        value: Numeric value to format

    Returns:
        str: Formatted percentage string
    """
    try:
        return f"{value:.2f}%"
    except (ValueError, TypeError):
        return "0.00%"


def safe_get_text(element: Any) -> str:
    """
    Safely get text from BeautifulSoup element.

    Args:
        element: BeautifulSoup element

    Returns:
        str: Text content or empty string
    """
    try:
        return element.get_text().strip() if element else ""
    except (AttributeError, TypeError):
        return ""


def safe_find(element: Any, *args, **kwargs) -> Any:
    """
    Safely find element in BeautifulSoup.

    Args:
        element: BeautifulSoup element to search in
        *args: Positional arguments for find()
        **kwargs: Keyword arguments for find()

    Returns:
        BeautifulSoup element or None
    """
    try:
        return element.find(*args, **kwargs) if element else None
    except (AttributeError, TypeError):
        return None
