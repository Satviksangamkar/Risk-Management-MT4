"""
Advanced Calculator for MT4 Parser
Handles advanced analytics calculations.
"""

from typing import Dict, Any, List, Optional

from ..core.interfaces import ICalculator
from ..core.exceptions import MT4CalculationError
from ..config import MT4Config
from ..models import TradeData, CalculatedMetrics
from ..utils import LoggerMixin


class AdvancedCalculator(LoggerMixin, ICalculator):
    """
    Calculator for advanced trading analytics.

    Provides sophisticated analysis including:
    - Volatility analysis
    - Sharpe and Sortino ratios
    - Calmar ratio
    - Ulcer index
    - Sterling ratio
    """

    def __init__(self, config: Optional[MT4Config] = None):
        """
        Initialize the advanced calculator.

        Args:
            config: Configuration object
        """
        self.config = config or MT4Config()
        self.log_info("Advanced Calculator initialized")

    def calculate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate advanced analytics.

        Args:
            data: Dictionary containing closed_trades and basic_metrics

        Returns:
            Dict: Advanced analytics results

        Raises:
            MT4CalculationError: If calculation fails
        """
        try:
            closed_trades = data.get('closed_trades', [])
            basic_metrics = data.get('basic_metrics')

            if not closed_trades:
                self.log_warning("No closed trades provided for advanced analytics")
                return {}

            self.log_info(f"Calculating advanced analytics for {len(closed_trades)} trades")

            results = {}

            # Extract profits for analysis
            profits = [trade.profit for trade in closed_trades]

            # Risk-adjusted performance metrics
            results['sharpe_ratio'] = self._calculate_sharpe_ratio(profits)
            results['sortino_ratio'] = self._calculate_sortino_ratio(profits)
            results['calmar_ratio'] = self._calculate_calmar_ratio(basic_metrics)

            # Drawdown analysis
            results['ulcer_index'] = self._calculate_ulcer_index(closed_trades)
            results['sterling_ratio'] = self._calculate_sterling_ratio(basic_metrics)

            # Volatility measures
            results['volatility_coefficient'] = self._calculate_volatility_coefficient(profits)
            results['downside_deviation'] = self._calculate_downside_deviation(profits)

            # Performance consistency
            results['profit_consistency_ratio'] = self._calculate_profit_consistency_ratio(closed_trades)

            self.log_info("Advanced analytics calculation completed")
            return results

        except Exception as e:
            self.log_error(f"Advanced analytics calculation failed: {e}")
            raise MT4CalculationError(f"Failed to calculate advanced analytics: {str(e)}", details=e) from e

    def _calculate_sharpe_ratio(self, profits: List[float]) -> float:
        """Calculate Sharpe Ratio."""
        if len(profits) < 2:
            return 0.0

        # Use risk-free rate of 0.02 (2%) annualized, convert to daily
        risk_free_daily = 0.02 / 365

        # Calculate mean return and standard deviation
        mean_return = sum(profits) / len(profits)
        variance = sum((p - mean_return) ** 2 for p in profits) / len(profits)
        std_dev = variance ** 0.5

        # Sharpe ratio = (Mean return - Risk-free rate) / Standard deviation
        return (mean_return - risk_free_daily) / std_dev if std_dev > 0 else 0.0

    def _calculate_sortino_ratio(self, profits: List[float]) -> float:
        """Calculate Sortino Ratio (downside deviation only)."""
        if len(profits) < 2:
            return 0.0

        # Calculate downside deviation
        risk_free_daily = 0.02 / 365
        negative_returns = [p for p in profits if p < risk_free_daily]

        if not negative_returns:
            return float('inf')  # No downside risk

        mean_return = sum(profits) / len(profits)

        # Downside deviation
        downside_variance = sum((min(0, p - risk_free_daily)) ** 2 for p in profits) / len(profits)
        downside_deviation = downside_variance ** 0.5

        return (mean_return - risk_free_daily) / downside_deviation if downside_deviation > 0 else float('inf')

    def _calculate_calmar_ratio(self, basic_metrics: Optional[CalculatedMetrics]) -> float:
        """Calculate Calmar Ratio (Annual return / Max drawdown)."""
        if not basic_metrics:
            return 0.0

        roi_percentage = basic_metrics.roi_percentage
        max_drawdown_percentage = basic_metrics.maximum_drawdown_percentage

        if max_drawdown_percentage <= 0:
            return 0.0

        return roi_percentage / max_drawdown_percentage

    def _calculate_ulcer_index(self, closed_trades: List[TradeData]) -> float:
        """Calculate Ulcer Index for drawdown measurement."""
        if len(closed_trades) < 2:
            return 0.0

        # Simulate equity curve
        equity_curve = []
        current_equity = 10000  # Starting equity

        for trade in closed_trades:
            current_equity += trade.profit
            equity_curve.append(current_equity)

        # Calculate drawdowns
        max_equity = equity_curve[0]
        drawdowns = []

        for equity in equity_curve:
            max_equity = max(max_equity, equity)
            drawdown = (max_equity - equity) / max_equity
            drawdowns.append(drawdown)

        # Ulcer Index = sqrt(mean of squared drawdowns)
        mean_squared_drawdown = sum(d ** 2 for d in drawdowns) / len(drawdowns)
        return mean_squared_drawdown ** 0.5

    def _calculate_sterling_ratio(self, basic_metrics: Optional[CalculatedMetrics]) -> float:
        """Calculate Sterling Ratio (Average annual return / Average drawdown)."""
        if not basic_metrics:
            return 0.0

        roi_percentage = basic_metrics.roi_percentage
        max_drawdown_percentage = basic_metrics.maximum_drawdown_percentage

        if max_drawdown_percentage <= 0:
            return 0.0

        return roi_percentage / max_drawdown_percentage

    def _calculate_volatility_coefficient(self, profits: List[float]) -> float:
        """Calculate coefficient of variation as percentage."""
        if not profits:
            return 0.0

        mean = sum(profits) / len(profits)
        if mean == 0:
            return 0.0

        variance = sum((p - mean) ** 2 for p in profits) / len(profits)
        std_dev = variance ** 0.5

        return (std_dev / abs(mean)) * 100  # Coefficient of variation as percentage

    def _calculate_downside_deviation(self, profits: List[float]) -> float:
        """Calculate downside deviation (only negative returns)."""
        if not profits:
            return 0.0

        negative_profits = [p for p in profits if p < 0]

        if not negative_profits:
            return 0.0

        mean_negative = sum(negative_profits) / len(negative_profits)
        variance = sum((p - mean_negative) ** 2 for p in negative_profits) / len(negative_profits)
        return variance ** 0.5

    def _calculate_profit_consistency_ratio(self, closed_trades: List[TradeData]) -> float:
        """Calculate profit consistency ratio."""
        if not closed_trades:
            return 0.0

        profitable_trades = sum(1 for trade in closed_trades if trade.profit > 0)
        total_trades = len(closed_trades)

        # Calculate consistency based on win rate and trade distribution
        win_rate = profitable_trades / total_trades

        # Additional consistency metrics
        profits = [trade.profit for trade in closed_trades]
        positive_profits = [p for p in profits if p > 0]

        if positive_profits:
            avg_win = sum(positive_profits) / len(positive_profits)
            consistency_score = win_rate * (avg_win / max(profits)) if max(profits) > 0 else 0
            return consistency_score * 100  # As percentage
        else:
            return 0.0

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data for advanced calculations."""
        if not isinstance(data, dict):
            return False

        closed_trades = data.get('closed_trades', [])
        if not isinstance(closed_trades, list):
            return False

        return True

