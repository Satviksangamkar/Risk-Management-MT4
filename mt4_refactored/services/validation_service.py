"""
Validation Service for MT4 Parser
Handles data validation and integrity checks.
"""

from typing import Dict, Any, List, Optional
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
    from mt4_refactored.core.exceptions import MT4ValidationError
    from mt4_refactored.config.settings import MT4Config
    from mt4_refactored.models.data_models import (
        MT4StatementData,
        AccountInfo,
        FinancialSummary,
        PerformanceMetrics,
        TradeData
    )
    from mt4_refactored.utils.logging_utils import LoggerMixin
except ImportError:
    try:
        # Try direct module imports
        from core.interfaces import IService
        from core.exceptions import MT4ValidationError
        from config.settings import MT4Config
        from models.data_models import (
            MT4StatementData,
            AccountInfo,
            FinancialSummary,
            PerformanceMetrics,
            TradeData
        )
        from utils.logging_utils import LoggerMixin
    except ImportError as e:
        print(f"ValidationService import error: {e}")
        # Define fallback classes
        class IService: pass
        class MT4ValidationError(Exception): pass
        class MT4Config: pass
        class MT4StatementData: pass
        class AccountInfo: pass
        class FinancialSummary: pass
        class PerformanceMetrics: pass
        class TradeData: pass
        class LoggerMixin: pass


