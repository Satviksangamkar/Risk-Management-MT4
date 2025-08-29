"""
Base parser class for MT4 HTML statement parsing.
Provides common functionality and interface for all parsers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from bs4 import BeautifulSoup

# Direct absolute imports to avoid relative import issues
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.logging_utils import LoggerMixin
from config.settings import MT4Config
from core.interfaces import IParser


class BaseParser(LoggerMixin, IParser, ABC):
    """Abstract base class for all MT4 parsers."""

    def __init__(self, soup: BeautifulSoup, config: Optional[MT4Config] = None):
        """
        Initialize the parser.

        Args:
            soup: BeautifulSoup object of the HTML content
            config: Configuration object (uses default if None)
        """
        self.soup = soup
        self.config = config or MT4Config()
        self._cache: Dict[str, Any] = {}

    @abstractmethod
    def parse(self) -> Any:
        """
        Parse the specific section and return structured data.

        Returns:
            Parsed data object
        """
        pass

    def find_rows_by_alignment(self, alignment: str) -> List[Any]:
        """
        Find all rows with specific alignment.

        Args:
            alignment: CSS alignment value ('left', 'right', 'center')

        Returns:
            List of matching row elements
        """
        cache_key = f"rows_{alignment}"
        if cache_key not in self._cache:
            self._cache[cache_key] = self.soup.find_all('tr', align=alignment)
        return self._cache[cache_key]

    def parse_labeled_data(self, labels: List[str], label_mapping: Dict[str, str],
                          data_object: Any, value_parser: callable = None) -> None:
        """
        Generic method to parse labeled data from HTML table rows.

        Args:
            labels: List of labels to look for
            label_mapping: Dictionary mapping labels to object attributes
            data_object: Object to populate with parsed data
            value_parser: Optional custom value parser function
        """
        rows = self.find_rows_by_alignment('right')

        for row in rows:
            cells = row.find_all(['td', 'th'])
            current_label = None

            for cell in cells:
                # Check if cell contains a bold element with a label
                bold = cell.find('b')
                if bold:
                    label_text = self.get_text_safely(bold)
                    if label_text in labels:
                        current_label = label_text

                # Check if cell is a value cell
                if (self.config.MSPT_CLASS in cell.get('class', []) or
                    'mspt' in str(cell.get('class', []))) and current_label:

                    value_text = self.get_text_safely(cell)

                    # Use custom parser or default numeric parser
                    if value_parser:
                        value = value_parser(value_text, current_label, data_object)
                    else:
                        value = self.parse_numeric_value(value_text)

                    # Set value on object
                    if current_label in label_mapping:
                        attr_name = label_mapping[current_label]
                        setattr(data_object, attr_name, value)
                        self.log_debug(f"Parsed {attr_name}: {value}")

                    current_label = None

    def parse_numeric_value(self, text: str) -> float:
        """
        Parse numeric value from text.

        Args:
            text: Text to parse

        Returns:
            float: Parsed numeric value
        """
        from ..utils import parse_numeric_value as parse_num
        return parse_num(text)

    def find_rows_by_selector(self, selector: str) -> List[Any]:
        """
        Find rows using CSS selector.

        Args:
            selector: CSS selector string

        Returns:
            List of matching elements
        """
        cache_key = f"selector_{selector}"
        if cache_key not in self._cache:
            self._cache[cache_key] = self.soup.select(selector)
        return self._cache[cache_key]

    def find_elements_by_class(self, class_name: str, tag: str = "*") -> List[Any]:
        """
        Find elements by CSS class.

        Args:
            class_name: CSS class name
            tag: HTML tag name (default: any tag)

        Returns:
            List of matching elements
        """
        cache_key = f"class_{tag}_{class_name}"
        if cache_key not in self._cache:
            if tag == "*":
                self._cache[cache_key] = self.soup.find_all(class_=class_name)
            else:
                self._cache[cache_key] = self.soup.find_all(tag, class_=class_name)
        return self._cache[cache_key]

    def clear_cache(self) -> None:
        """Clear the internal cache."""
        self._cache.clear()

    def get_text_safely(self, element: Any) -> str:
        """
        Safely extract text from an element.

        Args:
            element: BeautifulSoup element

        Returns:
            str: Text content or empty string
        """
        try:
            return element.get_text().strip() if element else ""
        except (AttributeError, TypeError):
            return ""

    def find_bold_text(self, element: Any) -> str:
        """
        Find and extract bold text from an element.

        Args:
            element: BeautifulSoup element

        Returns:
            str: Bold text content or empty string
        """
        bold = element.find('b') if element else None
        return self.get_text_safely(bold)

    def print_section_summary(self, section_number: int, section_title: str,
                             data_object: Any, field_formatters: Dict[str, str] = None) -> None:
        """
        Generic method to print section summaries.

        Args:
            section_number: Section number for display
            section_title: Section title
            data_object: Data object to display
            field_formatters: Optional custom formatters for fields
        """
        print(f"\n{section_number}. {section_title.upper()}:")
        print("-" * 50)

        if not field_formatters:
            field_formatters = {}

        # Get all non-private, non-method attributes
        for attr_name in dir(data_object):
            if not attr_name.startswith('_') and not callable(getattr(data_object, attr_name)):
                value = getattr(data_object, attr_name)

                # Skip None values and empty strings
                if value is None or value == "" or value == 0:
                    continue

                # Format field name
                display_name = attr_name.replace('_', ' ').title()

                # Apply custom formatter or default
                if attr_name in field_formatters:
                    formatter = field_formatters[attr_name]
                    if formatter == 'currency':
                        print(f"  {display_name}: {value:,.2f}")
                    elif formatter == 'percentage':
                        print(f"  {display_name}: {value:.2f}%")
                    elif formatter == 'ratio':
                        print(f"  {display_name}: {value:.2f}:1")
                    else:
                        print(f"  {display_name}: {value}")
                else:
                    # Default formatting based on value type
                    if isinstance(value, float):
                        if 'percentage' in attr_name.lower() or 'rate' in attr_name.lower():
                            print(f"  {display_name}: {value:.2f}%")
                        else:
                            print(f"  {display_name}: {value:,.2f}")
                    else:
                        print(f"  {display_name}: {value}")
