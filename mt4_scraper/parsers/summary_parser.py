"""Summary and performance data parser for MT4 reports."""

from bs4 import BeautifulSoup

from mt4_scraper.config.settings import SUMMARY_LABELS, PERFORMANCE_LABELS
from mt4_scraper.models.data_models import SummarySection, PerformanceDetails
from mt4_scraper.utils.parsing_utils import parse_numeric
from mt4_scraper.utils.logging_utils import get_logger

logger = get_logger()


class SummaryParser:
    """Parser for summary and performance sections."""

    def __init__(self, soup: BeautifulSoup, input_file: str = "unknown"):
        """Initialize parser with BeautifulSoup object and input file name.

        Args:
            soup: Parsed HTML content from MT4 report
            input_file: Name of the input file being processed
        """
        self.soup = soup
        self.input_file = input_file

    def extract_summary_and_performance(self) -> tuple[SummarySection, PerformanceDetails]:
        """Extract summary and performance data efficiently.

        Returns:
            Tuple of SummarySection and PerformanceDetails objects
        """
        summary_data = {}
        performance_data = {}

        for row in self.soup.find_all('tr', align='right'):
            cells = row.find_all(['td', 'th'])
            current_label = None

            for cell in cells:
                bold = cell.find('b')
                if bold:
                    label_text = bold.get_text().strip()
                    if label_text in SUMMARY_LABELS:
                        current_label = SUMMARY_LABELS[label_text]
                    elif label_text in PERFORMANCE_LABELS:
                        current_label = PERFORMANCE_LABELS[label_text]

                if 'mspt' in cell.get('class', []) and current_label:
                    value_text = cell.get_text().strip()
                    value = parse_numeric(value_text)

                    if current_label in SUMMARY_LABELS.values():
                        summary_data[current_label] = value
                    else:
                        performance_data[current_label] = value

                    current_label = None

        # Create objects from extracted data
        summary_section = SummarySection(**summary_data)
        performance_details = PerformanceDetails(**performance_data)

        return summary_section, performance_details
