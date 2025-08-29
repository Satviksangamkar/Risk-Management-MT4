"""
Response models for MT4 API endpoints
Pydantic models for API response formatting
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.domain.mt4_models import (
    MT4StatementData,
    AccountInfo,
    FinancialSummary,
    TradeData,
    CalculatedMetrics,
    RMultipleStatistics
)


class APIResponse(BaseModel):
    """Base API response model"""
    success: bool = Field(default=True, description="Operation success status")
    message: str = Field(default="", description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    processing_time: Optional[float] = Field(default=None, description="Processing time in seconds")


class AnalysisResponse(APIResponse):
    """MT4 statement analysis response"""
    data: MT4StatementData
    total_trades: int = Field(default=0, description="Total number of trades processed")
    processing_time: float = Field(..., description="Time taken for analysis in seconds")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MetricsResponse(APIResponse):
    """Calculated metrics response"""
    metrics: CalculatedMetrics
    trade_count: int = Field(default=0, description="Number of trades used in calculations")


class RMultipleResponse(APIResponse):
    """R-Multiple analysis response"""
    r_statistics: RMultipleStatistics
    r_trades: List[Dict[str, Any]] = Field(default_factory=list, description="R-Multiple trade data")


class SummaryResponse(APIResponse):
    """Summary response with key metrics"""
    account_info: AccountInfo
    financial_summary: FinancialSummary
    key_metrics: Dict[str, float] = Field(default_factory=dict, description="Key performance metrics")
    ratings: Dict[str, str] = Field(default_factory=dict, description="Performance ratings")
    total_trades: int = Field(default=0, description="Total number of trades")


class ErrorResponse(APIResponse):
    """Error response model"""
    success: bool = Field(default=False, description="Always false for errors")
    error_code: str = Field(default="", description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy", description="Service health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime: Optional[str] = Field(default=None, description="Service uptime")


class FileUploadResponse(APIResponse):
    """File upload response"""
    file_id: str = Field(default="", description="Uploaded file identifier")
    file_name: str = Field(default="", description="Original file name")
    file_size: int = Field(default=0, description="File size in bytes")
    content_type: str = Field(default="", description="File content type")
