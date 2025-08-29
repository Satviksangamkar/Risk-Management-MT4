"""File operation utilities for MT4 Scraper."""

import os
from typing import Optional
from mt4_scraper.config.settings import ENCODING, ENCODING_ERRORS


def validate_file_exists(file_path: str) -> bool:
    """Validate if file exists.

    Args:
        file_path: Path to the file

    Returns:
        True if file exists
    """
    return os.path.exists(file_path)


def read_html_file(file_path: str) -> Optional[str]:
    """Read HTML file content.

    Args:
        file_path: Path to HTML file

    Returns:
        File content as string or None if error
    """
    try:
        with open(file_path, 'r', encoding=ENCODING, errors=ENCODING_ERRORS) as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None



