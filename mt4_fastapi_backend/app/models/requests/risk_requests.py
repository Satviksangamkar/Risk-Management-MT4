"""
Request models for risk calculator endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional
from app.models.domain.mt4_models import TradeType


class RiskCalculatorRequest(BaseModel):
    """Request model for risk calculator"""
    entry_price: float = Field(..., gt=0, description="Entry price for the trade")
    stop_loss: float = Field(..., gt=0, description="Stop loss price")
    take_profit: Optional[float] = Field(default=None, gt=0, description="Take profit price (optional)")
    trade_type: TradeType = Field(default=TradeType.BUY, description="Trade type (buy/sell)")
    account_balance: Optional[float] = Field(default=None, gt=0, description="Account balance for position sizing")
    risk_percentage: float = Field(default=1.0, ge=0.1, le=10.0, description="Risk percentage of account (1-10%)")
    position_size: Optional[float] = Field(default=None, gt=0, description="Specific position size (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "entry_price": 1.2500,
                "stop_loss": 1.2450,
                "take_profit": 1.2600,
                "trade_type": "buy",
                "account_balance": 10000.0,
                "risk_percentage": 2.0,
                "position_size": 1.0
            }
        }
