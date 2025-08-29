#!/usr/bin/env python3
"""
MT4 FastAPI Backend - Main Application Entry Point
Production-ready FastAPI application for MT4 statement analysis and calculations
"""

import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.errors import add_exception_handlers
from app.utils.file_utils import ensure_upload_directory
from app.core.logging import get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting MT4 FastAPI Backend")

    # Ensure upload directory exists
    upload_dir = ensure_upload_directory()
    logger.info(f"Upload directory ready: {upload_dir}")

    logger.info("Application startup complete")
    yield

    # Shutdown
    logger.info("Shutting down MT4 FastAPI Backend")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add exception handlers
add_exception_handlers(app)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add trusted host middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files (frontend)
frontend_path = Path(__file__).parent.parent / "mt4_frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    logger.info(f"Mounted frontend static files from: {frontend_path}")

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - serve frontend"""
    from fastapi.responses import FileResponse
    frontend_path = Path(__file__).parent.parent / "mt4_frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(str(frontend_path))
    else:
        return RedirectResponse(url="/docs")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "service": "MT4 Analysis Backend",
        "environment": "development" if settings.DEBUG else "production"
    }


@app.get("/status", tags=["Health"])
async def system_status():
    """Detailed system status"""
    import psutil
    import os
    from datetime import datetime

    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.VERSION,
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "percent": disk.percent
                }
            },
            "configuration": {
                "debug": settings.DEBUG,
                "max_upload_size": settings.MAX_UPLOAD_SIZE,
                "max_trades_per_request": settings.MAX_TRADES_PER_REQUEST
            }
        }
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# Simple file analysis endpoint (backup implementation)
@app.post("/api/v1/mt4/analyze/file-simple", tags=["MT4 Analysis"])
async def analyze_file_simple(file: UploadFile = File(...)):
    """Simplified file analysis that works with basic parsing"""
    try:
        from fastapi import HTTPException
        from bs4 import BeautifulSoup
        import re
        
        # Read file content
        content = await file.read()
        html_content = content.decode('utf-8', errors='ignore')
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract basic account info
        account_info = {}
        
        # Try to find account number and details
        for cell in soup.find_all(['td', 'th']):
            text = cell.get_text(strip=True)
            if 'Account:' in text:
                account_info['account_number'] = text.replace('Account:', '').strip()
            elif 'Name:' in text:
                account_info['account_name'] = text.replace('Name:', '').strip()
            elif 'Currency:' in text:
                account_info['currency'] = text.replace('Currency:', '').strip()
            elif 'Leverage:' in text:
                account_info['leverage'] = text.replace('Leverage:', '').strip()
        
        # Extract trades from tables
        trades = []
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 1:  # Skip empty tables
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 10:  # Minimum columns for trade data
                        try:
                            # Extract numeric values
                            profit_text = cells[-1].get_text(strip=True) if len(cells) > 13 else '0'
                            profit = float(re.sub(r'[^\d.-]', '', profit_text)) if profit_text else 0
                            
                            size_text = cells[3].get_text(strip=True) if len(cells) > 3 else '0'
                            size = float(re.sub(r'[^\d.-]', '', size_text)) if size_text else 0
                            
                            if profit != 0 or size != 0:  # Valid trade
                                trades.append({
                                    'ticket': cells[0].get_text(strip=True) if cells[0] else '',
                                    'type': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                                    'size': size,
                                    'profit': profit
                                })
                        except (ValueError, IndexError):
                            continue
        
        # Calculate detailed R-Multiple for each trade
        detailed_trades = []
        r_multiple_data = []
        
        for i, trade in enumerate(trades):
            # Extract trade details
            ticket = trade.get('ticket', f'Trade_{i+1}')
            trade_type = trade.get('type', '').lower()
            size = trade.get('size', 0)
            profit = trade.get('profit', 0)
            
            # Try to extract prices from cells for R-Multiple calculation
            entry_price = 0
            stop_loss = 0
            take_profit = 0
            
            # Find the original row for this trade to extract prices
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 10 and cells[0].get_text(strip=True) == ticket:
                        try:
                            entry_price = float(re.sub(r'[^\d.-]', '', cells[5].get_text(strip=True))) if len(cells) > 5 else 0
                            stop_loss = float(re.sub(r'[^\d.-]', '', cells[6].get_text(strip=True))) if len(cells) > 6 else 0
                            take_profit = float(re.sub(r'[^\d.-]', '', cells[7].get_text(strip=True))) if len(cells) > 7 else 0
                        except (ValueError, IndexError):
                            pass
                        break
            
            # Calculate R-Multiple metrics for this trade
            risk_per_share = 0
            reward_per_share = 0
            r_multiple = 0
            risk_amount = 0
            is_valid_r_setup = False
            
            if entry_price > 0 and stop_loss > 0 and size > 0:
                if trade_type == 'buy' and stop_loss < entry_price:
                    risk_per_share = entry_price - stop_loss
                    risk_amount = size * risk_per_share
                    is_valid_r_setup = True
                elif trade_type == 'sell' and stop_loss > entry_price:
                    risk_per_share = stop_loss - entry_price
                    risk_amount = size * risk_per_share
                    is_valid_r_setup = True
                
                # Calculate actual R-Multiple based on profit
                if risk_amount > 0:
                    r_multiple = profit / risk_amount
                
                # Calculate theoretical reward if take profit was set
                if take_profit > 0:
                    if trade_type == 'buy' and take_profit > entry_price:
                        reward_per_share = take_profit - entry_price
                    elif trade_type == 'sell' and take_profit < entry_price:
                        reward_per_share = entry_price - take_profit
            
            # Enhanced trade data with R-Multiple details
            enhanced_trade = {
                'ticket': ticket,
                'type': trade_type,
                'size': size,
                'profit': profit,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'risk_per_share': risk_per_share,
                'reward_per_share': reward_per_share,
                'risk_amount': risk_amount,
                'r_multiple': r_multiple,
                'is_valid_r_setup': is_valid_r_setup,
                'potential_reward': size * reward_per_share if reward_per_share > 0 else 0,
                'theoretical_r_multiple': reward_per_share / risk_per_share if risk_per_share > 0 else 0
            }
            
            detailed_trades.append(enhanced_trade)
            
            # Add to R-Multiple analysis if valid
            if is_valid_r_setup:
                r_multiple_data.append({
                    'ticket': ticket,
                    'r_multiple': r_multiple,
                    'trade_type': trade_type,
                    'risk_amount': risk_amount,
                    'profit': profit,
                    'is_winner': profit > 0
                })
        
        # Calculate comprehensive R-Multiple statistics
        valid_r_trades = [r for r in r_multiple_data if r['r_multiple'] != 0]
        winning_r_trades = [r for r in valid_r_trades if r['is_winner']]
        losing_r_trades = [r for r in valid_r_trades if not r['is_winner']]
        
        r_statistics = {
            'total_valid_r_trades': len(valid_r_trades),
            'winning_r_trades': len(winning_r_trades),
            'losing_r_trades': len(losing_r_trades),
            'r_win_rate': (len(winning_r_trades) / len(valid_r_trades) * 100) if valid_r_trades else 0,
            'average_r_multiple': sum(r['r_multiple'] for r in valid_r_trades) / len(valid_r_trades) if valid_r_trades else 0,
            'average_winning_r': sum(r['r_multiple'] for r in winning_r_trades) / len(winning_r_trades) if winning_r_trades else 0,
            'average_losing_r': sum(r['r_multiple'] for r in losing_r_trades) / len(losing_r_trades) if losing_r_trades else 0,
            'best_r_multiple': max((r['r_multiple'] for r in valid_r_trades), default=0),
            'worst_r_multiple': min((r['r_multiple'] for r in valid_r_trades), default=0),
            'total_r_profit': sum(r['r_multiple'] for r in winning_r_trades),
            'total_r_loss': sum(r['r_multiple'] for r in losing_r_trades),
            'r_expectancy': sum(r['r_multiple'] for r in valid_r_trades) / len(valid_r_trades) if valid_r_trades else 0
        }
        
        # Calculate basic statistics
        total_trades = len(detailed_trades)
        profitable_trades = len([t for t in detailed_trades if t.get('profit', 0) > 0])
        loss_trades = total_trades - profitable_trades
        total_profit = sum(t.get('profit', 0) for t in detailed_trades)
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Create response in the expected format
        response = {
            "success": True,
            "message": "Analysis completed successfully",
            "data": {
                "account_info": {
                    "account_number": account_info.get('account_number', 'N/A'),
                    "account_name": account_info.get('account_name', 'N/A'),
                    "currency": account_info.get('currency', 'USD'),
                    "leverage": account_info.get('leverage', 'N/A'),
                    "report_date": 'N/A'
                },
                "trade_statistics": {
                    "total_trades": total_trades,
                    "profit_trades_count": profitable_trades,
                    "loss_trades_count": loss_trades,
                    "profit_trades_percentage": win_rate
                },
                "financial_summary": {
                    "balance": 0.0,
                    "equity": 0.0,
                    "closed_trade_pnl": total_profit,
                    "floating_pnl": 0.0,
                    "free_margin": 0.0
                },
                "calculated_metrics": {
                    "total_net_profit": total_profit,
                    "profit_factor": 1.0,
                    "win_rate": win_rate,
                    "expected_payoff": total_profit / total_trades if total_trades > 0 else 0,
                    "maximum_drawdown_percentage": 0.0,
                    "recovery_factor": 1.0,
                    "risk_reward_ratio": 1.0,
                    "kelly_percentage": 0.0,
                    "standard_deviation": 0.0,
                    "skewness": 0.0,
                    "kurtosis": 0.0
                },
                "closed_trades": detailed_trades,
                "open_trades": [],
                "r_multiple_statistics": r_statistics,
                "r_multiple_data": r_multiple_data
            },
            "total_trades": total_trades,
            "processing_time": 0.1
        }
        
        logger.info(f"Simple analysis completed: {total_trades} trades found, profit: {total_profit}")
        return response
        
    except Exception as e:
        logger.error(f"Simple file analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


if __name__ == "__main__":
    logger.info(f"Starting server with configuration:")
    logger.info(f"   - Host: 0.0.0.0")
    logger.info(f"   - Port: 5501")
    logger.info(f"   - Debug: {settings.DEBUG}")
    logger.info(f"   - Reload: {settings.DEBUG}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5501,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
        access_log=True
    )
