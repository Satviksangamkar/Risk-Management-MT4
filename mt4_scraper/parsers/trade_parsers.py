"""Trade data parsers for MT4 reports."""

from bs4 import BeautifulSoup

from mt4_scraper.config.settings import (
    SECTION_HEADERS,
    CLOSED_TRANSACTIONS_FIELD_MAPPING,
    OPEN_TRADES_FIELD_MAPPING,
    WORKING_ORDERS_FIELD_MAPPING
)
from mt4_scraper.models.data_models import ClosedTransactions, OpenTrades, WorkingOrders
from mt4_scraper.parsers.base_parser import BaseParser
from mt4_scraper.utils.logging_utils import get_logger

logger = get_logger()


class TradeParsers(BaseParser):
    """Parsers for different types of trade data."""

    def __init__(self, soup: BeautifulSoup, input_file: str = "unknown"):
        """Initialize parser with BeautifulSoup object and input file name.

        Args:
            soup: Parsed HTML content from MT4 report
            input_file: Name of the input file being processed
        """
        super().__init__(soup, input_file)

    def extract_closed_transactions(self) -> ClosedTransactions:
        """Extract closed transactions using generic extractor.

        Returns:
            ClosedTransactions object
        """
        data = self.extract_section_generic(
            SECTION_HEADERS['closed_transactions'],
            CLOSED_TRANSACTIONS_FIELD_MAPPING,
            True
        )

        return ClosedTransactions(
            total_closed_pl=data.get('total_pl', 0),
            trades=data.get('trades', [])
        )

    def extract_open_trades(self) -> OpenTrades:
        """Extract open trades using generic extractor.

        Returns:
            OpenTrades object
        """
        data = self.extract_section_generic(
            SECTION_HEADERS['open_trades'],
            OPEN_TRADES_FIELD_MAPPING,
            True
        )

        return OpenTrades(
            floating_pl=data.get('total_pl', 0),
            trades=data.get('trades', [])
        )

    def extract_working_orders(self) -> WorkingOrders:
        """Extract working orders using generic extractor.

        Returns:
            WorkingOrders object
        """
        data = self.extract_section_generic(
            SECTION_HEADERS['working_orders'],
            WORKING_ORDERS_FIELD_MAPPING,
            True
        )

        # Check for "No transactions" status
        orders = data.get('trades', [])
        status = f"{len(orders)} orders found" if orders else 'No transactions'

        return WorkingOrders(
            orders=orders,
            status=status
        )
