"""Main parser coordinator for MT4 reports."""

from bs4 import BeautifulSoup

from mt4_scraper.models.data_models import CompleteAnalysis
from mt4_scraper.parsers.header_parser import HeaderParser
from mt4_scraper.parsers.trade_parsers import TradeParsers
from mt4_scraper.parsers.summary_parser import SummaryParser
from mt4_scraper.utils.logging_utils import get_logger

logger = get_logger()


class MainParser:
    """Main parser that coordinates all individual parsers for MT4 reports."""

    def __init__(self, html_content: str, input_file: str = "unknown"):
        """Initialize main parser with HTML content and input file name.

        Args:
            html_content: Raw HTML content from MT4 report
            input_file: Name of the input file being processed
        """
        self.input_file = input_file
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.header_parser = HeaderParser(self.soup, input_file)
        self.trade_parsers = TradeParsers(self.soup, input_file)
        self.summary_parser = SummaryParser(self.soup, input_file)

    def parse_all(self) -> CompleteAnalysis:
        """Parse all sections of the MT4 report for the specified input file.

        Returns:
            CompleteAnalysis object with all extracted data
        """
        logger.info(f"🔍 Starting comprehensive MT4 report parsing for '{self.input_file}'...")

        # Extract all data efficiently
        logger.info(f"📋 Extracting header information from '{self.input_file}'...")
        header_info = self.header_parser.extract_header_info()

        logger.info(f"💼 Extracting closed transactions from '{self.input_file}'...")
        closed_transactions = self.trade_parsers.extract_closed_transactions()

        logger.info(f"📈 Extracting open trades from '{self.input_file}'...")
        open_trades = self.trade_parsers.extract_open_trades()

        logger.info(f"⚙️  Extracting working orders from '{self.input_file}'...")
        working_orders = self.trade_parsers.extract_working_orders()

        logger.info(f"📊 Extracting summary and performance data from '{self.input_file}'...")
        summary_section, performance_details = self.summary_parser.extract_summary_and_performance()

        # Structure complete analysis
        logger.info(f"🔧 Structuring complete analysis for '{self.input_file}'...")
        complete_analysis = CompleteAnalysis(
            header_information=header_info,
            closed_transactions=closed_transactions,
            open_trades=open_trades,
            working_orders=working_orders,
            summary_section=summary_section,
            performance_details=performance_details
        )

        logger.info(f"✅ All sections parsed successfully for '{self.input_file}'")
        return complete_analysis
