"""
Domain models for MT4 trading data
Pydantic models for MT4 statement processing and calculations
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class TradeType(str, Enum):
    """Trade type enumeration"""
    BUY = "buy"
    SELL = "sell"
    BALANCE = "balance"


class AccountInfo(BaseModel):
    """Account information model"""
    account_number: str = ""
    account_name: str = ""
    currency: str = ""
    leverage: str = "Not specified"
    report_date: str = ""

    def is_complete(self) -> bool:
        """Check if all essential account information is present"""
        return bool(self.account_number and self.account_name and self.currency)


class FinancialSummary(BaseModel):
    """Financial summary model"""
    deposit_withdrawal: float = 0.0
    credit_facility: float = 0.0
    closed_trade_pnl: float = 0.0
    floating_pnl: float = 0.0
    margin: float = 0.0
    balance: float = 0.0
    equity: float = 0.0
    free_margin: float = 0.0

    def get_total_equity(self) -> float:
        """Calculate total equity (balance + floating P/L)"""
        return self.balance + self.floating_pnl


class TradeData(BaseModel):
    """Individual trade data model"""
    ticket: str = ""
    open_time: str = ""
    type: TradeType = TradeType.BUY
    size: float = Field(default=0.0, ge=0)
    item: str = ""
    price: float = Field(default=0.0, ge=0)
    s_l: float = Field(default=0.0, ge=0)  # Stop Loss
    t_p: float = Field(default=0.0, ge=0)  # Take Profit
    close_time: str = ""
    close_price: float = Field(default=0.0, ge=0)
    commission: float = 0.0
    taxes: float = 0.0
    swap: float = 0.0
    profit: float = 0.0

    # Additional fields for open trades
    current_price: float = Field(default=0.0, ge=0)

    @property
    def is_closed_trade(self) -> bool:
        """Check if this is a closed trade"""
        return bool(self.close_time and self.close_price)

    @property
    def is_open_trade(self) -> bool:
        """Check if this is an open trade"""
        return not self.is_closed_trade

    @property
    def is_profitable(self) -> bool:
        """Check if the trade is profitable"""
        return self.profit > 0

    def get_trade_value(self) -> float:
        """Get the total value of the trade"""
        return self.size * self.price


class PerformanceMetrics(BaseModel):
    """Performance metrics model"""
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


class TradeStatistics(BaseModel):
    """Trade statistics model"""
    total_trades: int = Field(default=0, ge=0)
    short_positions_count: int = Field(default=0, ge=0)
    short_positions_win_rate: float = Field(default=0.0, ge=0, le=100)
    long_positions_count: int = Field(default=0, ge=0)
    long_positions_win_rate: float = Field(default=0.0, ge=0, le=100)
    profit_trades_count: int = Field(default=0, ge=0)
    profit_trades_percentage: float = Field(default=0.0, ge=0, le=100)
    loss_trades_count: int = Field(default=0, ge=0)
    loss_trades_percentage: float = Field(default=0.0, ge=0, le=100)

    def get_win_rate(self) -> float:
        """Calculate overall win rate"""
        if self.total_trades > 0:
            return (self.profit_trades_count / self.total_trades) * 100
        return 0.0


class CalculatedMetrics(BaseModel):
    """Calculated additional metrics model with comprehensive trading analytics"""
    # Financial Summary (5 formulas)
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    total_net_profit: float = 0.0
    profit_factor: float = 0.0
    expected_payoff: float = 0.0

    # Risk Metrics (5 formulas)
    win_rate: float = Field(default=0.0, ge=0, le=100)
    risk_reward_ratio: float = 0.0
    kelly_percentage: float = 0.0
    maximum_drawdown_percentage: float = 0.0
    recovery_factor: float = 0.0

    # Statistical Analysis (3 formulas)
    standard_deviation: float = 0.0
    skewness: float = 0.0
    kurtosis: float = 0.0

    # Drawdown Analysis (2 formulas)
    relative_drawdown_percentage: float = 0.0
    absolute_drawdown: float = 0.0

    # Performance Metrics (2 formulas)
    expectancy: float = 0.0

    # Additional metrics
    roi_percentage: float = 0.0
    account_growth_percentage: float = 0.0
    average_trade_profit: float = 0.0
    average_trade_loss: float = 0.0
    win_loss_ratio: float = 0.0

    def get_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        score = 0.0
        score += min(self.win_rate, 50)  # Max 50 points for win rate
        score += min(self.profit_factor * 10, 20)  # Max 20 points for profit factor
        score += min(self.expectancy * 5, 30)  # Max 30 points for expectancy
        return score

    def get_risk_adjusted_score(self) -> float:
        """Calculate risk-adjusted performance score"""
        if self.recovery_factor > 0:
            return min(self.recovery_factor * 10, 100)
        return 0.0

    def get_comprehensive_rating(self) -> str:
        """Get comprehensive performance rating"""
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


class RMultipleData(BaseModel):
    """R-Multiple specific trade data"""
    ticket: str = ""
    type: TradeType = TradeType.BUY
    entry_price: float = Field(default=0.0, ge=0)
    exit_price: float = Field(default=0.0, ge=0)
    stop_loss: float = Field(default=0.0, ge=0)
    take_profit: float = Field(default=0.0, ge=0)
    actual_profit: float = 0.0
    initial_risk: float = 0.0
    r_multiple: float = 0.0
    is_profitable: bool = False
    is_valid_r_trade: bool = False
    risk_reward_ratio: float = 0.0


class OpenTradeRiskData(BaseModel):
    """Risk analysis for open trades"""
    ticket: str = ""
    type: TradeType = TradeType.BUY
    entry_price: float = Field(default=0.0, ge=0)
    current_price: float = Field(default=0.0, ge=0)
    stop_loss: float = Field(default=0.0, ge=0)
    take_profit: float = Field(default=0.0, ge=0)
    position_size: float = Field(default=0.0, ge=0)
    
    # Risk Calculations
    risk_per_share: float = 0.0
    total_risk_1r: float = 0.0
    potential_reward: float = 0.0
    current_profit_loss: float = 0.0
    
    # R-Multiple Analysis
    potential_r_multiple: float = 0.0
    current_r_multiple: float = 0.0
    risk_reward_ratio: float = 0.0
    
    # Position Analysis
    position_value: float = 0.0
    required_win_rate: float = 0.0
    
    # Risk Status
    is_valid_risk_setup: bool = False
    risk_level: str = "UNKNOWN"  # LOW, MEDIUM, HIGH, EXTREME
    
    def calculate_risk_metrics(self):
        """Calculate all risk metrics for the open trade"""
        if self.entry_price <= 0 or self.position_size <= 0:
            return
            
        # Calculate position value
        self.position_value = self.position_size * self.entry_price
        
        # Calculate risk per share and total risk
        if self.stop_loss > 0:
            if self.type == TradeType.BUY:
                if self.stop_loss < self.entry_price:
                    self.risk_per_share = self.entry_price - self.stop_loss
                    self.total_risk_1r = self.position_size * self.risk_per_share
                    self.is_valid_risk_setup = True
            elif self.type == TradeType.SELL:
                if self.stop_loss > self.entry_price:
                    self.risk_per_share = self.stop_loss - self.entry_price
                    self.total_risk_1r = self.position_size * self.risk_per_share
                    self.is_valid_risk_setup = True
        
        # Calculate potential reward if take profit is set
        if self.take_profit > 0 and self.is_valid_risk_setup:
            if self.type == TradeType.BUY and self.take_profit > self.entry_price:
                reward_per_share = self.take_profit - self.entry_price
                self.potential_reward = self.position_size * reward_per_share
            elif self.type == TradeType.SELL and self.take_profit < self.entry_price:
                reward_per_share = self.entry_price - self.take_profit
                self.potential_reward = self.position_size * reward_per_share
                
            # Calculate R-Multiple and risk/reward ratio
            if self.total_risk_1r > 0:
                self.potential_r_multiple = self.potential_reward / self.total_risk_1r
                self.risk_reward_ratio = self.potential_r_multiple
                
                # Calculate required win rate
                self.required_win_rate = (1 / (1 + self.potential_r_multiple)) * 100
        
        # Calculate current P/L and current R-Multiple
        if self.current_price > 0:
            if self.type == TradeType.BUY:
                self.current_profit_loss = self.position_size * (self.current_price - self.entry_price)
            elif self.type == TradeType.SELL:
                self.current_profit_loss = self.position_size * (self.entry_price - self.current_price)
                
            if self.total_risk_1r > 0:
                self.current_r_multiple = self.current_profit_loss / self.total_risk_1r
        
        # Determine risk level
        self._determine_risk_level()
    
    def _determine_risk_level(self):
        """Determine risk level based on position size and risk amount"""
        if not self.is_valid_risk_setup or self.position_value <= 0:
            self.risk_level = "INVALID"
            return
            
        risk_percentage = (self.total_risk_1r / self.position_value) * 100
        
        if risk_percentage <= 1.0:
            self.risk_level = "LOW"
        elif risk_percentage <= 2.0:
            self.risk_level = "MEDIUM"
        elif risk_percentage <= 5.0:
            self.risk_level = "HIGH"
        else:
            self.risk_level = "EXTREME"


class RiskCalculatorData(BaseModel):
    """Comprehensive risk calculator for trade planning"""
    # Trade Setup
    entry_price: float = Field(default=0.0, ge=0)
    stop_loss: float = Field(default=0.0, ge=0)
    take_profit: float = Field(default=0.0, ge=0)
    trade_type: TradeType = TradeType.BUY
    
    # Position Sizing Options
    account_balance: float = Field(default=0.0, ge=0)
    risk_percentage: float = Field(default=1.0, ge=0.1, le=10.0)  # 1% default, max 10%
    position_size: Optional[float] = None
    
    # Calculated Metrics
    risk_per_share: float = 0.0
    reward_per_share: float = 0.0
    total_risk: float = 0.0
    total_reward: float = 0.0
    r_multiple: float = 0.0
    risk_reward_ratio: float = 0.0
    position_value: float = 0.0
    required_win_rate: float = 0.0
    
    # Optimal Position Sizing
    optimal_position_size: float = 0.0
    max_position_size: float = 0.0
    
    # Risk Assessment
    is_valid_setup: bool = False
    risk_level: str = "UNKNOWN"
    recommendations: List[str] = Field(default_factory=list)
    
    def calculate_risk_metrics(self):
        """Calculate comprehensive risk metrics"""
        self.recommendations = []
        
        # Validate basic setup
        if self.entry_price <= 0:
            self.recommendations.append("Entry price must be greater than 0")
            return
            
        if self.stop_loss <= 0:
            self.recommendations.append("Stop loss must be set for risk management")
            return
        
        # Calculate risk per share
        if self.trade_type == TradeType.BUY:
            if self.stop_loss >= self.entry_price:
                self.recommendations.append("For BUY trades, stop loss must be below entry price")
                return
            self.risk_per_share = self.entry_price - self.stop_loss
        elif self.trade_type == TradeType.SELL:
            if self.stop_loss <= self.entry_price:
                self.recommendations.append("For SELL trades, stop loss must be above entry price")
                return
            self.risk_per_share = self.stop_loss - self.entry_price
        
        # Calculate reward per share if take profit is set
        if self.take_profit > 0:
            if self.trade_type == TradeType.BUY:
                if self.take_profit <= self.entry_price:
                    self.recommendations.append("For BUY trades, take profit must be above entry price")
                else:
                    self.reward_per_share = self.take_profit - self.entry_price
            elif self.trade_type == TradeType.SELL:
                if self.take_profit >= self.entry_price:
                    self.recommendations.append("For SELL trades, take profit must be below entry price")
                else:
                    self.reward_per_share = self.entry_price - self.take_profit
            
            # Calculate R-Multiple and ratios
            if self.reward_per_share > 0 and self.risk_per_share > 0:
                self.r_multiple = self.reward_per_share / self.risk_per_share
                self.risk_reward_ratio = self.r_multiple
                self.required_win_rate = (1 / (1 + self.r_multiple)) * 100
                
                if self.r_multiple < 1.0:
                    self.recommendations.append("Risk/Reward ratio is less than 1:1. Consider adjusting targets.")
                elif self.r_multiple >= 2.0:
                    self.recommendations.append("Excellent risk/reward ratio of 1:" + f"{self.r_multiple:.2f}")
        
        # Calculate optimal position sizing
        if self.account_balance > 0 and self.risk_per_share > 0:
            # Calculate position size based on risk percentage
            risk_amount = self.account_balance * (self.risk_percentage / 100)
            self.optimal_position_size = risk_amount / self.risk_per_share
            
            # Calculate maximum position size (10% of account)
            max_risk_amount = self.account_balance * 0.10
            self.max_position_size = max_risk_amount / self.risk_per_share
            
            # Use provided position size or optimal
            if self.position_size is None:
                self.position_size = self.optimal_position_size
        
        # Calculate totals based on position size
        if self.position_size and self.position_size > 0:
            self.total_risk = self.position_size * self.risk_per_share
            self.total_reward = self.position_size * self.reward_per_share if self.reward_per_share > 0 else 0
            self.position_value = self.position_size * self.entry_price
            
            # Determine risk level
            if self.account_balance > 0:
                risk_pct = (self.total_risk / self.account_balance) * 100
                if risk_pct <= 1.0:
                    self.risk_level = "LOW"
                elif risk_pct <= 2.0:
                    self.risk_level = "MEDIUM"
                elif risk_pct <= 5.0:
                    self.risk_level = "HIGH"
                else:
                    self.risk_level = "EXTREME"
                    self.recommendations.append(f"Risk level is EXTREME ({risk_pct:.1f}% of account)")
        
        self.is_valid_setup = len([r for r in self.recommendations if "must" in r.lower()]) == 0


class RMultipleStatistics(BaseModel):
    """Comprehensive R-Multiple statistical analysis"""
    total_valid_r_trades: int = Field(default=0, ge=0)
    r_win_rate: float = Field(default=0.0, ge=0, le=100)
    average_r_multiple: float = 0.0
    average_winning_r: float = 0.0
    average_losing_r: float = 0.0

    # R-Multiple Distribution Analysis
    r_distribution: Dict[str, int] = Field(default_factory=lambda: {
        'below_-2r': 0, '-2r_to_-1r': 0, '-1r_to_0r': 0,
        '0r_to_+1r': 0, '+1r_to_+2r': 0, 'above_+2r': 0
    })

    # R-Multiple Expectancy
    r_expectancy: float = 0.0

    # Risk-Adjusted Performance
    r_sharpe_ratio: float = 0.0
    r_sortino_ratio: float = 0.0
    max_r_drawdown: float = 0.0

    # Advanced Analytics
    r_volatility: float = 0.0
    r_skewness: float = 0.0
    r_kurtosis: float = 0.0
    r_recovery_factor: float = 0.0

    def get_r_performance_rating(self) -> str:
        """Get comprehensive R-Multiple performance rating"""
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


class MT4StatementData(BaseModel):
    """Complete MT4 statement data model"""
    account_info: AccountInfo = Field(default_factory=AccountInfo)
    financial_summary: FinancialSummary = Field(default_factory=FinancialSummary)
    performance_metrics: PerformanceMetrics = Field(default_factory=PerformanceMetrics)
    trade_statistics: TradeStatistics = Field(default_factory=TradeStatistics)
    closed_trades: List[TradeData] = Field(default_factory=list)
    open_trades: List[TradeData] = Field(default_factory=list)
    calculated_metrics: CalculatedMetrics = Field(default_factory=CalculatedMetrics)

    # R-Multiple Analysis
    r_multiple_data: List[RMultipleData] = Field(default_factory=list)
    r_multiple_statistics: RMultipleStatistics = Field(default_factory=RMultipleStatistics)
    
    # Open Trade Risk Analysis
    open_trades_risk_data: List[OpenTradeRiskData] = Field(default_factory=list)

    def get_total_trades(self) -> int:
        """Get total number of trades (closed + open)"""
        return len(self.closed_trades) + len(self.open_trades)

    def get_total_profit(self) -> float:
        """Get total profit from all trades"""
        closed_profit = sum(trade.profit for trade in self.closed_trades)
        open_profit = sum(trade.profit for trade in self.open_trades)
        return closed_profit + open_profit

    def get_profitable_trades_count(self) -> int:
        """Get count of profitable trades"""
        return sum(1 for trade in self.closed_trades if trade.is_profitable)

    def get_losing_trades_count(self) -> int:
        """Get count of losing trades"""
        return sum(1 for trade in self.closed_trades if not trade.is_profitable)
