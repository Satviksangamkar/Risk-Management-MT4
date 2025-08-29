"""Data models for MT4 trading data structures."""

from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field


@dataclass
class HeaderInformation:
    """Header information from MT4 report."""
    account_number: Optional[str] = None
    account_name: Optional[str] = None
    currency: Optional[str] = None
    leverage: Optional[str] = None
    report_date: Optional[str] = None
    company: Optional[str] = None


@dataclass
class TradeData:
    """Individual trade data."""
    ticket: Optional[str] = None
    open_time: Optional[str] = None
    type: Optional[str] = None
    size: Optional[float] = None
    item: Optional[str] = None
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    close_time: Optional[str] = None
    close_price: Optional[float] = None
    commission: Optional[float] = None
    taxes: Optional[float] = None
    swap: Optional[float] = None
    profit: Optional[float] = None
    current_price: Optional[float] = None
    market_price: Optional[float] = None


@dataclass
class ClosedTransactions:
    """Closed transactions section."""
    total_closed_pl: float = 0.0
    trades: List[Dict] = field(default_factory=list)


@dataclass
class OpenTrades:
    """Open trades section."""
    floating_pl: float = 0.0
    trades: List[Dict] = field(default_factory=list)


@dataclass
class WorkingOrders:
    """Working orders section."""
    orders: List[Dict] = field(default_factory=list)
    status: str = "No transactions"


@dataclass
class SummarySection:
    """Summary section data."""
    deposit_withdrawal: Optional[float] = None
    credit_facility: Optional[float] = None
    closed_trade_pnl: Optional[float] = None
    floating_pnl: Optional[float] = None
    margin: Optional[float] = None
    balance: Optional[float] = None
    equity: Optional[float] = None
    free_margin: Optional[float] = None


@dataclass
class PerformanceDetails:
    """Performance details section."""
    gross_profit: Optional[float] = None
    gross_loss: Optional[float] = None
    total_net_profit: Optional[float] = None
    profit_factor: Optional[float] = None
    expected_payoff: Optional[float] = None
    absolute_drawdown: Optional[float] = None
    maximal_drawdown_amount: Optional[float] = None
    relative_drawdown_percentage: Optional[float] = None
    total_trades: Optional[int] = None
    largest_profit_trade: Optional[float] = None
    largest_loss_trade: Optional[float] = None
    average_profit_trade: Optional[float] = None
    average_loss_trade: Optional[float] = None


@dataclass
class CompleteAnalysis:
    """Complete MT4 analysis data structure."""
    header_information: HeaderInformation = field(default_factory=HeaderInformation)
    closed_transactions: ClosedTransactions = field(default_factory=ClosedTransactions)
    open_trades: OpenTrades = field(default_factory=OpenTrades)
    working_orders: WorkingOrders = field(default_factory=WorkingOrders)
    summary_section: SummarySection = field(default_factory=SummarySection)
    performance_details: PerformanceDetails = field(default_factory=PerformanceDetails)
