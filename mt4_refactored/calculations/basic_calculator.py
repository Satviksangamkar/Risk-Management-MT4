"""
Basic Calculator for MT4 Parser
Handles basic trading metrics calculations.
"""

from typing import Dict, Any, List, Optional
import statistics

from ..core.interfaces import ICalculator
from ..core.exceptions import MT4CalculationError
from ..config import MT4Config
from ..models import CalculatedMetrics, TradeData, FinancialSummary, PerformanceMetrics
from ..utils import LoggerMixin


class BasicCalculator(LoggerMixin, ICalculator):
    """
    Calculator for basic trading metrics.

    Provides optimized single-pass calculations for:
    - Financial summary metrics
    - Risk metrics
    - Statistical analysis
    - Performance metrics
    """

    def __init__(self, config: Optional[MT4Config] = None):
        """
        Initialize the basic calculator.

        Args:
            config: Configuration object
        """
        self.config = config or MT4Config()
        self.log_info("Basic Calculator initialized")

    def calculate(self, data: Dict[str, Any]) -> CalculatedMetrics:
        """
        Calculate basic trading metrics using optimized single-pass algorithm.

        Args:
            data: Dictionary containing closed_trades, financial_summary, performance_metrics

        Returns:
            CalculatedMetrics: Complete set of calculated metrics

        Raises:
            MT4CalculationError: If calculation fails
        """
        try:
            closed_trades = data.get('closed_trades', [])
            financial_summary = data.get('financial_summary')
            performance_metrics = data.get('performance_metrics')

            if not closed_trades:
                self.log_warning("No closed trades provided for calculation")
                return CalculatedMetrics()

            self.log_info(f"Calculating basic metrics for {len(closed_trades)} trades")

            # Single-pass calculation for maximum efficiency
            trade_stats = self._calculate_trade_statistics_single_pass(closed_trades)

            # Create result object
            metrics = CalculatedMetrics()

            # Financial Summary (5 formulas)
            self._apply_financial_summary_formulas(metrics, trade_stats, financial_summary)

            # Risk Metrics (5 formulas)
            self._apply_risk_metrics_formulas(metrics, trade_stats, performance_metrics)

            # Statistical Analysis (2 formulas)
            self._apply_statistical_analysis_formulas(metrics, trade_stats)

            # Drawdown Analysis (2 formulas)
            self._apply_drawdown_analysis_formulas(metrics, performance_metrics)

            # Performance Metrics (2 formulas)
            self._apply_performance_metrics_formulas(metrics, trade_stats)

            # Additional metrics for compatibility
            self._apply_additional_metrics(metrics, financial_summary, trade_stats)

            self.log_info("Basic metrics calculation completed")
            return metrics

        except Exception as e:
            self.log_error(f"Basic metrics calculation failed: {e}")
            raise MT4CalculationError(f"Failed to calculate basic metrics: {str(e)}", details=e) from e

    def _calculate_trade_statistics_single_pass(self, closed_trades: List[TradeData]) -> Dict[str, Any]:
        """
        Calculate all trade statistics in a single pass through the data.

        Returns:
            dict: All calculated trade statistics
        """
        # Initialize accumulators
        profits = []
        winning_trades = []
        losing_trades = []
        total_profit_sum = 0.0
        gross_profit_sum = 0.0
        gross_loss_sum = 0.0

        # Single pass through all trades
        for trade in closed_trades:
            profit = trade.profit
            profits.append(profit)
            total_profit_sum += profit

            if profit > 0:
                winning_trades.append(profit)
                gross_profit_sum += profit
            elif profit < 0:
                losing_trades.append(abs(profit))
                gross_loss_sum += abs(profit)

        # Calculate basic metrics
        total_trades = len(closed_trades)
        win_count = len(winning_trades)
        loss_count = len(losing_trades)

        # Financial metrics
        gross_profit = gross_profit_sum
        gross_loss = gross_loss_sum
        total_net_profit = total_profit_sum
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else (float('inf') if gross_profit > 0 else 0.0)
        expected_payoff = total_net_profit / total_trades if total_trades > 0 else 0.0

        # Risk metrics
        win_rate = (win_count / total_trades) * 100 if total_trades > 0 else 0.0
        win_loss_ratio = win_count / loss_count if loss_count > 0 else 0.0

        # Averages
        avg_win = sum(winning_trades) / len(winning_trades) if winning_trades else 0.0
        avg_loss = sum(losing_trades) / len(losing_trades) if losing_trades else 0.0
        risk_reward_ratio = avg_win / avg_loss if avg_loss > 0 else 0.0

        # Statistical calculations
        mean = total_net_profit / total_trades if total_trades > 0 else 0.0
        variance = sum((p - mean) ** 2 for p in profits) / total_trades if total_trades > 1 else 0.0
        std_dev = variance ** 0.5 if total_trades > 1 else 0.0

        # Higher moments
        skewness = 0.0
        kurtosis = 0.0
        if std_dev > 0 and total_trades >= 3:
            third_moment = sum(((p - mean) / std_dev) ** 3 for p in profits) / total_trades
            skewness = third_moment
            if total_trades >= 4:
                fourth_moment = sum(((p - mean) / std_dev) ** 4 for p in profits) / total_trades
                kurtosis = fourth_moment - 3  # Excess kurtosis

        # Expectancy
        expectancy = 0.0
        if total_trades > 0:
            win_rate_decimal = win_rate / 100.0
            loss_rate_decimal = (loss_count / total_trades) if total_trades > 0 else 0.0
            expectancy = (win_rate_decimal * avg_win) - (loss_rate_decimal * avg_loss)

        return {
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'total_net_profit': total_net_profit,
            'profit_factor': profit_factor,
            'expected_payoff': expected_payoff,
            'win_rate': win_rate,
            'win_loss_ratio': win_loss_ratio,
            'risk_reward_ratio': risk_reward_ratio,
            'average_win': avg_win,
            'average_loss': avg_loss,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'expectancy': expectancy,
            'standard_deviation': std_dev,
            'total_trades': total_trades,
            'win_count': win_count,
            'loss_count': loss_count
        }

    def _apply_financial_summary_formulas(
        self,
        metrics: CalculatedMetrics,
        trade_stats: Dict[str, Any],
        financial_summary: Optional[FinancialSummary]
    ) -> None:
        """Apply financial summary formulas."""
        metrics.gross_profit = trade_stats['gross_profit']
        metrics.gross_loss = trade_stats['gross_loss']
        metrics.total_net_profit = trade_stats['total_net_profit']
        metrics.profit_factor = trade_stats['profit_factor']
        metrics.expected_payoff = trade_stats['expected_payoff']

    def _apply_risk_metrics_formulas(
        self,
        metrics: CalculatedMetrics,
        trade_stats: Dict[str, Any],
        performance_metrics: Optional[PerformanceMetrics]
    ) -> None:
        """Apply risk metrics formulas."""
        metrics.win_rate = trade_stats['win_rate']
        metrics.risk_reward_ratio = trade_stats['risk_reward_ratio']
        metrics.maximum_drawdown_percentage = (
            performance_metrics.maximal_drawdown_percentage
            if performance_metrics else 0.0
        )

        # Recovery factor
        if performance_metrics and performance_metrics.maximal_drawdown_amount > 0:
            metrics.recovery_factor = trade_stats['total_net_profit'] / performance_metrics.maximal_drawdown_amount

        # Kelly Criterion
        metrics.kelly_percentage = self._calculate_kelly_percentage(
            metrics.win_rate, metrics.risk_reward_ratio
        )

    def _apply_statistical_analysis_formulas(
        self,
        metrics: CalculatedMetrics,
        trade_stats: Dict[str, Any]
    ) -> None:
        """Apply statistical analysis formulas."""
        metrics.skewness = trade_stats['skewness']
        metrics.kurtosis = trade_stats['kurtosis']

    def _apply_drawdown_analysis_formulas(
        self,
        metrics: CalculatedMetrics,
        performance_metrics: Optional[PerformanceMetrics]
    ) -> None:
        """Apply drawdown analysis formulas."""
        if performance_metrics:
            metrics.relative_drawdown_percentage = performance_metrics.relative_drawdown_percentage
            metrics.absolute_drawdown = performance_metrics.relative_drawdown_amount

    def _apply_performance_metrics_formulas(
        self,
        metrics: CalculatedMetrics,
        trade_stats: Dict[str, Any]
    ) -> None:
        """Apply performance metrics formulas."""
        metrics.expectancy = trade_stats['expectancy']
        metrics.standard_deviation = trade_stats['standard_deviation']

    def _apply_additional_metrics(
        self,
        metrics: CalculatedMetrics,
        financial_summary: Optional[FinancialSummary],
        trade_stats: Dict[str, Any]
    ) -> None:
        """Apply additional compatibility metrics."""
        if financial_summary:
            metrics.roi_percentage = self._calculate_roi(financial_summary)
            metrics.account_growth_percentage = self._calculate_account_growth(financial_summary)

        metrics.average_trade_profit = trade_stats['average_win']
        metrics.average_trade_loss = trade_stats['average_loss']
        metrics.win_loss_ratio = trade_stats['win_loss_ratio']

    def _calculate_kelly_percentage(self, win_rate: float, risk_reward_ratio: float) -> float:
        """Calculate Kelly Criterion percentage."""
        if risk_reward_ratio <= 0 or win_rate <= 0 or win_rate >= 100:
            return 0.0

        win_rate_decimal = win_rate / 100.0
        kelly = win_rate_decimal - ((1 - win_rate_decimal) / risk_reward_ratio)
        return max(0.0, kelly * 100)

    def _calculate_roi(self, financial_summary: FinancialSummary) -> float:
        """Calculate Return on Investment."""
        initial_deposit = financial_summary.deposit_withdrawal
        closed_pnl = financial_summary.closed_trade_pnl
        return (closed_pnl / initial_deposit) * 100 if initial_deposit > 0 else 0.0

    def _calculate_account_growth(self, financial_summary: FinancialSummary) -> float:
        """Calculate Account Growth."""
        initial_deposit = financial_summary.deposit_withdrawal
        balance = financial_summary.balance
        return ((balance - initial_deposit) / initial_deposit) * 100 if initial_deposit > 0 else 0.0

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data for calculations."""
        if not isinstance(data, dict):
            return False

        closed_trades = data.get('closed_trades', [])
        if not isinstance(closed_trades, list):
            return False

        return True

