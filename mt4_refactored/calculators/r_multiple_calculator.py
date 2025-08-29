"""
R-Multiple Calculator Module
Implements comprehensive R-Multiple analysis for trading performance evaluation.

This module provides industry-standard R-Multiple calculations including:
- Core R-Multiple formulas for BUY/SELL trades
- Statistical analysis and distribution metrics
- Risk-adjusted performance measures
- Advanced analytics and expectancy calculations
- Consecutive trade analysis and streak detection
"""

from typing import List, Dict, Any, Tuple, Optional
import math
import statistics
from dataclasses import dataclass

try:
    # Try relative imports first (for package usage)
    from ..models import TradeData, RMultipleData, RMultipleStatistics
    from ..utils import LoggerMixin, RMultipleValidator
except ImportError:
    # Fall back to absolute imports (for direct execution)
    from models.data_models import TradeData, RMultipleData, RMultipleStatistics
    from utils.logging_utils import LoggerMixin
    from utils.r_multiple_validation import RMultipleValidator


@dataclass
class RMultipleCalculatorResult:
    """Container for R-Multiple calculation results."""
    r_multiple_data: List[RMultipleData]
    statistics: RMultipleStatistics
    validation_report: Dict[str, Any]


class RMultipleCalculator(LoggerMixin):
    """
    Comprehensive R-Multiple calculator implementing industry-standard formulas.

    Provides optimized single-pass calculations for maximum performance and accuracy.
    """

    def __init__(self):
        """Initialize the R-Multiple calculator."""
        self.log_info("R-Multiple Calculator initialized")
        self.validator = RMultipleValidator()

    def calculate_comprehensive_r_analysis(self, closed_trades: List[TradeData]) -> RMultipleCalculatorResult:
        """
        Perform comprehensive R-Multiple analysis on closed trades with validation.

        Args:
            closed_trades: List of closed trade data

        Returns:
            RMultipleCalculatorResult: Complete analysis results
        """
        self.log_info(f"Starting comprehensive R-Multiple analysis for {len(closed_trades)} trades")

        # Step 1: Convert trades to R-Multiple format
        r_multiple_data = self._convert_trades_to_r_format(closed_trades)

        # Step 2: Validate and calculate R-Multiples
        valid_r_trades = self._calculate_and_validate_r_multiples(r_multiple_data)

        # Step 3: Perform statistical analysis with validation
        statistics = self._calculate_r_statistics_with_validation(valid_r_trades)

        # Step 4: Generate comprehensive validation report
        validation_report = self.validator.generate_comprehensive_validation_report(
            closed_trades, r_multiple_data, statistics
        )

        result = RMultipleCalculatorResult(
            r_multiple_data=valid_r_trades,
            statistics=statistics,
            validation_report=validation_report
        )

        # Print validation report if there are issues
        if validation_report['summary']['validation_rate'] < 100:
            self.validator.print_validation_report(validation_report)

        self.log_info(f"R-Multiple analysis completed. Valid trades: {len(valid_r_trades)}")
        return result

    def _calculate_and_validate_r_multiples(self, r_trades: List[RMultipleData]) -> List[RMultipleData]:
        """
        Calculate R-Multiples for trades with comprehensive validation.

        Args:
            r_trades: List of RMultipleData objects

        Returns:
            List[RMultipleData]: Valid trades with calculated R-Multiples
        """
        valid_trades = []

        for r_trade in r_trades:
            # Calculate R-Multiple
            r_value = r_trade.calculate_r_multiple()

            # Validate the calculation
            is_valid, issues = self.validator.validate_r_multiple_calculation(r_trade)

            if is_valid and r_trade.is_valid_r_trade:
                valid_trades.append(r_trade)
                self.log_debug(f"Trade {r_trade.ticket}: R = {r_value:.3f} ✓")
            else:
                self.log_warning(f"Trade {r_trade.ticket}: Invalid R-Multiple calculation - {', '.join(issues)}")

        self.log_info(f"Validated R-Multiples for {len(valid_trades)} trades")
        return valid_trades

    def _calculate_r_statistics_with_validation(self, valid_r_trades: List[RMultipleData]) -> RMultipleStatistics:
        """
        Calculate R-Multiple statistics with validation.

        Args:
            valid_r_trades: List of valid R-Multiple trades

        Returns:
            RMultipleStatistics: Validated statistical analysis
        """
        statistics = self._calculate_r_statistics(valid_r_trades)

        # Validate statistics calculation
        is_valid, issues = self.validator.validate_statistics_calculation(valid_r_trades, statistics)

        if not is_valid:
            self.log_warning(f"Statistics validation issues: {', '.join(issues)}")
            for issue in issues:
                self.log_warning(f"  - {issue}")

        return statistics

    def _convert_trades_to_r_format(self, closed_trades: List[TradeData]) -> List[RMultipleData]:
        """
        Convert TradeData objects to RMultipleData format with validation.

        Args:
            closed_trades: List of TradeData objects

        Returns:
            List[RMultipleData]: Converted R-Multiple data
        """
        r_trades = []

        for trade in closed_trades:
            # Only process closed trades with required data
            if not trade.is_closed_trade():
                self.log_debug(f"Trade {trade.ticket}: Skipped - not closed")
                continue

            # Validate trade data for R-Multiple calculation
            is_valid, issues = self.validator.validate_trade_data_for_r_multiple(trade)

            if not is_valid:
                self.log_warning(f"Trade {trade.ticket}: Invalid for R-Multiple - {', '.join(issues)}")
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
            self.log_debug(f"Trade {trade.ticket}: Converted to R-Multiple format")

        self.log_info(f"Converted {len(r_trades)} trades to R-Multiple format (from {len(closed_trades)} closed trades)")
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
            r_value = r_trade.calculate_r_multiple()
            if r_trade.is_valid_r_trade:
                valid_trades.append(r_trade)
                self.log_debug(f"Trade {r_trade.ticket}: R = {r_value:.3f}")

        self.log_info(f"Calculated R-Multiples for {len(valid_trades)} valid trades")
        return valid_trades

    def _calculate_r_statistics(self, valid_r_trades: List[RMultipleData]) -> RMultipleStatistics:
        """
        Calculate comprehensive R-Multiple statistics in a single optimized pass.

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

        # Single pass through all trades for efficiency
        winning_r_values = []
        losing_r_values = []
        all_r_values = []
        cumulative_r = 0.0
        peak_cumulative_r = 0.0
        max_drawdown_r = 0.0

        # Distribution counters
        distribution = {
            'below_-2r': 0, '-2r_to_-1r': 0, '-1r_to_0r': 0,
            '0r_to_+1r': 0, '+1r_to_+2r': 0, 'above_+2r': 0
        }

        # Consecutive analysis variables
        current_win_streak = 0
        current_loss_streak = 0
        win_streaks = []
        loss_streaks = []

        for r_trade in valid_r_trades:
            r_value = r_trade.r_multiple
            all_r_values.append(r_value)

            # Update cumulative R and drawdown tracking
            cumulative_r += r_value
            peak_cumulative_r = max(peak_cumulative_r, cumulative_r)
            current_drawdown = peak_cumulative_r - cumulative_r
            max_drawdown_r = max(max_drawdown_r, current_drawdown)

            # Categorize R-Multiple for distribution
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

            # Separate winning and losing trades
            if r_value > 0:
                winning_r_values.append(r_value)

                # Handle consecutive wins
                if current_loss_streak > 0:
                    loss_streaks.append(current_loss_streak)
                    current_loss_streak = 0
                current_win_streak += 1
            elif r_value < 0:
                losing_r_values.append(r_value)

                # Handle consecutive losses
                if current_win_streak > 0:
                    win_streaks.append(current_win_streak)
                    current_win_streak = 0
                current_loss_streak += 1
            else:
                # Breakeven trade - reset both streaks
                if current_win_streak > 0:
                    win_streaks.append(current_win_streak)
                    current_win_streak = 0
                if current_loss_streak > 0:
                    loss_streaks.append(current_loss_streak)
                    current_loss_streak = 0

        # Handle final streaks
        if current_win_streak > 0:
            win_streaks.append(current_win_streak)
        if current_loss_streak > 0:
            loss_streaks.append(current_loss_streak)

        # Calculate basic statistics
        stats.r_win_rate = (len(winning_r_values) / len(valid_r_trades)) * 100 if valid_r_trades else 0.0
        stats.average_r_multiple = statistics.mean(all_r_values) if all_r_values else 0.0
        stats.average_winning_r = statistics.mean(winning_r_values) if winning_r_values else 0.0
        stats.average_losing_r = statistics.mean(losing_r_values) if losing_r_values else 0.0
        stats.r_distribution = distribution

        # Calculate R-Multiple Expectancy
        win_rate_decimal = stats.r_win_rate / 100.0
        loss_rate_decimal = 1.0 - win_rate_decimal
        stats.r_expectancy = (win_rate_decimal * stats.average_winning_r) + \
                           (loss_rate_decimal * stats.average_losing_r)

        # Calculate risk-adjusted metrics
        if len(all_r_values) > 1:
            stats.r_volatility = statistics.stdev(all_r_values)
            stats.r_sharpe_ratio = self._calculate_r_sharpe_ratio(all_r_values)
            stats.r_sortino_ratio = self._calculate_r_sortino_ratio(all_r_values)

            # Calculate skewness and kurtosis
            stats.r_skewness, stats.r_kurtosis = self._calculate_r_moments(all_r_values)

        # Update drawdown and recovery
        stats.max_r_drawdown = max_drawdown_r
        if max_drawdown_r > 0:
            stats.r_recovery_factor = cumulative_r / max_drawdown_r

        # Consecutive statistics
        stats.max_consecutive_r_wins = max(win_streaks) if win_streaks else 0
        stats.max_consecutive_r_losses = max(loss_streaks) if loss_streaks else 0
        stats.average_r_win_streak = statistics.mean(win_streaks) if win_streaks else 0.0
        stats.average_r_loss_streak = statistics.mean(loss_streaks) if loss_streaks else 0.0

        self.log_info(f"Calculated comprehensive R-Multiple statistics for {stats.total_valid_r_trades} trades")
        return stats

    def _calculate_r_sharpe_ratio(self, r_values: List[float]) -> float:
        """Calculate R-Multiple Sharpe Ratio."""
        if len(r_values) < 2:
            return 0.0

        mean_r = statistics.mean(r_values)
        std_r = statistics.stdev(r_values)
        risk_free_r = 0.0  # Assuming 0% risk-free rate for R-Multiple analysis

        return (mean_r - risk_free_r) / std_r if std_r > 0 else 0.0

    def _calculate_r_sortino_ratio(self, r_values: List[float]) -> float:
        """Calculate R-Multiple Sortino Ratio (downside deviation only)."""
        if len(r_values) < 2:
            return 0.0

        mean_r = statistics.mean(r_values)
        risk_free_r = 0.0

        # Calculate downside deviation
        negative_returns = [r for r in r_values if r < risk_free_r]
        if not negative_returns:
            return float('inf')  # No downside risk

        downside_variance = sum((r - risk_free_r) ** 2 for r in negative_returns) / len(negative_returns)
        downside_deviation = math.sqrt(downside_variance)

        return (mean_r - risk_free_r) / downside_deviation if downside_deviation > 0 else float('inf')

    def _calculate_r_moments(self, r_values: List[float]) -> Tuple[float, float]:
        """Calculate skewness and excess kurtosis for R-Multiple distribution."""
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
        kurtosis = (kurtosis_sum / len(r_values)) - 3  # Excess kurtosis

        return skewness, kurtosis

    def _generate_validation_report(self, original_trades: List[TradeData],
                                  valid_r_trades: List[RMultipleData]) -> Dict[str, Any]:
        """
        Generate comprehensive validation report for R-Multiple calculations.

        Args:
            original_trades: Original closed trades
            valid_r_trades: Valid R-Multiple trades

        Returns:
            Dict containing validation metrics and issues
        """
        total_original = len(original_trades)
        total_valid = len(valid_r_trades)
        invalid_count = total_original - total_valid

        report = {
            'total_original_trades': total_original,
            'total_valid_r_trades': total_valid,
            'invalid_trades': invalid_count,
            'validation_rate': (total_valid / total_original * 100) if total_original > 0 else 0.0,
            'issues': []
        }

        # Analyze validation issues
        if invalid_count > 0:
            issues = []

            # Check for missing stop losses
            missing_sl = sum(1 for trade in original_trades if trade.s_l <= 0)
            if missing_sl > 0:
                issues.append(f"Missing stop loss: {missing_sl} trades")

            # Check for invalid trade types
            invalid_types = sum(1 for trade in original_trades
                              if trade.type.lower() not in ['buy', 'sell'])
            if invalid_types > 0:
                issues.append(f"Invalid trade type: {invalid_types} trades")

            # Check for missing close prices
            missing_close = sum(1 for trade in original_trades if trade.close_price <= 0)
            if missing_close > 0:
                issues.append(f"Missing close price: {missing_close} trades")

            report['issues'] = issues

        # Performance validation
        if valid_r_trades:
            r_values = [trade.r_multiple for trade in valid_r_trades]
            report['r_range'] = {
                'min_r': min(r_values),
                'max_r': max(r_values),
                'median_r': statistics.median(r_values)
            }

        self.log_info(f"Generated validation report: {total_valid}/{total_original} valid trades")
        return report

    def get_r_distribution_summary(self, statistics: RMultipleStatistics) -> Dict[str, Any]:
        """
        Generate human-readable R-Multiple distribution summary.

        Args:
            statistics: R-Multiple statistics

        Returns:
            Dict with formatted distribution data
        """
        total = statistics.total_valid_r_trades
        if total == 0:
            return {}

        distribution = statistics.r_distribution

        return {
            'below_-2r': {
                'count': distribution['below_-2r'],
                'percentage': (distribution['below_-2r'] / total) * 100
            },
            '-2r_to_-1r': {
                'count': distribution['-2r_to_-1r'],
                'percentage': (distribution['-2r_to_-1r'] / total) * 100
            },
            '-1r_to_0r': {
                'count': distribution['-1r_to_0r'],
                'percentage': (distribution['-1r_to_0r'] / total) * 100
            },
            '0r_to_+1r': {
                'count': distribution['0r_to_+1r'],
                'percentage': (distribution['0r_to_+1r'] / total) * 100
            },
            '+1r_to_+2r': {
                'count': distribution['+1r_to_+2r'],
                'percentage': (distribution['+1r_to_+2r'] / total) * 100
            },
            'above_+2r': {
                'count': distribution['above_+2r'],
                'percentage': (distribution['above_+2r'] / total) * 100
            }
        }

    def print_comprehensive_r_analysis(self, result: RMultipleCalculatorResult) -> None:
        """
        Print comprehensive R-Multiple analysis report.

        Args:
            result: Complete R-Multiple analysis results
        """
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE R-MULTIPLE ANALYSIS REPORT")
        print("="*80)

        # Validation Summary
        validation = result.validation_report
        summary = validation['summary']
        print("\n📊 VALIDATION SUMMARY:")
        print(f"  Total Original Trades: {summary['total_original_trades']}")
        print(f"  Valid R-Multiple Trades: {summary['valid_r_trades']}")
        print(f"  Validation Rate: {summary['validation_rate']:.1f}%")

        if validation.get('issues'):
            print(f"  Issues Found: {len(validation['issues'])}")
            for issue in validation['issues']:
                print(f"    • {issue}")

        # Basic R-Multiple Statistics
        stats = result.statistics
        if stats.total_valid_r_trades > 0:
            print("\n🎯 CORE R-MULTIPLE METRICS:")
            print(f"  R Win Rate: {stats.r_win_rate:.1f}%")
            print(f"  Average R-Multiple: {stats.average_r_multiple:.3f}R")
            print(f"  Average Winning R: {stats.average_winning_r:.3f}R")
            print(f"  Average Losing R: {stats.average_losing_r:.3f}R")
            print(f"  R-Multiple Expectancy: {stats.r_expectancy:.3f}R")

            # R-Multiple Distribution
            print("\n📈 R-MULTIPLE DISTRIBUTION:")
            dist = self.get_r_distribution_summary(stats)
            for range_name, data in dist.items():
                range_label = range_name.replace('_', ' ').replace('r', 'R').upper()
                print(f"  {range_label}: {data['count']} ({data['percentage']:.1f}%)")

            # Risk-Adjusted Performance
            print("\n⚠️  RISK-ADJUSTED PERFORMANCE:")
            print(f"  R Volatility (Std Dev): {stats.r_volatility:.3f}R")
            print(f"  R Sharpe Ratio: {stats.r_sharpe_ratio:.3f}")
            print(f"  R Sortino Ratio: {stats.r_sortino_ratio:.3f}")
            print(f"  Max R Drawdown: {stats.max_r_drawdown:.3f}R")
            print(f"  R Recovery Factor: {stats.r_recovery_factor:.3f}")

            # Statistical Analysis
            print("\n📉 STATISTICAL ANALYSIS:")
            print(f"  R Skewness: {stats.r_skewness:.3f}")
            print(f"  R Kurtosis (Excess): {stats.r_kurtosis:.3f}")

            # Consecutive Analysis
            print("\n🔄 CONSECUTIVE R-MULTIPLE ANALYSIS:")
            print(f"  Max Consecutive R Wins: {stats.max_consecutive_r_wins}")
            print(f"  Max Consecutive R Losses: {stats.max_consecutive_r_losses}")
            print(f"  Average R Win Streak: {stats.average_r_win_streak:.1f}")
            print(f"  Average R Loss Streak: {stats.average_r_loss_streak:.1f}")

            # Performance Rating
            rating = stats.get_r_performance_rating()
            print("\n🏆 R-MULTIPLE PERFORMANCE RATING:")
            print(f"  Rating: {rating}")

            # Interpretation
            if stats.r_expectancy > 0.5:
                print("  💪 Excellent: Strong positive expectancy indicates profitable system")
            elif stats.r_expectancy > 0.2:
                print("  👍 Good: Positive expectancy with room for improvement")
            elif stats.r_expectancy > 0:
                print("  ⚠️  Fair: Slightly positive but needs optimization")
            else:
                print("  ❌ Needs Work: Negative expectancy requires strategy review")

        print("\n" + "="*80)
