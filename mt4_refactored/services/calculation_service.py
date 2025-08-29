"""
Calculation Service for MT4 Parser
Orchestrates all calculation operations using the calculation factory.
"""

from typing import Dict, Any, Optional, List
import sys
import os

# Robust import system for both package and direct execution
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    # Try package imports first
    from mt4_refactored.core.interfaces import IService
    from mt4_refactored.core.exceptions import MT4CalculationError
    from mt4_refactored.config.settings import MT4Config
    from mt4_refactored.models.data_models import (
        CalculatedMetrics,
        RMultipleData,
        RMultipleStatistics,
        TradeData
    )
    from mt4_refactored.calculations.calculation_factory import CalculationFactory
    from mt4_refactored.utils.logging_utils import LoggerMixin, ProgressLogger
except ImportError:
    try:
        # Try direct module imports
        from core.interfaces import IService
        from core.exceptions import MT4CalculationError
        from config.settings import MT4Config
        from models.data_models import (
            CalculatedMetrics,
            RMultipleData,
            RMultipleStatistics,
            TradeData
        )
        from calculations.calculation_factory import CalculationFactory
        from utils.logging_utils import LoggerMixin, ProgressLogger
    except ImportError as e:
        print(f"CalculationService import error: {e}")
        # Define fallback classes
        class IService: pass
        class MT4CalculationError(Exception): pass
        class MT4Config: pass
        class CalculatedMetrics: pass
        class RMultipleData: pass
        class RMultipleStatistics: pass
        class TradeData: pass
        class CalculationFactory: pass
        class LoggerMixin: pass
        class ProgressLogger: pass


class CalculationService(LoggerMixin, IService):
    """
    Service for orchestrating calculation operations.

    Uses the calculation factory to create and manage different calculators,
    coordinating all mathematical computations and analytics.
    """

    def __init__(self, config: Optional[MT4Config] = None):
        """
        Initialize the calculation service.

        Args:
            config: Configuration object
        """
        self.config = config or MT4Config()
        self.calculation_factory = CalculationFactory(self.config)
        self.log_info("Calculation Service initialized")

    def process(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process parsed data and perform all calculations.

        Args:
            parsed_data: Dictionary containing parsed MT4 data

        Returns:
            Dict containing all calculated metrics and analytics

        Raises:
            MT4CalculationError: If calculations fail
        """
        try:
            self.log_info("Starting calculation process")

            # Create progress logger for calculation steps
            progress = ProgressLogger("Calculations", 4)

            # Initialize result container
            calculated_data = {}

            # Extract required data
            closed_trades = parsed_data.get('closed_trades', [])
            financial_summary = parsed_data.get('financial_summary')
            performance_metrics = parsed_data.get('performance_metrics')

            # Step 1: Calculate basic metrics
            progress.start()
            progress.log_section("Basic Metrics")
            calculated_data['calculated_metrics'] = self._calculate_basic_metrics(
                closed_trades, financial_summary, performance_metrics
            )
            progress.update()

            # Step 2: Calculate R-Multiple analysis
            progress.log_section("R-Multiple Analysis")
            r_multiple_result = self._calculate_r_multiple_analysis(closed_trades)
            calculated_data.update(r_multiple_result)
            progress.update()

            # Step 3: Calculate advanced analytics
            progress.log_section("Advanced Analytics")
            calculated_data['advanced_analytics'] = self._calculate_advanced_analytics(
                closed_trades, calculated_data['calculated_metrics']
            )
            progress.update()

            # Step 4: Generate performance ratings
            progress.log_section("Performance Ratings")
            calculated_data['performance_ratings'] = self._calculate_performance_ratings(
                calculated_data['calculated_metrics'],
                calculated_data.get('r_multiple_statistics')
            )
            progress.update()

            progress.complete()
            self.log_info("Calculation process completed successfully")

            return calculated_data

        except Exception as e:
            self.log_error(f"Calculation process failed: {e}")
            raise MT4CalculationError(f"Failed to perform calculations: {str(e)}", details=e) from e

    def _calculate_basic_metrics(
        self,
        closed_trades: List[TradeData],
        financial_summary: Any,
        performance_metrics: Any
    ) -> CalculatedMetrics:
        """Calculate basic trading metrics."""
        try:
            calculator = self.calculation_factory.create_calculator('basic')
            return calculator.calculate({
                'closed_trades': closed_trades,
                'financial_summary': financial_summary,
                'performance_metrics': performance_metrics
            })
        except Exception as e:
            self.log_error(f"Basic metrics calculation failed: {e}")
            return CalculatedMetrics()

    def _calculate_r_multiple_analysis(self, closed_trades: List[TradeData]) -> Dict[str, Any]:
        """Calculate R-Multiple analysis."""
        try:
            calculator = self.calculation_factory.create_calculator('r_multiple')
            result = calculator.calculate({'closed_trades': closed_trades})
            return {
                'r_multiple_data': result.r_multiple_data,
                'r_multiple_statistics': result.statistics
            }
        except Exception as e:
            self.log_error(f"R-Multiple analysis failed: {e}")
            return {
                'r_multiple_data': [],
                'r_multiple_statistics': RMultipleStatistics()
            }

    def _calculate_advanced_analytics(
        self,
        closed_trades: List[TradeData],
        basic_metrics: CalculatedMetrics
    ) -> Dict[str, Any]:
        """Calculate advanced analytics."""
        try:
            calculator = self.calculation_factory.create_calculator('advanced')
            return calculator.calculate({
                'closed_trades': closed_trades,
                'basic_metrics': basic_metrics
            })
        except Exception as e:
            self.log_error(f"Advanced analytics calculation failed: {e}")
            return {}

    def _calculate_performance_ratings(
        self,
        basic_metrics: CalculatedMetrics,
        r_multiple_stats: Optional[RMultipleStatistics]
    ) -> Dict[str, Any]:
        """Calculate performance ratings."""
        try:
            calculator = self.calculation_factory.create_calculator('rating')
            return calculator.calculate({
                'basic_metrics': basic_metrics,
                'r_multiple_statistics': r_multiple_stats
            })
        except Exception as e:
            self.log_error(f"Performance rating calculation failed: {e}")
            return {}

    def get_name(self) -> str:
        """Get service name."""
        return "CalculationService"

