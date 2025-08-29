"""Header information parser for MT4 reports."""

import re
from typing import Dict, Optional
from bs4 import BeautifulSoup

from mt4_scraper.models.data_models import HeaderInformation
from mt4_scraper.utils.logging_utils import get_logger

logger = get_logger()


class HeaderParser:
    """Parser for header information in MT4 reports."""

    def __init__(self, soup: BeautifulSoup, input_file: str = "unknown"):
        """Initialize parser with BeautifulSoup object and input file name.

        Args:
            soup: Parsed HTML content from MT4 report
            input_file: Name of the input file being processed
        """
        self.soup = soup
        self.input_file = input_file

    def extract_header_info(self) -> HeaderInformation:
        """Extract header information efficiently.

        Returns:
            HeaderInformation object with extracted data
        """
        header_info = HeaderInformation()
        header_rows = self.soup.find_all('tr', align='left')

        for row in header_rows:
            for bold in row.find_all('b'):
                text = bold.get_text().strip()

                if text.startswith('Account:'):
                    header_info.account_number = text.replace('Account:', '').strip()
                elif text.startswith('Name:'):
                    header_info.account_name = text.replace('Name:', '').strip()
                elif text.startswith('Currency:'):
                    header_info.currency = text.replace('Currency:', '').strip()
                elif text.startswith('Leverage:'):
                    leverage = text.replace('Leverage:', '').strip()
                    header_info.leverage = leverage if leverage else "Not specified"
                elif re.search(r'\d{4}\s+\w+\s+\d{1,2},\s+\d{1,2}:\d{2}', text):
                    header_info.report_date = text

        # Company info
        if self.soup.find_all(string=re.compile(r'Exness Technologies Ltd')):
            header_info.company = 'Exness Technologies Ltd'

        return header_info
