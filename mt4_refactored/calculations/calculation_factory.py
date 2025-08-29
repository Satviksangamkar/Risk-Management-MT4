"""
Calculation Factory for MT4 Parser
Implements factory pattern for creating different calculator instances.
"""

from typing import Dict, Type, Any, Optional
import sys
import os

# Robust import system for both package and direct execution
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    # Try package imports first
    from mt4_refactored.core.interfaces import ICalculator
    from mt4_refactored.config.settings import MT4Config
    from mt4_refactored.utils.logging_utils import LoggerMixin
except ImportError:
    try:
        # Try direct module imports
        from core.interfaces import ICalculator
        from config.settings import MT4Config
        from utils.logging_utils import LoggerMixin
    except ImportError as e:
        print(f"CalculationFactory import error: {e}")
        # Define fallback classes
        class ICalculator: pass
        class MT4Config: pass
        class LoggerMixin: pass


class CalculationFactory(LoggerMixin):
    """
    Factory for creating calculator instances.

    Implements the factory pattern to create and manage different calculator types.
    Provides caching and lazy initialization for better performance.
    """

    def __init__(self, config: Optional[MT4Config] = None):
        """
        Initialize the calculation factory.

        Args:
            config: Configuration object
        """
        self.config = config or MT4Config()

        # Calculator registry mapping calculator names to classes
        self._calculator_registry: Dict[str, Type[ICalculator]] = {}

        # Cache for calculator instances
        self._calculator_cache: Dict[str, ICalculator] = {}

        # Register built-in calculators
        self._register_builtin_calculators()

        self.log_info("Calculation Factory initialized")

    def _register_builtin_calculators(self) -> None:
        """Register all built-in calculator types."""
        # Import here to avoid circular imports
        from .basic_calculator import BasicCalculator
        from .r_multiple_calculator import RMultipleCalculator
        from .advanced_calculator import AdvancedCalculator
        from .rating_calculator import RatingCalculator

        self._calculator_registry.update({
            'basic': BasicCalculator,
            'r_multiple': RMultipleCalculator,
            'advanced': AdvancedCalculator,
            'rating': RatingCalculator
        })

    def create_calculator(self, calculator_type: str) -> ICalculator:
        """
        Create or retrieve a calculator instance.

        Args:
            calculator_type: Type of calculator to create

        Returns:
            Calculator instance

        Raises:
            ValueError: If calculator type is unknown
        """
        if calculator_type not in self._calculator_registry:
            available_types = list(self._calculator_registry.keys())
            raise ValueError(f"Unknown calculator type: {calculator_type}. Available: {available_types}")

        # Return cached instance if available
        if calculator_type in self._calculator_cache:
            return self._calculator_cache[calculator_type]

        # Create new instance
        calculator_class = self._calculator_registry[calculator_type]
        calculator_instance = calculator_class(self.config)
        self._calculator_cache[calculator_type] = calculator_instance
        self.log_debug(f"Created new {calculator_type} calculator instance")

        return calculator_instance

    def create_calculator_fresh(self, calculator_type: str) -> ICalculator:
        """
        Create a fresh calculator instance, bypassing cache.

        Args:
            calculator_type: Type of calculator to create

        Returns:
            New calculator instance
        """
        if calculator_type not in self._calculator_registry:
            available_types = list(self._calculator_registry.keys())
            raise ValueError(f"Unknown calculator type: {calculator_type}. Available: {available_types}")

        calculator_class = self._calculator_registry[calculator_type]
        calculator_instance = calculator_class(self.config)
        self.log_debug(f"Created fresh {calculator_type} calculator instance")
        return calculator_instance

    def clear_cache(self) -> None:
        """Clear the calculator cache."""
        self._calculator_cache.clear()
        self.log_debug("Calculator cache cleared")

    def get_cached_calculators(self) -> Dict[str, ICalculator]:
        """Get all cached calculator instances."""
        return self._calculator_cache.copy()

    def register_calculator(self, name: str, calculator_class: Type[ICalculator]) -> None:
        """
        Register a new calculator type.

        Args:
            name: Name of the calculator
            calculator_class: Calculator class to register
        """
        self._calculator_registry[name] = calculator_class
        self.log_info(f"Registered new calculator: {name}")

    def unregister_calculator(self, name: str) -> None:
        """
        Unregister a calculator type.

        Args:
            name: Name of the calculator to remove
        """
        if name in self._calculator_registry:
            del self._calculator_registry[name]
            # Also remove from cache if exists
            if name in self._calculator_cache:
                del self._calculator_cache[name]
            self.log_info(f"Unregistered calculator: {name}")

    def list_available_calculators(self) -> list:
        """List all available calculator types."""
        return list(self._calculator_registry.keys())