class ValidationService(LoggerMixin, IService):
    """
    Service for validating parsed MT4 data.

    Provides comprehensive validation including:
    - Data integrity checks
    - Business rule validation
    - Consistency validation
    - Required field validation
    """

    def __init__(self, config: Optional[MT4Config] = None):
        """
        Initialize the validation service.

        Args:
            config: Configuration object
        """
        self.config = config or MT4Config()
        self.log_info("Validation Service initialized")

    def process(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parsed data comprehensively.

        Args:
            parsed_data: Dictionary containing all parsed data sections

        Returns:
            Dict: Validation results with status and issues

        Raises:
            MT4ValidationError: If critical validation errors are found
        """
        try:
            self.log_info("Starting comprehensive data validation")

            validation_results = {
                'is_valid': True,
                'issues': [],
                'warnings': [],
                'sections': {}
            }

            # Validate each data section
            validation_results['sections']['account_info'] = self._validate_account_info(
                parsed_data.get('account_info')
            )

            validation_results['sections']['financial_summary'] = self._validate_financial_summary(
                parsed_data.get('financial_summary')
            )

            validation_results['sections']['performance_metrics'] = self._validate_performance_metrics(
                parsed_data.get('performance_metrics')
            )

            validation_results['sections']['trade_data'] = self._validate_trade_data(
                parsed_data.get('closed_trades', []),
                parsed_data.get('open_trades', [])
            )

            # Check for critical issues
            critical_issues = []
            for section_result in validation_results['sections'].values():
                if not section_result['is_valid']:
                    critical_issues.extend(section_result['issues'])

            # Overall validation status
            validation_results['is_valid'] = len(critical_issues) == 0

            if critical_issues:
                validation_results['issues'] = critical_issues
                self.log_warning(f"Validation found {len(critical_issues)} critical issues")

            self.log_info("Data validation completed")
            return validation_results

        except Exception as e:
            self.log_error(f"Validation process failed: {e}")
            raise MT4ValidationError(f"Failed to validate data: {str(e)}", details=e) from e

    def _validate_account_info(self, account_info: Optional[AccountInfo]) -> Dict[str, Any]:
        """Validate account information."""
        result = {'is_valid': True, 'issues': [], 'warnings': []}

        if not account_info:
            result['is_valid'] = False
            result['issues'].append("Account information is missing")
            return result

        # Check required fields
        if not account_info.account_number:
            result['issues'].append("Account number is missing")

        if not account_info.account_name:
            result['issues'].append("Account name is missing")

        if not account_info.currency:
            result['issues'].append("Account currency is missing")

        # Check for valid currency format
        if account_info.currency and len(account_info.currency) != 3:
            result['warnings'].append(f"Currency format may be invalid: {account_info.currency}")

        # Update validity
        result['is_valid'] = len(result['issues']) == 0

        return result

    def _validate_financial_summary(self, financial_summary: Optional[FinancialSummary]) -> Dict[str, Any]:
        """Validate financial summary."""
        result = {'is_valid': True, 'issues': [], 'warnings': []}

        if not financial_summary:
            result['is_valid'] = False
            result['issues'].append("Financial summary is missing")
            return result

        # Check for negative balance (critical)
        if financial_summary.balance < 0:
            result['issues'].append(f"Negative balance detected: {financial_summary.balance}")

        # Check for unrealistic values
        if financial_summary.balance > 10000000:  # 10 million
            result['warnings'].append(f"Very high balance detected: {financial_summary.balance}")

        # Check equity vs balance consistency
        expected_equity = financial_summary.balance + financial_summary.floating_pnl
        if abs(financial_summary.equity - expected_equity) > 0.01:
            result['warnings'].append("Equity calculation may be inconsistent")

        return result

    def _validate_performance_metrics(self, performance_metrics: Optional[PerformanceMetrics]) -> Dict[str, Any]:
        """Validate performance metrics."""
        result = {'is_valid': True, 'issues': [], 'warnings': []}

        if not performance_metrics:
            result['warnings'].append("Performance metrics are missing")
            return result

        # Check for invalid profit factor
        if performance_metrics.profit_factor < 0:
            result['issues'].append(f"Invalid profit factor: {performance_metrics.profit_factor}")

        # Check for unrealistic drawdown
        if performance_metrics.maximal_drawdown_percentage > 100:
            result['issues'].append(f"Invalid drawdown percentage: {performance_metrics.maximal_drawdown_percentage}%")

        # Check consistency between profit and drawdown
        if (performance_metrics.total_net_profit > 0 and
            performance_metrics.maximal_drawdown_amount > performance_metrics.total_net_profit):
            result['warnings'].append("Drawdown amount exceeds total profit")

        return result

    def _validate_trade_data(self, closed_trades: List[TradeData], open_trades: List[TradeData]) -> Dict[str, Any]:
        """Validate trade data."""
        result = {'is_valid': True, 'issues': [], 'warnings': []}

        all_trades = closed_trades + open_trades

        if not all_trades:
            result['warnings'].append("No trades found")
            return result

        # Validate individual trades
        for i, trade in enumerate(all_trades):
            trade_issues = self._validate_single_trade(trade, i)
            result['issues'].extend(trade_issues['issues'])
            result['warnings'].extend(trade_issues['warnings'])

        # Check for duplicate tickets
        tickets = [trade.ticket for trade in all_trades if trade.ticket]
        if len(tickets) != len(set(tickets)):
            result['issues'].append("Duplicate trade tickets found")

        # Check trade type consistency
        invalid_types = [trade.type for trade in all_trades
                        if trade.type and trade.type.lower() not in ['buy', 'sell', 'balance']]
        if invalid_types:
            result['issues'].append(f"Invalid trade types found: {set(invalid_types)}")

        # Update validity
        result['is_valid'] = len(result['issues']) == 0

        return result

    def _validate_single_trade(self, trade: TradeData, index: int) -> Dict[str, Any]:
        """Validate a single trade."""
        result = {'issues': [], 'warnings': []}

        # Check required fields for closed trades
        if trade.is_closed_trade():
            if not trade.close_price or trade.close_price <= 0:
                result['issues'].append(f"Trade {index}: Missing or invalid close price")
            if not trade.close_time:
                result['issues'].append(f"Trade {index}: Missing close time")

        # Check price validity
        if trade.price <= 0:
            result['issues'].append(f"Trade {index}: Invalid entry price: {trade.price}")

        # Check stop loss validity
        if trade.s_l < 0:
            result['issues'].append(f"Trade {index}: Invalid stop loss: {trade.s_l}")

        # Check take profit validity
        if trade.t_p < 0:
            result['issues'].append(f"Trade {index}: Invalid take profit: {trade.t_p}")

        # Check profit calculation consistency
        if trade.is_closed_trade():
            # For buy trades: profit = (close_price - entry_price) * size
            # For sell trades: profit = (entry_price - close_price) * size
            expected_profit = 0
            if trade.type and trade.type.lower() == 'buy':
                expected_profit = (trade.close_price - trade.price) * trade.size
            elif trade.type and trade.type.lower() == 'sell':
                expected_profit = (trade.price - trade.close_price) * trade.size

            if abs(trade.profit - expected_profit) > 0.01:
                result['warnings'].append(f"Trade {index}: Profit calculation may be inconsistent")

        return result

    def get_name(self) -> str:
        """Get service name."""
        return "ValidationService"

