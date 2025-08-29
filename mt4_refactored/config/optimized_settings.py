"""
ULTRA-OPTIMIZED CONFIGURATION SETTINGS
Consolidated, production-ready configuration for MT4 HTML statement processing
"""

from typing import Dict, List, Any, Set
from pathlib import Path
import re

class UltraFastMT4Config:
    """Ultra-optimized configuration class with all settings consolidated."""

    # File processing settings
    SUPPORTED_EXTENSIONS: Set[str] = {'.htm', '.html'}
    DEFAULT_ENCODING: str = 'utf-8'
    FALLBACK_ENCODING: str = 'replace'
    MAX_FILE_SIZE_MB: int = 100

    # Pre-compiled regex patterns for ultra-fast parsing
    NUMERIC_PATTERN = re.compile(r'-?\d*\.?\d+')
    WHITESPACE_PATTERN = re.compile(r'\s+')
    TRADE_INDICATOR_PATTERN = re.compile(r'\b(buy|sell)\b', re.IGNORECASE)

    # HTML parsing selectors (optimized)
    TRADE_ROW_SELECTOR: str = 'tr:has(td:-soup-contains("buy")), tr:has(td:-soup-contains("sell"))'
    HEADER_ROW_BG_COLOR: str = "#C0C0C0"
    MSPT_CLASS: str = 'mspt'

    # Default file path
    DEFAULT_HTML_FILE: Path = Path(r"D:\D Drive\ULTIMATE CALCULATOR\10.htm")

    # Trade data column mapping
    TRADE_COLUMNS: Dict[str, int] = {
        'ticket': 0,
        'open_time': 1,
        'type': 2,
        'size': 3,
        'item': 4,
        'price': 5,
        's_l': 6,
        't_p': 7,
        'close_time': 8,
        'close_price': 9,
        'commission': 10,
        'taxes': 11,
        'swap': 12,
        'profit': 13
    }

    # Numeric columns for optimized parsing
    NUMERIC_COLUMNS: Set[str] = {
        'size', 'price', 's_l', 't_p', 'close_price',
        'commission', 'taxes', 'swap', 'profit'
    }

    # Account information labels
    ACCOUNT_LABELS: Dict[str, str] = {
        'account_number': 'Account:',
        'account_name': 'Name:',
        'currency': 'Currency:',
        'leverage': 'Leverage:'
    }

    # Financial summary labels
    FINANCIAL_LABELS: List[str] = [
        'Deposit/Withdrawal:', 'Credit Facility:', 'Closed Trade P/L:',
        'Floating P/L:', 'Margin:', 'Balance:', 'Equity:', 'Free Margin:'
    ]

    # Performance metrics labels
    PERFORMANCE_LABELS: List[str] = [
        'Gross Profit:', 'Gross Loss:', 'Total Net Profit:', 'Profit Factor:',
        'Expected Payoff:', 'Absolute Drawdown:', 'Maximal Drawdown:', 'Relative Drawdown:'
    ]

    # Trade statistics labels
    TRADE_STATISTICS_LABELS: List[str] = [
        'Total Trades:', 'Short Positions (won %):', 'Long Positions (won %):',
        'Profit Trades (% of total):', 'Loss trades (% of total):'
    ]

    # Section headers for navigation
    SECTION_HEADERS: Dict[str, str] = {
        'closed_trades': 'Closed Transactions:',
        'open_trades': 'Open Trades:',
        'working_orders': 'Working Orders:'
    }

    # Date and time patterns
    DATETIME_PATTERN: str = r'\d{4}\s+\w+\s+\d{1,2},\s+\d{1,2}:\d{2}'

    # Parsing patterns
    PERCENTAGE_PATTERN: str = r'(\d+)\s*\((\d+\.?\d*)%\)'
    CONSECUTIVE_STATS_PATTERN: str = r'(\d+)\s*\(([\d\s.-]+)\)|\(([\d\s.-]+)\)\s*(\d+)'

    # Logging configuration
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_LEVEL: str = 'INFO'

    # Output formatting
    CURRENCY_FORMAT: str = ',.2f'
    PERCENTAGE_FORMAT: str = '.2f'
    RATIO_FORMAT: str = '.3f'

    # Performance thresholds for ratings
    RATING_THRESHOLDS: Dict[str, Dict[str, float]] = {
        'profit_factor': {'excellent': 1.5, 'good': 1.0, 'fair': 0.8},
        'win_rate': {'excellent': 60.0, 'good': 50.0, 'fair': 40.0},
        'r_expectancy': {'excellent': 0.5, 'good': 0.2, 'fair': 0.1},
        'sharpe_ratio': {'excellent': 1.0, 'good': 0.5, 'fair': 0.0},
        'kelly_percentage': {'excellent': 10.0, 'good': 5.0, 'fair': 2.0},
        'recovery_factor': {'excellent': 2.0, 'good': 1.0, 'fair': 0.5}
    }

    # Risk-free rate for calculations
    RISK_FREE_RATE_ANNUAL: float = 0.02  # 2%
    RISK_FREE_RATE_DAILY: float = RISK_FREE_RATE_ANNUAL / 365

    @classmethod
    def get_default_file_path(cls) -> Path:
        """Get the default file path for processing."""
        return cls.DEFAULT_HTML_FILE

    @classmethod
    def validate_file_extension(cls, file_path: Path) -> bool:
        """Validate if the file has a supported extension."""
        return file_path.suffix.lower() in cls.SUPPORTED_EXTENSIONS

    @classmethod
    def is_numeric_column(cls, column_name: str) -> bool:
        """Check if a column should be parsed as numeric."""
        return column_name.lower() in cls.NUMERIC_COLUMNS

    @classmethod
    def get_rating_score(cls, metric_name: str, value: float) -> float:
        """Get rating score for a metric value."""
        if metric_name not in cls.RATING_THRESHOLDS:
            return 0.0

        thresholds = cls.RATING_THRESHOLDS[metric_name]
        if value >= thresholds['excellent']:
            return 100.0
        elif value >= thresholds['good']:
            return 75.0
        elif value >= thresholds['fair']:
            return 50.0
        elif value > 0:
            return 25.0
        else:
            return 0.0

    @classmethod
    def get_all_labels(cls) -> Dict[str, Any]:
        """Get all label categories for reference."""
        return {
            'account': cls.ACCOUNT_LABELS,
            'financial': cls.FINANCIAL_LABELS,
            'performance': cls.PERFORMANCE_LABELS,
            'trade_statistics': cls.TRADE_STATISTICS_LABELS,
            'sections': cls.SECTION_HEADERS
        }

# Global configuration instance
config = UltraFastMT4Config()
