"""
MT4 Analysis API Endpoints
RESTful endpoints for MT4 statement analysis
"""

import time
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import JSONResponse

from app.api.dependencies.services import get_mt4_service, validate_file_upload, validate_content_type
from app.models.requests.mt4_requests import AnalysisOptions
from app.models.requests.risk_requests import RiskCalculatorRequest
from app.models.responses.mt4_responses import (
    AnalysisResponse,
    ErrorResponse,
    FileUploadResponse,
    HealthResponse
)
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/analyze/file",
    response_model=AnalysisResponse,
    summary="Analyze MT4 Statement from File Upload",
    description="""
    Upload and analyze an MT4 HTML statement file.

    **Features:**
    - Comprehensive trading metrics calculation (45+ metrics)
    - R-Multiple analysis (optional)
    - Risk assessment and performance ratings
    - Statistical analysis and drawdown calculations

    **Supported file types:** .htm, .html
    **Maximum file size:** 50MB
    """,
    responses={
        200: {"description": "Analysis completed successfully"},
        400: {"description": "Invalid file or request parameters"},
        413: {"description": "File too large"},
        500: {"description": "Internal server error"}
    }
)
async def analyze_mt4_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    calculate_r_multiple: bool = Query(True, description="Include R-Multiple analysis"),
    include_open_trades: bool = Query(True, description="Include open trades in analysis"),
    mt4_service: Any = get_mt4_service()
) -> AnalysisResponse:
    """Analyze MT4 statement from uploaded file"""

    start_time = time.time()

    try:
        logger.info(f"Received file upload: {file.filename}")

        # Validate file
        validate_content_type(file.content_type)
        file_content = await file.read()
        validate_file_upload(len(file_content))

        # Save temporary file (Windows compatible)
        import tempfile
        import os
        temp_dir = tempfile.gettempdir()
        temp_file_path = Path(temp_dir) / file.filename
        temp_file_path.parent.mkdir(exist_ok=True)

        with open(temp_file_path, 'wb') as f:
            f.write(file_content)

        # Process the file
        success, response = mt4_service.process_statement_file(
            temp_file_path,
            calculate_r_multiple=calculate_r_multiple,
            include_open_trades=include_open_trades
        )

        # Clean up temporary file
        background_tasks.add_task(temp_file_path.unlink, missing_ok=True)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.message
            )

        logger.info(f"File analysis completed in {time.time() - start_time:.2f}s")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File analysis failed"
        )


@router.post(
    "/analyze/content",
    response_model=AnalysisResponse,
    summary="Analyze MT4 Statement from HTML Content",
    description="""
    Analyze MT4 statement from raw HTML content string.

    **Use cases:**
    - Direct HTML content processing
    - API integrations
    - Programmatic analysis

    **Content requirements:**
    - Valid HTML format
    - Contains MT4 statement tables
    - UTF-8 encoded
    """,
    responses={
        200: {"description": "Analysis completed successfully"},
        400: {"description": "Invalid HTML content"},
        500: {"description": "Internal server error"}
    }
)
async def analyze_mt4_content(
    html_content: str,
    calculate_r_multiple: bool = Query(True, description="Include R-Multiple analysis"),
    include_open_trades: bool = Query(True, description="Include open trades in analysis"),
    mt4_service: Any = get_mt4_service()
) -> AnalysisResponse:
    """Analyze MT4 statement from HTML content"""

    start_time = time.time()

    try:
        logger.info(f"Received HTML content analysis request ({len(html_content)} chars)")

        if not html_content or len(html_content.strip()) < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid HTML content: too short or empty"
            )

        # Process the content
        success, response = mt4_service.process_statement_content(
            html_content,
            calculate_r_multiple=calculate_r_multiple,
            include_open_trades=include_open_trades
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.message
            )

        logger.info(f"Content analysis completed in {time.time() - start_time:.2f}s")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content analysis failed"
        )


