"""Parsing utilities for MT4 Scraper."""

import re
from typing import Union


def parse_numeric(value_str: str) -> Union[float, int]:
    """Parse numeric values efficiently.

    Args:
        value_str: String containing numeric value

    Returns:
        Parsed numeric value or 0.0 if parsing fails
    """
    if not value_str:
        return 0.0

    cleaned = re.sub(r'[^\d.-]', '', value_str.replace(',', ''))

    try:
        # Try to convert to int first, then float
        if '.' not in cleaned and 'e' not in cleaned.lower():
            return int(cleaned)
        else:
            return float(cleaned)
    except ValueError:
        return 0.0


def clean_header_text(header: str) -> str:
    """Clean and normalize header text.

    Args:
        header: Raw header text

    Returns:
        Cleaned header text
    """
    return header.lower().replace(' ', '_').replace('/', '_').replace('&nbsp;', 'current_price')


def is_valid_ticket(ticket_str: str) -> bool:
    """Check if ticket string is valid.

    Args:
        ticket_str: Ticket number as string

    Returns:
        True if valid ticket number
    """
    return ticket_str.isdigit()
