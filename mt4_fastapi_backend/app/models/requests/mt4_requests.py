"""
Request models for MT4 API endpoints
Pydantic models for API request validation
"""

from typing import Optional
from pydantic import BaseModel, Field
from fastapi import UploadFile, File


class FileUploadRequest(BaseModel):
    """File upload request model"""
    file: UploadFile = File(...)
    calculate_r_multiple: bool = Field(default=True, description="Include R-Multiple analysis")
    include_open_trades: bool = Field(default=True, description="Include open trades in analysis")


class URLUploadRequest(BaseModel):
    """URL upload request model"""
    url: str = Field(..., description="URL to MT4 HTML statement")
    calculate_r_multiple: bool = Field(default=True, description="Include R-Multiple analysis")
    include_open_trades: bool = Field(default=True, description="Include open trades in analysis")


class AnalysisOptions(BaseModel):
    """Analysis configuration options"""
    calculate_r_multiple: bool = Field(default=True, description="Include R-Multiple analysis")
    include_open_trades: bool = Field(default=True, description="Include open trades in analysis")
    risk_free_rate: float = Field(default=0.02, ge=0, le=1, description="Risk-free rate for calculations")
    benchmark_return: Optional[float] = Field(default=None, description="Benchmark return for comparison")


class CalculationRequest(BaseModel):
    """Request model for specific calculations"""
    trades_data: list = Field(..., description="List of trade data dictionaries")
    options: AnalysisOptions = Field(default_factory=AnalysisOptions)


class BatchAnalysisRequest(BaseModel):
    """Batch analysis request model"""
    files: list = Field(..., description="List of file paths or URLs")
    options: AnalysisOptions = Field(default_factory=AnalysisOptions)
