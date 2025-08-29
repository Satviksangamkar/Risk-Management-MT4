"""Base HTML parser for MT4 reports."""

import re
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup

from mt4_scraper.config.settings import (
    SECTION_END_MARKERS, NUMERIC_COLUMNS
)
from mt4_scraper.utils.parsing_utils import parse_numeric, clean_header_text, is_valid_ticket
from mt4_scraper.utils.logging_utils import get_logger

logger = get_logger()


class BaseParser:
    """Base parser for MT4 HTML reports."""

    def __init__(self, soup: BeautifulSoup, input_file: str = "unknown"):
        """Initialize parser with BeautifulSoup object and input file name.

        Args:
            soup: Parsed HTML content from MT4 report
            input_file: Name of the input file being processed
        """
        self.soup = soup
        self.input_file = input_file

    def find_section_header(self, section_name: str) -> Optional['bs4.element.Tag']:
        """Find section header in the HTML.

        Args:
            section_name: Name of the section to find

        Returns:
            Section row element or None
        """
        for row in self.soup.find_all('tr'):
            if row.find('td') and row.find('td').find('b') and section_name in row.get_text():
                return row
        return None

    def extract_section_generic(
        self,
        section_name: str,
        field_mappings: Dict[str, str],
        is_trade_section: bool = False
    ) -> Dict:
        """Generic section extractor for MT4 reports.

        Args:
            section_name: Name of the section
            field_mappings: Field mapping dictionary
            is_trade_section: Whether this is a trade section

        Returns:
            Extracted data dictionary
        """
        logger.info(f"🔍 Extracting '{section_name}' from '{self.input_file}'...")

        # Find section header
        section_row = self.find_section_header(section_name)

        if not section_row:
            logger.info(f"⚠️  No '{section_name}' section found in '{self.input_file}'")
            return {} if not is_trade_section else {'trades': [], 'total_pl': 0}

        # Find header row
        header_row = section_row.find_next_sibling('tr')
        if not header_row or header_row.get('bgcolor') != "#C0C0C0":
            return {} if not is_trade_section else {'trades': [], 'total_pl': 0}

        headers = [td.get_text().strip() for td in header_row.find_all('td')]

        data = {'trades': []} if is_trade_section else {}
        current_row = header_row.find_next_sibling('tr')

        while current_row:
            cells = current_row.find_all('td')

            # Check for end conditions
            if cells:
                first_text = cells[0].get_text().strip()
                if any(end_marker in first_text for end_marker in SECTION_END_MARKERS):
                    if 'P/L:' in first_text:
                        pl_text = current_row.get_text()
                        pl_match = re.search(r'([A-Za-z\s]+P/L):\s*([-\d.,]+)', pl_text)
                        if pl_match:
                            data['total_pl'] = parse_numeric(pl_match.group(2))
                    break

            # Process trade rows
            if is_trade_section and len(cells) >= 10 and cells[0].get_text().strip().isdigit():
                trade_data = {}
                for i, header in enumerate(headers):
                    if i < len(cells):
                        value = cells[i].get_text().strip()
                        header_key = clean_header_text(header)

                        # Apply field mappings
                        if header_key in field_mappings:
                            header_key = field_mappings[header_key]

                        trade_data[header_key] = parse_numeric(value) if header in NUMERIC_COLUMNS else value

                if is_valid_ticket(trade_data.get('ticket', '')):
                    data['trades'].append(trade_data)

            current_row = current_row.find_next_sibling('tr')

        return data