@router.post(
    "/analyze/path",
    response_model=AnalysisResponse,
    summary="Analyze MT4 Statement from File Path",
    description="""
    Analyze MT4 statement from a file path on the server.

    **Security Note:** This endpoint is intended for server-side processing.
    Direct file path access should be restricted in production.

    **Requirements:**
    - File must exist on server
    - Valid MT4 HTML format
    - Accessible by the application
    """,
    responses={
        200: {"description": "Analysis completed successfully"},
        404: {"description": "File not found"},
        500: {"description": "Internal server error"}
    }
)
async def analyze_mt4_path(
    file_path: str = Query(..., description="Path to MT4 HTML file on server"),
    calculate_r_multiple: bool = Query(True, description="Include R-Multiple analysis"),
    include_open_trades: bool = Query(True, description="Include open trades in analysis"),
    mt4_service: Any = get_mt4_service()
) -> AnalysisResponse:
    """Analyze MT4 statement from file path"""

    start_time = time.time()

    try:
        logger.info(f"Received file path analysis request: {file_path}")

        file_path_obj = Path(file_path)

        # Process the file
        success, response = mt4_service.process_statement_file(
            file_path_obj,
            calculate_r_multiple=calculate_r_multiple,
            include_open_trades=include_open_trades
        )

        if not success:
            if "not found" in response.message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response.message
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response.message
                )

        logger.info(f"Path analysis completed in {time.time() - start_time:.2f}s")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Path analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File path analysis failed"
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    description="""
    Check the health status of the MT4 analysis service.

    **Returns:**
    - Service status
    - Component health
    - Timestamp
    """,
    responses={
        200: {"description": "Service is healthy"},
        500: {"description": "Service health check failed"}
    }
)
async def health_check(mt4_service: Any = get_mt4_service()) -> HealthResponse:
    """Get service health status"""

    try:
        health_data = mt4_service.get_health_status()

        return HealthResponse(
            status=health_data["status"],
            version=settings.VERSION,
            timestamp=health_data["timestamp"]
        )

    except Exception as e:
        logger.error(f"Health check error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )


@router.get(
    "/metrics",
    summary="Get Service Metrics",
    description="""
    Get current service performance metrics and statistics.

    **Returns:**
    - Processing statistics
    - System information
    - Cache status (if applicable)
    """,
    responses={
        200: {"description": "Metrics retrieved successfully"},
        500: {"description": "Metrics retrieval failed"}
    }
)
async def get_service_metrics():
    """Get service performance metrics"""

    try:
        # This would typically return actual metrics from a metrics collector
        metrics = {
            "service_name": "MT4 Analysis Service",
            "version": settings.VERSION,
            "uptime": "N/A",  # Would be calculated from service start time
            "total_requests": 0,  # Would be tracked
            "active_connections": 0,  # Would be tracked
            "memory_usage": "N/A",  # Would be measured
            "cpu_usage": "N/A"  # Would be measured
        }

        return JSONResponse(
            content=metrics,
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error(f"Metrics retrieval error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Metrics retrieval failed"
        )


@router.post(
    "/risk-calculator",
    summary="Risk Calculator for Trade Planning",
    description="""
    Calculate comprehensive risk metrics for trade planning.
    
    **Features:**
    - Risk per share calculation
    - R-Multiple analysis
    - Position sizing recommendations
    - Risk/reward ratio analysis
    - Required win rate calculation
    - Risk level assessment
    
    **Use this for:**
    - Planning new trades
    - Position sizing optimization
    - Risk management analysis
    """,
    responses={
        200: {"description": "Risk calculation completed successfully"},
        400: {"description": "Invalid trade parameters"},
        500: {"description": "Internal server error"}
    }
)
async def calculate_trade_risk(
    request: RiskCalculatorRequest,
    mt4_service: Any = get_mt4_service()
) -> Dict[str, Any]:
    """Calculate comprehensive risk metrics for trade planning"""
    
    try:
        logger.info(f"Risk calculation request: {request.trade_type} @ {request.entry_price}")
        
        # Use the calculator service to compute risk metrics
        risk_calc = mt4_service.calculator.calculate_risk_calculator(
            entry_price=request.entry_price,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit,
            trade_type=request.trade_type,
            account_balance=request.account_balance or 0.0,
            risk_percentage=request.risk_percentage,
            position_size=request.position_size
        )
        
        return {
            "success": True,
            "message": "Risk calculation completed successfully",
            "data": {
                "trade_setup": {
                    "entry_price": risk_calc.entry_price,
                    "stop_loss": risk_calc.stop_loss,
                    "take_profit": risk_calc.take_profit,
                    "trade_type": risk_calc.trade_type,
                    "is_valid_setup": risk_calc.is_valid_setup
                },
                "risk_metrics": {
                    "risk_per_share": risk_calc.risk_per_share,
                    "reward_per_share": risk_calc.reward_per_share,
                    "total_risk": risk_calc.total_risk,
                    "total_reward": risk_calc.total_reward,
                    "r_multiple": risk_calc.r_multiple,
                    "risk_reward_ratio": risk_calc.risk_reward_ratio,
                    "required_win_rate": risk_calc.required_win_rate
                },
                "position_analysis": {
                    "position_size": risk_calc.position_size,
                    "optimal_position_size": risk_calc.optimal_position_size,
                    "max_position_size": risk_calc.max_position_size,
                    "position_value": risk_calc.position_value,
                    "risk_level": risk_calc.risk_level
                },
                "account_analysis": {
                    "account_balance": risk_calc.account_balance,
                    "risk_percentage": risk_calc.risk_percentage,
                    "recommendations": risk_calc.recommendations
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Risk calculation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Risk calculation failed"
        )
