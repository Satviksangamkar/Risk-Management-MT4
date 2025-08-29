"""
Parser Factory for MT4 Parser
Implements factory pattern for creating different parser instances.
"""

from typing import Dict, Type, Any, Optional
from bs4 import BeautifulSoup

# Robust import system to handle both package and direct execution
import sys
import os
from typing import Dict, Type, Any, Optional
from bs4 import BeautifulSoup

# Add parent directory to path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Try imports with fallback
try:
    # Try package imports first
    from mt4_refactored.core.interfaces import IParser
    from mt4_refactored.config.settings import MT4Config
    from mt4_refactored.parsers.account_parser import AccountParser
    from mt4_refactored.parsers.financial_parser import FinancialParser
    from mt4_refactored.parsers.performance_parser import PerformanceParser
    from mt4_refactored.parsers.trade_parser import TradeParser
    from mt4_refactored.utils.logging_utils import LoggerMixin
except ImportError:
    try:
        # Try direct module imports
        from core.interfaces import IParser
        from config.settings import MT4Config
        from parsers.account_parser import AccountParser
        from parsers.financial_parser import FinancialParser
        from parsers.performance_parser import PerformanceParser
        from parsers.trade_parser import TradeParser
        from utils.logging_utils import LoggerMixin
    except ImportError as e:
        print(f"Critical import error in parser_factory: {e}")
        # Provide fallback definitions
        class IParser: pass
        class MT4Config:
            @staticmethod
            def get_default_file_path(): return None
        class LoggerMixin: pass
        # Define minimal parser classes
        class AccountParser: pass
        class FinancialParser: pass
        class PerformanceParser: pass
        class TradeParser: pass


class ParserFactory(LoggerMixin):
    """
    Factory for creating parser instances.

    Implements the factory pattern to create and manage different parser types.
    Provides caching and lazy initialization for better performance.
    """

    def __init__(self, config: Optional[MT4Config] = None):
        """
        Initialize the parser factory.

        Args:
            config: Configuration object
        """
        self.config = config or MT4Config()

        # Parser registry mapping parser names to classes
        self._parser_registry: Dict[str, Type[IParser]] = {
            'account': AccountParser,
            'financial': FinancialParser,
            'performance': PerformanceParser,
            'trade': TradeParser
        }

        # Cache for parser instances
        self._parser_cache: Dict[str, IParser] = {}

        self.log_info("Parser Factory initialized")

    def create_parser(self, parser_type: str, soup: Optional[BeautifulSoup] = None) -> IParser:
        """
        Create or retrieve a parser instance.

        Args:
            parser_type: Type of parser to create ('account', 'financial', 'performance', 'trade')
            soup: BeautifulSoup object (required for first creation)

        Returns:
            Parser instance

        Raises:
            ValueError: If parser type is unknown
        """
        if parser_type not in self._parser_registry:
            available_types = list(self._parser_registry.keys())
            raise ValueError(f"Unknown parser type: {parser_type}. Available: {available_types}")

        # Return cached instance if available
        if parser_type in self._parser_cache:
            return self._parser_cache[parser_type]

        # Create new instance if soup is provided
        if soup is not None:
            parser_class = self._parser_registry[parser_type]
            parser_instance = parser_class(soup, self.config)
            self._parser_cache[parser_type] = parser_instance
            self.log_debug(f"Created new {parser_type} parser instance")
            return parser_instance

        # If no soup provided and not cached, raise error
        raise ValueError(f"Parser {parser_type} not cached and no soup provided for creation")

    def create_parser_with_soup(self, parser_type: str, soup: BeautifulSoup) -> IParser:
        """
        Create a parser instance with a specific soup object.
        Always creates a new instance, bypassing cache.

        Args:
            parser_type: Type of parser to create
            soup: BeautifulSoup object

        Returns:
            New parser instance
        """
        if parser_type not in self._parser_registry:
            available_types = list(self._parser_registry.keys())
            raise ValueError(f"Unknown parser type: {parser_type}. Available: {available_types}")

        parser_class = self._parser_registry[parser_type]
        parser_instance = parser_class(soup, self.config)
        self.log_debug(f"Created fresh {parser_type} parser instance")
        return parser_instance

    def clear_cache(self) -> None:
        """Clear the parser cache."""
        self._parser_cache.clear()
        self.log_debug("Parser cache cleared")

    def get_cached_parsers(self) -> Dict[str, IParser]:
        """Get all cached parser instances."""
        return self._parser_cache.copy()

    def register_parser(self, name: str, parser_class: Type[IParser]) -> None:
        """
        Register a new parser type.

        Args:
            name: Name of the parser
            parser_class: Parser class to register
        """
        self._parser_registry[name] = parser_class
        self.log_info(f"Registered new parser: {name}")

    def unregister_parser(self, name: str) -> None:
        """
        Unregister a parser type.

        Args:
            name: Name of the parser to remove
        """
        if name in self._parser_registry:
            del self._parser_registry[name]
            # Also remove from cache if exists
            if name in self._parser_cache:
                del self._parser_cache[name]
            self.log_info(f"Unregistered parser: {name}")

    def list_available_parsers(self) -> list:
        """List all available parser types."""
        return list(self._parser_registry.keys())
