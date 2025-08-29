"""
Parsing Service for MT4 Parser
Orchestrates all HTML parsing operations using the parser factory.
"""

from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

# Robust import system to handle both package and direct execution
import sys
import os
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

# Add parent directory to path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Try imports with fallback
try:
    # Try package imports first
    from mt4_refactored.core.interfaces import IService
    from mt4_refactored.core.exceptions import MT4ParsingError
    from mt4_refactored.config.settings import MT4Config
    from mt4_refactored.models.data_models import (
        MT4StatementData,
        AccountInfo,
        FinancialSummary,
        PerformanceMetrics,
        TradeStatistics
    )
    from mt4_refactored.utils.logging_utils import LoggerMixin, ProgressLogger
except ImportError:
    try:
        # Try direct module imports
        from core.interfaces import IService
        from core.exceptions import MT4ParsingError
        from config.settings import MT4Config
        from models.data_models import (
            MT4StatementData,
            AccountInfo,
            FinancialSummary,
            PerformanceMetrics,
            TradeStatistics
        )
        from utils.logging_utils import LoggerMixin, ProgressLogger
    except ImportError as e:
        print(f"Critical import error in parsing_service: {e}")
        # Provide fallback definitions
        class IService: pass
        class MT4ParsingError(Exception): pass
        class MT4Config:
            @staticmethod
            def get_default_file_path(): return None
        class LoggerMixin: pass
        class ProgressLogger: pass
        # Define minimal data classes
        class MT4StatementData: pass
        class AccountInfo: pass
        class FinancialSummary: pass
        class PerformanceMetrics: pass
        class TradeStatistics: pass


class ParsingService(LoggerMixin, IService):
    """
    Service for orchestrating HTML parsing operations.

    Uses the parser factory to create and manage different parsers,
    coordinating the parsing of all HTML sections.
    """

    def __init__(self, config: Optional[MT4Config] = None):
        """
        Initialize the parsing service.

        Args:
            config: Configuration object
        """
        self.config = config or MT4Config()
        # Local import to avoid circular dependencies
        from strategies.parser_factory import ParserFactory
        self.parser_factory = ParserFactory(self.config)
        self.log_info("Parsing Service initialized")

    def process(self, html_content: str) -> Dict[str, Any]:
        """
        Process HTML content and extract all data sections.

        Args:
            html_content: Raw HTML content as string

        Returns:
            Dict containing all parsed data sections

        Raises:
            MT4ParsingError: If parsing fails
        """
        try:
            self.log_info("Starting HTML parsing process")

            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Create progress logger for parsing steps
            progress = ProgressLogger("HTML parsing", 5)

            # Initialize result container
            parsed_data = {}

            # Step 1: Parse account information
            progress.start()
            progress.log_section("Account Information")
            parsed_data['account_info'] = self._parse_account_info(soup)
            progress.update()

            # Step 2: Parse financial summary
            progress.log_section("Financial Summary")
            parsed_data['financial_summary'] = self._parse_financial_summary(soup)
            progress.update()

            # Step 3: Parse performance metrics
            progress.log_section("Performance Metrics")
            parsed_data['performance_metrics'] = self._parse_performance_metrics(soup)
            progress.update()

            # Step 4: Parse trade data
            progress.log_section("Trade Data")
            trade_data = self._parse_trade_data(soup)
            parsed_data.update(trade_data)
            progress.update()

            # Step 5: Parse additional statistics
            progress.log_section("Additional Statistics")
            parsed_data['trade_statistics'] = self._parse_trade_statistics(soup)
            progress.update()

            progress.complete()
            self.log_info("HTML parsing completed successfully")

            return parsed_data

        except Exception as e:
            self.log_error(f"HTML parsing failed: {e}")
            raise MT4ParsingError(f"Failed to parse HTML content: {str(e)}", details=e) from e

    def _parse_account_info(self, soup: BeautifulSoup) -> AccountInfo:
        """Parse account information section."""
        try:
            parser = self.parser_factory.create_parser('account')
            return parser.parse(soup)
        except Exception as e:
            self.log_error(f"Account info parsing failed: {e}")
            return AccountInfo()

    def _parse_financial_summary(self, soup: BeautifulSoup) -> FinancialSummary:
        """Parse financial summary section."""
        try:
            parser = self.parser_factory.create_parser('financial')
            return parser.parse(soup)
        except Exception as e:
            self.log_error(f"Financial summary parsing failed: {e}")
            return FinancialSummary()

    def _parse_performance_metrics(self, soup: BeautifulSoup) -> PerformanceMetrics:
        """Parse performance metrics section."""
        try:
            parser = self.parser_factory.create_parser('performance')
            return parser.parse(soup)
        except Exception as e:
            self.log_error(f"Performance metrics parsing failed: {e}")
            return PerformanceMetrics()

    def _parse_trade_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Parse trade data sections."""
        try:
            parser = self.parser_factory.create_parser('trade')
            return {
                'closed_trades': parser.parse_closed_trades(soup),
                'open_trades': parser.parse_open_trades(soup)
            }
        except Exception as e:
            self.log_error(f"Trade data parsing failed: {e}")
            return {'closed_trades': [], 'open_trades': []}

    def _parse_trade_statistics(self, soup: BeautifulSoup) -> TradeStatistics:
        """Parse trade statistics section."""
        try:
            parser = self.parser_factory.create_parser('trade')
            return parser.parse_trade_statistics(soup)
        except Exception as e:
            self.log_error(f"Trade statistics parsing failed: {e}")
            return TradeStatistics()

    def get_name(self) -> str:
        """Get service name."""
        return "ParsingService"
