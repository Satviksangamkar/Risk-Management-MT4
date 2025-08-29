"""
MT4 Calculator Service
Comprehensive trading calculations and analytics service
"""

import math
import statistics
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from datetime import datetime

from app.models.domain.mt4_models import (
    TradeData, MT4StatementData, CalculatedMetrics,
    RMultipleData, RMultipleStatistics, TradeType
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class MT4CalculatorService:
    """Service for MT4 trading calculations and analytics"""

    def __init__(self):
        self.risk_free_rate = 0.02  # 2% annual risk-free rate

    def calculate_all_metrics(
        self,
        trades: List[TradeData],
        include_r_multiple: bool = True
    ) -> CalculatedMetrics:
        """
        Calculate all trading metrics in single pass
        Returns comprehensive metrics analysis
        """
        if not trades:
            return CalculatedMetrics()

        logger.info(f"Calculating metrics for {len(trades)} trades")

        # Separate closed and open trades
        closed_trades = [t for t in trades if t.is_closed_trade]
        open_trades = [t for t in trades if t.is_open_trade]

        # Basic financial calculations
        gross_profit = sum(t.profit for t in closed_trades if t.profit > 0)
        gross_loss = abs(sum(t.profit for t in closed_trades if t.profit < 0))
        total_net_profit = sum(t.profit for t in closed_trades)

        # Profit factor
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        # Expected payoff
        expected_payoff = total_net_profit / len(closed_trades) if closed_trades else 0

        # Win rate
        profitable_trades = len([t for t in closed_trades if t.profit > 0])
        win_rate = (profitable_trades / len(closed_trades)) * 100 if closed_trades else 0

        # Risk-reward ratio
        avg_win = gross_profit / profitable_trades if profitable_trades > 0 else 0
        losing_trades = len([t for t in closed_trades if t.profit < 0])
        avg_loss = gross_loss / losing_trades if losing_trades > 0 else 0
        risk_reward_ratio = abs(avg_win / avg_loss) if avg_loss > 0 else float('inf')

        # Kelly Criterion
        kelly_percentage = self._calculate_kelly_criterion(win_rate / 100, risk_reward_ratio)

        # Statistical analysis
        profits = [t.profit for t in closed_trades]
        standard_deviation = statistics.stdev(profits) if len(profits) > 1 else 0
        skewness = self._calculate_skewness(profits)
        kurtosis = self._calculate_kurtosis(profits)

        # Drawdown analysis
        max_drawdown_pct, recovery_factor = self._calculate_drawdown_metrics(closed_trades)

        # Expectancy
        expectancy = (win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * avg_loss)

        return CalculatedMetrics(
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            total_net_profit=total_net_profit,
            profit_factor=profit_factor,
            expected_payoff=expected_payoff,
            win_rate=win_rate,
            risk_reward_ratio=risk_reward_ratio,
            kelly_percentage=kelly_percentage,
            maximum_drawdown_percentage=max_drawdown_pct,
            recovery_factor=recovery_factor,
            standard_deviation=standard_deviation,
            skewness=skewness,
            kurtosis=kurtosis,
            expectancy=expectancy,
            average_trade_profit=avg_win,
            average_trade_loss=avg_loss,
            win_loss_ratio=avg_win / avg_loss if avg_loss > 0 else float('inf')
        )

    def calculate_r_multiple_analysis(
        self,
        trades: List[TradeData]
    ) -> Tuple[List[RMultipleData], RMultipleStatistics]:
        """
        Calculate comprehensive R-Multiple analysis
        Returns R-Multiple data and statistics
        """
        closed_trades = [t for t in trades if t.is_closed_trade]
        r_trades = []
        valid_r_trades = []

        for trade in closed_trades:
            r_trade = self._calculate_single_r_multiple(trade)
            r_trades.append(r_trade)
            if r_trade.is_valid_r_trade:
                valid_r_trades.append(r_trade)

        # Calculate R-Multiple statistics
        statistics_obj = self._calculate_r_statistics(valid_r_trades)

        return r_trades, statistics_obj

    def _calculate_single_r_multiple(self, trade: TradeData) -> RMultipleData:
        """Calculate R-Multiple for a single trade"""
        r_trade = RMultipleData(
            ticket=trade.ticket,
            type=trade.type,
            entry_price=trade.price,
            exit_price=trade.close_price,
            stop_loss=trade.s_l,
            take_profit=trade.t_p,
            actual_profit=trade.profit
        )

        # Calculate initial risk and R-Multiple
        if trade.type == TradeType.BUY:
            if trade.s_l >= trade.price:
                return r_trade  # Invalid stop loss
            initial_risk = trade.price - trade.s_l
            actual_profit = trade.close_price - trade.price
        elif trade.type == TradeType.SELL:
            if trade.s_l <= trade.price:
                return r_trade  # Invalid stop loss
            initial_risk = trade.s_l - trade.price
            actual_profit = trade.price - trade.close_price
        else:
            return r_trade

        r_trade.initial_risk = initial_risk
        r_trade.actual_profit = actual_profit
        r_trade.r_multiple = actual_profit / initial_risk if initial_risk > 0 else 0
        r_trade.is_profitable = actual_profit > 0
        r_trade.is_valid_r_trade = True

        # Calculate risk-reward ratio
        if trade.t_p > 0:
            if trade.type == TradeType.BUY:
                potential_reward = trade.t_p - trade.price
            else:  # sell
                potential_reward = trade.price - trade.t_p
            r_trade.risk_reward_ratio = potential_reward / initial_risk if initial_risk > 0 else 0

        return r_trade

    def _calculate_r_statistics(self, r_trades: List[RMultipleData]) -> RMultipleStatistics:
        """Calculate comprehensive R-Multiple statistics"""
        if not r_trades:
            return RMultipleStatistics()

        # Basic R-Multiple stats
        r_multiples = [t.r_multiple for t in r_trades]
        winning_r = [t.r_multiple for t in r_trades if t.is_profitable]
        losing_r = [t.r_multiple for t in r_trades if not t.is_profitable]

        stats = RMultipleStatistics(
            total_valid_r_trades=len(r_trades),
            r_win_rate=len(winning_r) / len(r_trades) * 100 if r_trades else 0,
            average_r_multiple=statistics.mean(r_multiples) if r_multiples else 0,
            average_winning_r=statistics.mean(winning_r) if winning_r else 0,
            average_losing_r=statistics.mean(losing_r) if losing_r else 0
        )

        # R-Multiple distribution
        stats.r_distribution = self._calculate_r_distribution(r_multiples)

        # R-Multiple expectancy
        win_prob = stats.r_win_rate / 100
        loss_prob = 1 - win_prob
        stats.r_expectancy = (win_prob * stats.average_winning_r) - (loss_prob * abs(stats.average_losing_r))

        # R-Multiple volatility
        stats.r_volatility = statistics.stdev(r_multiples) if len(r_multiples) > 1 else 0

        # R-Multiple skewness and kurtosis
        stats.r_skewness = self._calculate_skewness(r_multiples)
        stats.r_kurtosis = self._calculate_kurtosis(r_multiples)

        return stats

    def _calculate_r_distribution(self, r_multiples: List[float]) -> Dict[str, int]:
        """Calculate R-Multiple distribution"""
        distribution = {
            'below_-2r': 0, '-2r_to_-1r': 0, '-1r_to_0r': 0,
            '0r_to_+1r': 0, '+1r_to_+2r': 0, 'above_+2r': 0
        }

        for r in r_multiples:
            if r < -2:
                distribution['below_-2r'] += 1
            elif -2 <= r < -1:
                distribution['-2r_to_-1r'] += 1
            elif -1 <= r < 0:
                distribution['-1r_to_0r'] += 1
            elif 0 <= r < 1:
                distribution['0r_to_+1r'] += 1
            elif 1 <= r < 2:
                distribution['+1r_to_+2r'] += 1
            else:
                distribution['above_+2r'] += 1

        return distribution

    def _calculate_kelly_criterion(self, win_rate: float, risk_reward_ratio: float) -> float:
        """Calculate Kelly Criterion percentage"""
        if risk_reward_ratio <= 0:
            return 0

        # Kelly formula: (bp - q) / b
        # where b = risk-reward ratio, p = win rate, q = loss rate
        b = risk_reward_ratio
        p = win_rate
        q = 1 - p

        kelly = (b * p - q) / b if b > 0 else 0
        return max(0, min(kelly * 100, 100))  # Convert to percentage and cap at 100%

    def _calculate_drawdown_metrics(self, trades: List[TradeData]) -> Tuple[float, float]:
        """Calculate maximum drawdown and recovery factor"""
        if not trades:
            return 0.0, 0.0

        # Sort trades by close time
        sorted_trades = sorted(trades, key=lambda x: x.close_time)

        # Calculate cumulative returns
        cumulative = 0
        peak = 0
        max_drawdown = 0
        max_drawdown_pct = 0

        for trade in sorted_trades:
            cumulative += trade.profit
            if cumulative > peak:
                peak = cumulative
            drawdown = peak - cumulative
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                max_drawdown_pct = (drawdown / peak) * 100 if peak > 0 else 0

        # Calculate recovery factor
        total_profit = sum(t.profit for t in trades if t.profit > 0)
        recovery_factor = total_profit / max_drawdown if max_drawdown > 0 else float('inf')

        return max_drawdown_pct, recovery_factor

    def _calculate_skewness(self, data: List[float]) -> float:
        """Calculate skewness of data"""
        if len(data) < 3:
            return 0.0

        mean = statistics.mean(data)
        std_dev = statistics.stdev(data)
        if std_dev == 0:
            return 0.0

        n = len(data)
        skewness = (n / ((n - 1) * (n - 2))) * sum(((x - mean) / std_dev) ** 3 for x in data)
        return skewness

    def _calculate_kurtosis(self, data: List[float]) -> float:
        """Calculate kurtosis of data"""
        if len(data) < 4:
            return 0.0

        mean = statistics.mean(data)
        std_dev = statistics.stdev(data)
        if std_dev == 0:
            return 0.0

        n = len(data)
        kurtosis = (n * (n + 1) / ((n - 1) * (n - 2) * (n - 3))) * sum(((x - mean) / std_dev) ** 4 for x in data)
        kurtosis -= (3 * (n - 1) ** 2) / ((n - 2) * (n - 3))
        return kurtosis
