"""
R-Multiple Validation Utilities
Comprehensive validation and error checking for R-Multiple calculations.
"""

from typing import List, Dict, Any, Tuple, Optional
import math
try:
    # Try relative imports first (for package usage)
    from ..models import TradeData, RMultipleData, RMultipleStatistics
    from .logging_utils import LoggerMixin
except ImportError:
    # Fall back to absolute imports (for direct execution)
    from models.data_models import TradeData, RMultipleData, RMultipleStatistics
    from utils.logging_utils import LoggerMixin


class RMultipleValidator(LoggerMixin):
    """
    Comprehensive validator for R-Multiple calculations.
    Ensures data integrity and calculation accuracy.
    """

    def __init__(self):
        """Initialize the R-Multiple validator."""
        self.log_info("R-Multiple Validator initialized")

    def validate_trade_data_for_r_multiple(self, trade: TradeData) -> Tuple[bool, List[str]]:
        """
        Validate a single trade for R-Multiple calculation.

        Args:
            trade: TradeData object to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check if trade is closed
        if not trade.is_closed_trade():
            issues.append("Trade is not closed")
            return False, issues

        # Validate entry price
        if trade.price <= 0:
            issues.append("Invalid entry price (must be positive)")

        # Validate exit price
        if trade.close_price <= 0:
            issues.append("Invalid close price (must be positive)")

        # Validate stop loss
        if trade.s_l <= 0:
            issues.append("Missing or invalid stop loss (must be positive)")

        # Validate trade type
        if trade.type.lower() not in ['buy', 'sell']:
            issues.append("Invalid trade type (must be 'buy' or 'sell')")

        # Validate stop loss position relative to entry
        if trade.s_l > 0 and trade.price > 0:
            if trade.type.lower() == 'buy' and trade.s_l >= trade.price:
                issues.append("BUY trade stop loss must be below entry price")
            elif trade.type.lower() == 'sell' and trade.s_l <= trade.price:
                issues.append("SELL trade stop loss must be above entry price")

        # Validate take profit if present
        if trade.t_p > 0:
            if trade.type.lower() == 'buy' and trade.t_p <= trade.price:
                issues.append("BUY trade take profit must be above entry price")
            elif trade.type.lower() == 'sell' and trade.t_p >= trade.price:
                issues.append("SELL trade take profit must be below entry price")

        is_valid = len(issues) == 0
        return is_valid, issues

    def validate_r_multiple_calculation(self, r_trade: RMultipleData) -> Tuple[bool, List[str]]:
        """
        Validate R-Multiple calculation for a trade.

        Args:
            r_trade: RMultipleData object with calculated R-Multiple

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Validate basic data
        if not r_trade.ticket:
            issues.append("Missing trade ticket")

        if not r_trade.type:
            issues.append("Missing trade type")

        # Validate R-Multiple calculation
        if not r_trade.is_valid_r_trade:
            issues.append("Trade marked as invalid for R-Multiple calculation")
            return False, issues

        # Manually recalculate R-Multiple for verification
        expected_r = self._calculate_expected_r_multiple(r_trade)

        if abs(r_trade.r_multiple - expected_r) > 0.001:  # Allow for small floating point differences
            issues.append(f"R-Multiple calculation mismatch. Expected: {expected_r:.6f}, Got: {r_trade.r_multiple:.6f}")

        # Validate risk-reward ratio if take profit is set
        if r_trade.take_profit > 0 and r_trade.risk_reward_ratio > 0:
            expected_rr = self._calculate_expected_risk_reward_ratio(r_trade)
            if abs(r_trade.risk_reward_ratio - expected_rr) > 0.001:
                issues.append(f"Risk-Reward ratio mismatch. Expected: {expected_rr:.6f}, Got: {r_trade.risk_reward_ratio:.6f}")

        is_valid = len(issues) == 0
        return is_valid, issues

    def _calculate_expected_r_multiple(self, r_trade: RMultipleData) -> float:
        """Calculate expected R-Multiple for validation."""
        if r_trade.type.lower() == 'buy':
            if r_trade.stop_loss >= r_trade.entry_price:
                return 0.0
            initial_risk = r_trade.entry_price - r_trade.stop_loss
            actual_profit = r_trade.exit_price - r_trade.entry_price
        elif r_trade.type.lower() == 'sell':
            if r_trade.stop_loss <= r_trade.entry_price:
                return 0.0
            initial_risk = r_trade.stop_loss - r_trade.entry_price
            actual_profit = r_trade.entry_price - r_trade.exit_price
        else:
            return 0.0

        return actual_profit / initial_risk if initial_risk > 0 else 0.0

    def _calculate_expected_risk_reward_ratio(self, r_trade: RMultipleData) -> float:
        """Calculate expected risk-reward ratio for validation."""
        if r_trade.take_profit <= 0:
            return 0.0

        if r_trade.type.lower() == 'buy':
            if r_trade.stop_loss >= r_trade.entry_price:
                return 0.0
            risk = r_trade.entry_price - r_trade.stop_loss
            reward = r_trade.take_profit - r_trade.entry_price
        elif r_trade.type.lower() == 'sell':
            if r_trade.stop_loss <= r_trade.entry_price:
                return 0.0
            risk = r_trade.stop_loss - r_trade.entry_price
            reward = r_trade.entry_price - r_trade.take_profit
        else:
            return 0.0

        return reward / risk if risk > 0 else 0.0

    def validate_statistics_calculation(self, trades: List[RMultipleData],
                                       statistics: RMultipleStatistics) -> Tuple[bool, List[str]]:
        """
        Validate statistical calculations for R-Multiple data.

        Args:
            trades: List of R-Multiple trades
            statistics: Calculated statistics

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        if not trades:
            return True, []  # Empty data is valid

        valid_trades = [t for t in trades if t.is_valid_r_trade]

        # Validate basic counts
        if len(valid_trades) != statistics.total_valid_r_trades:
            issues.append(f"Trade count mismatch. Expected: {len(valid_trades)}, Got: {statistics.total_valid_r_trades}")

        if len(valid_trades) == 0:
            return len(issues) == 0, issues

        # Validate win rate calculation
        winning_trades = [t for t in valid_trades if t.r_multiple > 0]
        expected_win_rate = (len(winning_trades) / len(valid_trades)) * 100

        if abs(statistics.r_win_rate - expected_win_rate) > 0.1:  # Allow 0.1% tolerance
            issues.append(f"Win rate mismatch. Expected: {expected_win_rate:.2f}%, Got: {statistics.r_win_rate:.2f}%")

        # Validate average R-Multiple
        r_values = [t.r_multiple for t in valid_trades]
        expected_avg_r = sum(r_values) / len(r_values)

        if abs(statistics.average_r_multiple - expected_avg_r) > 0.001:
            issues.append(f"Average R-Multiple mismatch. Expected: {expected_avg_r:.6f}, Got: {statistics.average_r_multiple:.6f}")

        # Validate R-Multiple distribution
        distribution = statistics.r_distribution
        total_in_distribution = sum(distribution.values())

        if total_in_distribution != statistics.total_valid_r_trades:
            issues.append(f"Distribution total mismatch. Expected: {statistics.total_valid_r_trades}, Got: {total_in_distribution}")

        # Validate expectancy calculation
        expected_expectancy = (statistics.r_win_rate / 100 * statistics.average_winning_r) + \
                             ((100 - statistics.r_win_rate) / 100 * statistics.average_losing_r)

        if abs(statistics.r_expectancy - expected_expectancy) > 0.001:
            issues.append(f"R Expectancy mismatch. Expected: {expected_expectancy:.6f}, Got: {statistics.r_expectancy:.6f}")

        is_valid = len(issues) == 0
        return is_valid, issues

    def generate_comprehensive_validation_report(self, original_trades: List[TradeData],
                                               r_trades: List[RMultipleData],
                                               statistics: RMultipleStatistics) -> Dict[str, Any]:
        """
        Generate comprehensive validation report for R-Multiple calculations.

        Args:
            original_trades: Original TradeData objects
            r_trades: Converted RMultipleData objects
            statistics: Calculated R-Multiple statistics

        Returns:
            Comprehensive validation report
        """
        report = {
            'summary': {},
            'trade_validation': {},
            'calculation_validation': {},
            'statistics_validation': {},
            'recommendations': []
        }

        # Summary statistics
        total_original = len(original_trades)
        total_r_trades = len(r_trades)
        valid_r_trades = [t for t in r_trades if t.is_valid_r_trade]

        report['summary'] = {
            'total_original_trades': total_original,
            'total_r_trades_converted': total_r_trades,
            'valid_r_trades': len(valid_r_trades),
            'invalid_r_trades': total_r_trades - len(valid_r_trades),
            'validation_rate': (len(valid_r_trades) / total_original * 100) if total_original > 0 else 0.0
        }

        # Trade validation details
        trade_issues = []
        for i, trade in enumerate(original_trades):
            is_valid, issues = self.validate_trade_data_for_r_multiple(trade)
            if not is_valid:
                trade_issues.append({
                    'trade_index': i,
                    'ticket': trade.ticket,
                    'issues': issues
                })

        report['trade_validation'] = {
            'total_issues': len(trade_issues),
            'issues_by_trade': trade_issues
        }

        # Calculation validation
        calc_issues = []
        for r_trade in valid_r_trades:
            is_valid, issues = self.validate_r_multiple_calculation(r_trade)
            if not is_valid:
                calc_issues.append({
                    'ticket': r_trade.ticket,
                    'issues': issues
                })

        report['calculation_validation'] = {
            'total_calculation_issues': len(calc_issues),
            'calculation_issues': calc_issues
        }

        # Statistics validation
        stats_valid, stats_issues = self.validate_statistics_calculation(r_trades, statistics)
        report['statistics_validation'] = {
            'is_valid': stats_valid,
            'issues': stats_issues
        }

        # Generate recommendations
        recommendations = []

        if report['summary']['validation_rate'] < 80:
            recommendations.append("Low validation rate - review data quality and missing stop losses")

        if report['trade_validation']['total_issues'] > 0:
            recommendations.append("Address trade data issues to improve R-Multiple calculation accuracy")

        if report['calculation_validation']['total_calculation_issues'] > 0:
            recommendations.append("Review R-Multiple calculation logic for identified issues")

        if not stats_valid:
            recommendations.append("Statistics calculation errors detected - verify implementation")

        if statistics.total_valid_r_trades > 0:
            if statistics.r_expectancy <= 0:
                recommendations.append("Negative R expectancy - strategy needs improvement")
            elif statistics.r_expectancy < 0.2:
                recommendations.append("Low R expectancy - consider optimizing risk management")

            if statistics.average_losing_r > -1.0:
                recommendations.append("Average losing trade exceeds 1R - review stop loss placement")

        report['recommendations'] = recommendations

        return report

    def print_validation_report(self, report: Dict[str, Any]) -> None:
        """
        Print formatted validation report.

        Args:
            report: Validation report dictionary
        """
        print("\n" + "="*80)
        print("🔍 R-MULTIPLE VALIDATION REPORT")
        print("="*80)

        # Summary
        summary = report['summary']
        print("\n📊 SUMMARY:")
        print(f"  Original Trades: {summary['total_original_trades']}")
        print(f"  R-Trades Converted: {summary['total_r_trades_converted']}")
        print(f"  Valid R-Trades: {summary['valid_r_trades']}")
        print(f"  Invalid R-Trades: {summary['invalid_r_trades']}")
        print(f"  Validation Rate: {summary['validation_rate']:.1f}%")

        # Trade validation
        trade_val = report['trade_validation']
        if trade_val['total_issues'] > 0:
            print("\n⚠️  TRADE VALIDATION ISSUES:")
            print(f"  Total Issues: {trade_val['total_issues']}")
            for issue in trade_val['issues_by_trade'][:5]:  # Show first 5 issues
                print(f"    Trade {issue['ticket']}: {', '.join(issue['issues'])}")
            if trade_val['total_issues'] > 5:
                print(f"    ... and {trade_val['total_issues'] - 5} more issues")

        # Calculation validation
        calc_val = report['calculation_validation']
        if calc_val['total_calculation_issues'] > 0:
            print("\n❌ CALCULATION VALIDATION ISSUES:")
            print(f"  Total Issues: {calc_val['total_calculation_issues']}")
            for issue in calc_val['calculation_issues'][:3]:  # Show first 3 issues
                print(f"    Trade {issue['ticket']}: {', '.join(issue['issues'])}")
            if calc_val['total_calculation_issues'] > 3:
                print(f"    ... and {calc_val['total_calculation_issues'] - 3} more issues")

        # Statistics validation
        stats_val = report['statistics_validation']
        if not stats_val['is_valid']:
            print("\n📈 STATISTICS VALIDATION ISSUES:")
            for issue in stats_val['issues']:
                print(f"    {issue}")

        # Recommendations
        if report['recommendations']:
            print("\n💡 RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"    • {rec}")

        print("\n" + "="*80)
