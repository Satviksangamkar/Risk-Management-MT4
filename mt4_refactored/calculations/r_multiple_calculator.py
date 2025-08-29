"""
R-Multiple Calculator for MT4 Parser
Handles R-Multiple analysis calculations.
"""

from typing import Dict, Any, List, Optional
import statistics
from dataclasses import dataclass

from ..core.interfaces import ICalculator
from ..core.exceptions import MT4CalculationError
from ..config import MT4Config
from ..models import (
    TradeData,
    RMultipleData,
    RMultipleStatistics,
    RMultipleCalculatorResult
)
from ..utils import LoggerMixin


@dataclass
class RMultipleCalculatorResult:
    """Container for R-Multiple calculation results."""
    r_multiple_data: List[RMultipleData]
    statistics: RMultipleStatistics


class RMultipleCalculator(LoggerMixin, ICalculator):
    """
    Calculator for R-Multiple analysis.

    Provides comprehensive R-Multiple calculations including:
    - Core R-Multiple formulas for BUY/SELL trades
    - Statistical analysis and distribution metrics
    - Risk-adjusted performance measures
    """

    def __init__(self, config: Optional[MT4Config] = None):
        """
        Initialize the R-Multiple calculator.

        Args:
            config: Configuration object
        """
        self.config = config or MT4Config()
        self.log_info("R-Multiple Calculator initialized")

    def calculate(self, data: Dict[str, Any]) -> RMultipleCalculatorResult:
        """
        Calculate comprehensive R-Multiple analysis.

        Args:
            data: Dictionary containing closed_trades

        Returns:
            RMultipleCalculatorResult: Complete R-Multiple analysis

        Raises:
            MT4CalculationError: If calculation fails
        """
        try:
            closed_trades = data.get('closed_trades', [])

            if not closed_trades:
                self.log_warning("No closed trades provided for R-Multiple analysis")
                return RMultipleCalculatorResult(
                    r_multiple_data=[],
                    statistics=RMultipleStatistics()
                )

            self.log_info(f"Starting R-Multiple analysis for {len(closed_trades)} trades")

            # Step 1: Convert trades to R-Multiple format
            r_multiple_data = self._convert_trades_to_r_format(closed_trades)

            # Step 2: Calculate R-Multiples
            valid_r_trades = self._calculate_r_multiples(r_multiple_data)

            # Step 3: Perform statistical analysis
            statistics = self._calculate_r_statistics(valid_r_trades)

            result = RMultipleCalculatorResult(
                r_multiple_data=valid_r_trades,
                statistics=statistics
            )

            self.log_info(f"R-Multiple analysis completed. Valid trades: {len(valid_r_trades)}")
            return result

        except Exception as e:
            self.log_error(f"R-Multiple calculation failed: {e}")
            raise MT4CalculationError(f"Failed to calculate R-Multiple analysis: {str(e)}", details=e) from e

    def _convert_trades_to_r_format(self, closed_trades: List[TradeData]) -> List[RMultipleData]:
        """
        Convert TradeData objects to RMultipleData format.

        Args:
            closed_trades: List of TradeData objects

        Returns:
            List[RMultipleData]: Converted R-Multiple data
        """
        r_trades = []

        for trade in closed_trades:
            # Only process closed trades with required data
            if not trade.is_closed_trade():
                continue

            r_trade = RMultipleData(
                ticket=trade.ticket,
                type=trade.type,
                entry_price=trade.price,
                exit_price=trade.close_price,
                stop_loss=trade.s_l,
                take_profit=trade.t_p,
                actual_profit=trade.profit
            )

            r_trades.append(r_trade)

        self.log_debug(f"Converted {len(r_trades)} trades to R-Multiple format")
        return r_trades

    def _calculate_r_multiples(self, r_trades: List[RMultipleData]) -> List[RMultipleData]:
        """
        Calculate R-Multiples for all valid trades.

        Args:
            r_trades: List of RMultipleData objects

        Returns:
            List[RMultipleData]: Valid trades with calculated R-Multiples
        """
        valid_trades = []

        for r_trade in r_trades:
            # Calculate R-Multiple
            r_value = r_trade.calculate_r_multiple()

            if r_trade.is_valid_r_trade:
                valid_trades.append(r_trade)
                self.log_debug(f"Trade {r_trade.ticket}: R = {r_value:.3f}")
            else:
                self.log_debug(f"Trade {r_trade.ticket}: Invalid R-Multiple")

        self.log_info(f"Calculated R-Multiples for {len(valid_trades)} valid trades")
        return valid_trades

    def _calculate_r_statistics(self, valid_r_trades: List[RMultipleData]) -> RMultipleStatistics:
        """
        Calculate comprehensive R-Multiple statistics.

        Args:
            valid_r_trades: List of valid R-Multiple trades

        Returns:
            RMultipleStatistics: Complete statistical analysis
        """
        if not valid_r_trades:
            self.log_warning("No valid R-Multiple trades found")
            return RMultipleStatistics()

        stats = RMultipleStatistics()
        stats.total_valid_r_trades = len(valid_r_trades)

        # Extract R values
        r_values = [trade.r_multiple for trade in valid_r_trades]
        winning_r_values = [r for r in r_values if r > 0]
        losing_r_values = [r for r in r_values if r < 0]

        # Basic statistics
        stats.r_win_rate = (len(winning_r_values) / len(valid_r_trades)) * 100 if valid_r_trades else 0.0
        stats.average_r_multiple = statistics.mean(r_values) if r_values else 0.0
        stats.average_winning_r = statistics.mean(winning_r_values) if winning_r_values else 0.0
        stats.average_losing_r = statistics.mean(losing_r_values) if losing_r_values else 0.0

        # R-Multiple distribution
        distribution = self._calculate_r_distribution(r_values)
        stats.r_distribution = distribution

        # R-Multiple expectancy
        win_rate_decimal = stats.r_win_rate / 100.0
        loss_rate_decimal = 1.0 - win_rate_decimal
        stats.r_expectancy = (win_rate_decimal * stats.average_winning_r) - \
                           (loss_rate_decimal * abs(stats.average_losing_r))

        # Risk-adjusted metrics
        if len(r_values) > 1:
            stats.r_volatility = statistics.stdev(r_values)
            stats.r_skewness, stats.r_kurtosis = self._calculate_r_moments(r_values)

        self.log_info(f"Calculated comprehensive R-Multiple statistics for {stats.total_valid_r_trades} trades")
        return stats

    def _calculate_r_distribution(self, r_values: List[float]) -> Dict[str, int]:
        """Calculate R-Multiple distribution."""
        distribution = {
            'below_-2r': 0, '-2r_to_-1r': 0, '-1r_to_0r': 0,
            '0r_to_+1r': 0, '+1r_to_+2r': 0, 'above_+2r': 0
        }

        for r_value in r_values:
            if r_value < -2.0:
                distribution['below_-2r'] += 1
            elif -2.0 <= r_value < -1.0:
                distribution['-2r_to_-1r'] += 1
            elif -1.0 <= r_value < 0.0:
                distribution['-1r_to_0r'] += 1
            elif 0.0 <= r_value < 1.0:
                distribution['0r_to_+1r'] += 1
            elif 1.0 <= r_value < 2.0:
                distribution['+1r_to_+2r'] += 1
            else:  # r_value >= 2.0
                distribution['above_+2r'] += 1

        return distribution

    def _calculate_r_moments(self, r_values: List[float]) -> tuple:
        """Calculate skewness and kurtosis for R-Multiple distribution."""
        if len(r_values) < 3:
            return 0.0, 0.0

        mean_r = statistics.mean(r_values)
        std_r = statistics.stdev(r_values)

        if std_r == 0:
            return 0.0, 0.0

        # Calculate skewness
        skewness_sum = sum(((r - mean_r) / std_r) ** 3 for r in r_values)
        skewness = skewness_sum / len(r_values)

        # Calculate kurtosis (excess kurtosis)
        kurtosis_sum = sum(((r - mean_r) / std_r) ** 4 for r in r_values)
        kurtosis = (kurtosis_sum / len(r_values)) - 3

        return skewness, kurtosis

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data for R-Multiple calculations."""
        if not isinstance(data, dict):
            return False

        closed_trades = data.get('closed_trades', [])
        if not isinstance(closed_trades, list):
            return False

        return True

