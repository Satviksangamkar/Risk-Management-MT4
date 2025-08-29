"""
Configuration settings for MT4 HTML statement parser.
Centralized configuration management for all parsing parameters.
"""

from typing import Dict, List, Any
from pathlib import Path


class MT4Config:
    """Configuration class for MT4 statement parsing."""

    # File processing settings
    SUPPORTED_EXTENSIONS = ['.htm', '.html']
    DEFAULT_ENCODING = 'utf-8'
    FALLBACK_ENCODING = 'replace'
    MAX_FILE_SIZE_MB = 50  # Maximum file size in MB

    # HTML parsing selectors and patterns
    ACCOUNT_ROW_SELECTOR = 'tr[align="left"]'
    RIGHT_ALIGNED_ROW_SELECTOR = 'tr[align="right"]'
    HEADER_ROW_BG_COLOR = "#C0C0C0"
    MSPT_CLASS = 'mspt'

    # Account information labels
    ACCOUNT_LABELS = {
        'account_number': 'Account:',
        'account_name': 'Name:',
        'currency': 'Currency:',
        'leverage': 'Leverage:',
        'report_date': None  # Will be detected by datetime pattern
    }

    # Financial summary labels
    FINANCIAL_LABELS = [
        'Deposit/Withdrawal:', 'Credit Facility:', 'Closed Trade P/L:',
        'Floating P/L:', 'Margin:', 'Balance:', 'Equity:', 'Free Margin:'
    ]

    # Performance metrics labels
    PERFORMANCE_LABELS = [
        'Gross Profit:', 'Gross Loss:', 'Total Net Profit:', 'Profit Factor:',
        'Expected Payoff:', 'Absolute Drawdown:', 'Maximal Drawdown:', 'Relative Drawdown:'
    ]

    # Trade statistics labels
    TRADE_STATISTICS_LABELS = [
        'Total Trades:', 'Short Positions (won %):', 'Long Positions (won %):',
        'Profit Trades (% of total):', 'Loss trades (% of total):'
    ]

    # Section headers for navigation
    SECTION_HEADERS = {
        'closed_trades': 'Closed Transactions:',
        'open_trades': 'Open Trades:',
        'working_orders': 'Working Orders:'
    }

    # Date and time patterns
    DATETIME_PATTERN = r'\d{4}\s+\w+\s+\d{1,2},\s+\d{1,2}:\d{2}'

    # Numeric parsing patterns
    PERCENTAGE_PATTERN = r'(\d+)\s*\((\d+\.?\d*)%\)'
    CONSECUTIVE_STATS_PATTERN = r'(\d+)\s*\(([\d\s.-]+)\)|\(([\d\s.-]+)\)\s*(\d+)'

    # Logging configuration
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_LEVEL = 'INFO'

    # Output formatting
    CURRENCY_FORMAT = ',.2f'
    PERCENTAGE_FORMAT = '.2f'

    @classmethod
    def get_default_file_path(cls) -> Path:
        """Get the default file path for processing."""
        return Path("10.htm")

    @classmethod
    def validate_file_extension(cls, file_path: Path) -> bool:
        """Validate if the file has a supported extension."""
        return file_path.suffix.lower() in cls.SUPPORTED_EXTENSIONS

    @classmethod
    def get_all_labels(cls) -> Dict[str, List[str]]:
        """Get all label categories for reference."""
        return {
            'financial': cls.FINANCIAL_LABELS,
            'performance': cls.PERFORMANCE_LABELS,
            'trade_statistics': cls.TRADE_STATISTICS_LABELS
        }

    @classmethod
    def get_numeric_columns(cls) -> List[str]:
        """Get column names that should be parsed as numeric values."""
        return [
            'Size', 'Price', 'S / L', 'T / P', 'Commission',
            'Taxes', 'Swap', 'Profit', 'Current Price'
        ]
