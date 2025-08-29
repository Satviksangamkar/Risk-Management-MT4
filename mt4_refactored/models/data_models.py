"""
Data models for MT4 statement parsing.
Provides structured data representation with type hints and validation.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import math


@dataclass
class AccountInfo:
    """Account information model."""
    account_number: str = ""
    account_name: str = ""
    currency: str = ""
    leverage: str = "Not specified"
    report_date: str = ""

    def is_complete(self) -> bool:
        """Check if all essential account information is present."""
        return bool(self.account_number and self.account_name and self.currency)


@dataclass
class FinancialSummary:
    """Financial summary model."""
    deposit_withdrawal: float = 0.0
    credit_facility: float = 0.0
    closed_trade_pnl: float = 0.0
    floating_pnl: float = 0.0
    margin: float = 0.0
    balance: float = 0.0
    equity: float = 0.0
    free_margin: float = 0.0

    def get_total_equity(self) -> float:
        """Calculate total equity (balance + floating P/L)."""
        return self.balance + self.floating_pnl


@dataclass
class PerformanceMetrics:
    """Performance metrics model."""
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    total_net_profit: float = 0.0
    profit_factor: float = 0.0
    expected_payoff: float = 0.0
    absolute_drawdown: float = 0.0
    maximal_drawdown_amount: float = 0.0
    maximal_drawdown_percentage: float = 0.0
    relative_drawdown_amount: float = 0.0
    relative_drawdown_percentage: float = 0.0

    def get_profit_factor(self) -> float:
        """Calculate profit factor if not already set."""
        if self.profit_factor == 0.0 and self.gross_loss != 0.0:
            return self.gross_profit / abs(self.gross_loss)
        return self.profit_factor


@dataclass
class TradeStatistics:
    """Trade statistics model."""
    total_trades: int = 0
    short_positions_count: int = 0
    short_positions_win_rate: float = 0.0
    long_positions_count: int = 0
    long_positions_win_rate: float = 0.0
    profit_trades_count: int = 0
    profit_trades_percentage: float = 0.0
    loss_trades_count: int = 0
    loss_trades_percentage: float = 0.0

    def get_win_rate(self) -> float:
        """Calculate overall win rate."""
        if self.total_trades > 0:
            return (self.profit_trades_count / self.total_trades) * 100
        return 0.0


@dataclass
class TradeData:
    """Individual trade data model."""
    ticket: str = ""
    open_time: str = ""
    type: str = ""  # 'buy', 'sell', or 'balance'
    size: float = 0.0
    item: str = ""
    price: float = 0.0
    s_l: float = 0.0  # Stop Loss
    t_p: float = 0.0  # Take Profit
    close_time: str = ""
    close_price: float = 0.0
    commission: float = 0.0
    taxes: float = 0.0
    swap: float = 0.0
    profit: float = 0.0

    # Additional fields for open trades
    current_price: float = 0.0


    def is_closed_trade(self) -> bool:
        """Check if this is a closed trade."""
        return bool(self.close_time and self.close_price)

    def is_open_trade(self) -> bool:
        """Check if this is an open trade."""
        return not self.is_closed_trade()

    def is_profitable(self) -> bool:
        """Check if the trade is profitable."""
        return self.profit > 0

    def get_trade_value(self) -> float:
        """Get the total value of the trade."""
        return self.size * self.price


@dataclass
class LargestAverageTrades:
    """Largest and average trade data model."""
    largest_profit_trade: float = 0.0
    largest_loss_trade: float = 0.0
    average_profit_trade: float = 0.0
    average_loss_trade: float = 0.0




@dataclass
class ConsecutiveStatistics:
    """Consecutive wins/losses statistics model."""
    max_consecutive_wins_count: int = 0
    max_consecutive_wins_amount: float = 0.0
    max_consecutive_losses_count: int = 0
    max_consecutive_losses_amount: float = 0.0
    maximal_consecutive_profit_amount: float = 0.0
    maximal_consecutive_profit_count: int = 0
    maximal_consecutive_loss_amount: float = 0.0
    maximal_consecutive_loss_count: int = 0
    average_consecutive_wins: float = 0.0
    average_consecutive_losses: float = 0.0


@dataclass
class CalculatedMetrics:
    """Calculated additional metrics model with comprehensive trading analytics."""
    # Financial Summary (5 formulas)
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    total_net_profit: float = 0.0
    profit_factor: float = 0.0
    expected_payoff: float = 0.0

    # Risk Metrics (5 formulas)
    win_rate: float = 0.0
    risk_reward_ratio: float = 0.0
    kelly_percentage: float = 0.0  # Fixed Kelly Criterion
    maximum_drawdown_percentage: float = 0.0
    recovery_factor: float = 0.0

    # Statistical Analysis (2 formulas)
    skewness: float = 0.0
    kurtosis: float = 0.0

    # Drawdown Analysis (2 formulas)
    relative_drawdown_percentage: float = 0.0
    absolute_drawdown: float = 0.0

    # Performance Metrics (2 formulas)
    expectancy: float = 0.0
    standard_deviation: float = 0.0

    # Additional metrics (kept for compatibility)
    roi_percentage: float = 0.0
    account_growth_percentage: float = 0.0
    average_trade_profit: float = 0.0
    average_trade_loss: float = 0.0
    win_loss_ratio: float = 0.0

    def get_performance_score(self) -> float:
        """Calculate overall performance score (0-100) using multiple metrics."""
        score = 0.0
        score += min(self.win_rate, 50)  # Max 50 points for win rate
        score += min(self.profit_factor * 10, 20)  # Max 20 points for profit factor
        score += min(self.expectancy * 5, 30)  # Max 30 points for expectancy
        return score

    def get_risk_adjusted_score(self) -> float:
        """Calculate risk-adjusted performance score."""
        if self.recovery_factor > 0:
            return min(self.recovery_factor * 10, 100)
        return 0.0

    def get_comprehensive_rating(self) -> str:
        """Get comprehensive performance rating."""
        score = self.get_performance_score()
        recovery = self.get_risk_adjusted_score()

        if score >= 70 and recovery >= 70:
            return "EXCELLENT"
        elif score >= 60 and recovery >= 60:
            return "VERY GOOD"
        elif score >= 50 and recovery >= 50:
            return "GOOD"
        elif score >= 40 and recovery >= 40:
            return "FAIR"
        else:
            return "NEEDS IMPROVEMENT"


@dataclass
class RMultipleData:
    """R-Multiple specific trade data with calculated metrics."""
    ticket: str = ""
    type: str = ""  # 'buy' or 'sell'
    entry_price: float = 0.0
    exit_price: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    actual_profit: float = 0.0
    initial_risk: float = 0.0
    r_multiple: float = 0.0
    is_profitable: bool = False
    is_valid_r_trade: bool = False
    risk_reward_ratio: float = 0.0

    def calculate_r_multiple(self) -> float:
        """Calculate R-Multiple for this trade."""
        if not self._validate_trade_data():
            return 0.0

        # Calculate initial risk
        if self.type.lower() == 'buy':
            if self.stop_loss >= self.entry_price:
                return 0.0  # Invalid stop loss for buy trade
            self.initial_risk = self.entry_price - self.stop_loss
            self.actual_profit = self.exit_price - self.entry_price
        elif self.type.lower() == 'sell':
            if self.stop_loss <= self.entry_price:
                return 0.0  # Invalid stop loss for sell trade
            self.initial_risk = self.stop_loss - self.entry_price
            self.actual_profit = self.entry_price - self.exit_price
        else:
            return 0.0

        # Calculate R-Multiple
        if self.initial_risk > 0:
            self.r_multiple = self.actual_profit / self.initial_risk
            self.is_profitable = self.actual_profit > 0
            self.is_valid_r_trade = True

            # Calculate risk-reward ratio if take profit is set
            if self.take_profit > 0:
                if self.type.lower() == 'buy':
                    potential_reward = self.take_profit - self.entry_price
                else:  # sell
                    potential_reward = self.entry_price - self.take_profit
                self.risk_reward_ratio = potential_reward / self.initial_risk if self.initial_risk > 0 else 0.0

        return self.r_multiple

    def _validate_trade_data(self) -> bool:
        """Validate that trade has required data for R-Multiple calculation."""
        if not all([self.entry_price > 0, self.exit_price > 0, self.stop_loss > 0]):
            return False

        # Additional validations
        if self.type.lower() not in ['buy', 'sell']:
            return False

        return True


@dataclass
class RMultipleStatistics:
    """Comprehensive R-Multiple statistical analysis."""
    # Basic R-Multiple Statistics
    total_valid_r_trades: int = 0
    r_win_rate: float = 0.0
    average_r_multiple: float = 0.0
    average_winning_r: float = 0.0
    average_losing_r: float = 0.0

    # R-Multiple Distribution Analysis
    r_distribution: Dict[str, int] = field(default_factory=lambda: {
        'below_-2r': 0, '-2r_to_-1r': 0, '-1r_to_0r': 0,
        '0r_to_+1r': 0, '+1r_to_+2r': 0, 'above_+2r': 0
    })

    # R-Multiple Expectancy
    r_expectancy: float = 0.0

    # Risk-Adjusted Performance
    r_sharpe_ratio: float = 0.0
    r_sortino_ratio: float = 0.0
    max_r_drawdown: float = 0.0

    # Consecutive R-Multiple Analysis
    max_consecutive_r_wins: int = 0
    max_consecutive_r_losses: int = 0
    average_r_win_streak: float = 0.0
    average_r_loss_streak: float = 0.0

    # Advanced Analytics
    r_volatility: float = 0.0
    r_skewness: float = 0.0
    r_kurtosis: float = 0.0
    r_recovery_factor: float = 0.0

    def get_r_performance_rating(self) -> str:
        """Get comprehensive R-Multiple performance rating."""
        score = 0.0

        # R Expectancy (40% weight)
        if self.r_expectancy > 0.5:
            score += 40
        elif self.r_expectancy > 0.2:
            score += 25
        elif self.r_expectancy > 0:
            score += 10

        # R Win Rate (30% weight)
        if self.r_win_rate >= 60:
            score += 30
        elif self.r_win_rate >= 50:
            score += 20
        elif self.r_win_rate >= 40:
            score += 10

        # Risk Management (20% weight)
        if self.average_losing_r > -1.0:
            score += 20
        elif self.average_losing_r > -2.0:
            score += 10

        # Consistency (10% weight)
        if self.r_volatility < 2.0:
            score += 10

        if score >= 80:
            return "EXCELLENT"
        elif score >= 65:
            return "VERY GOOD"
        elif score >= 50:
            return "GOOD"
        elif score >= 35:
            return "FAIR"
        else:
            return "NEEDS IMPROVEMENT"


@dataclass
class MT4StatementData:
    """Complete MT4 statement data model."""
    account_info: AccountInfo = field(default_factory=AccountInfo)
    financial_summary: FinancialSummary = field(default_factory=FinancialSummary)
    performance_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    trade_statistics: TradeStatistics = field(default_factory=TradeStatistics)
    largest_average_trades: LargestAverageTrades = field(default_factory=LargestAverageTrades)
    consecutive_statistics: ConsecutiveStatistics = field(default_factory=ConsecutiveStatistics)
    closed_trades: List[TradeData] = field(default_factory=list)
    open_trades: List[TradeData] = field(default_factory=list)
    calculated_metrics: CalculatedMetrics = field(default_factory=CalculatedMetrics)

    # R-Multiple Analysis
    r_multiple_data: List[RMultipleData] = field(default_factory=list)
    r_multiple_statistics: RMultipleStatistics = field(default_factory=RMultipleStatistics)

    def get_total_trades(self) -> int:
        """Get total number of trades (closed + open)."""
        return len(self.closed_trades) + len(self.open_trades)

    def get_total_profit(self) -> float:
        """Get total profit from all trades."""
        closed_profit = sum(trade.profit for trade in self.closed_trades)
        open_profit = sum(trade.profit for trade in self.open_trades)
        return closed_profit + open_profit

    def get_profitable_trades_count(self) -> int:
        """Get count of profitable trades."""
        return sum(1 for trade in self.closed_trades if trade.is_profitable())

    def get_losing_trades_count(self) -> int:
        """Get count of losing trades."""
        return sum(1 for trade in self.closed_trades if not trade.is_profitable())

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary for serialization."""
        return {
            'account_info': self.account_info.__dict__,
            'financial_summary': self.financial_summary.__dict__,
            'performance_metrics': self.performance_metrics.__dict__,
            'trade_statistics': self.trade_statistics.__dict__,
            'largest_average_trades': self.largest_average_trades.__dict__,
            'consecutive_statistics': self.consecutive_statistics.__dict__,
            'closed_trades': [trade.__dict__ for trade in self.closed_trades],
            'open_trades': [trade.__dict__ for trade in self.open_trades],
            'calculated_metrics': self.calculated_metrics.__dict__,
            'r_multiple_data': [r_trade.__dict__ for r_trade in self.r_multiple_data],
            'r_multiple_statistics': self.r_multiple_statistics.__dict__,
            'summary': {
                'total_trades': self.get_total_trades(),
                'total_profit': self.get_total_profit(),
                'profitable_trades': self.get_profitable_trades_count(),
                'losing_trades': self.get_losing_trades_count(),
                'valid_r_trades': self.r_multiple_statistics.total_valid_r_trades,
                'r_performance_rating': self.r_multiple_statistics.get_r_performance_rating()
            }
        }
