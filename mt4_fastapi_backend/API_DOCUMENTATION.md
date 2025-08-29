# 🌐 MT4 Backend - Complete API Documentation

## 📋 API Overview

### Base Information
- **Base URL**: `http://localhost:5501`
- **API Version**: `v1`
- **Content Type**: `application/json`
- **Documentation**: Available at `/docs` (Swagger UI)
- **Alternative Docs**: Available at `/redoc` (ReDoc)

### Authentication
- **Current**: No authentication required
- **Future**: Can be extended with JWT tokens or API keys

---

## 🔍 Complete Endpoint Reference

### 1. Health & Monitoring Endpoints

#### `GET /health`
**Purpose**: Basic application health check
**Use Case**: Load balancer health checks, monitoring systems
**Response Time**: < 10ms
**Dependencies**: None

**Response**:
```json
{
    "status": "healthy",
    "version": "1.0.0", 
    "service": "MT4 Analysis Backend",
    "environment": "production"
}
```

**Status Codes**:
- `200`: Service healthy
- `500`: Service error

#### `GET /api/v1/mt4/health`
**Purpose**: Detailed MT4 service health with component status
**Use Case**: Service-specific monitoring, debugging
**Dependencies**: MT4Service initialization

**Response**:
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "uptime": null
}
```

#### `GET /api/v1/version`
**Purpose**: API version information
**Response**:
```json
{
    "api_version": "v1",
    "service_version": "1.0.0",
    "project_name": "MT4 Analysis Backend"
}
```

### 2. File Analysis Endpoints

#### `POST /api/v1/mt4/analyze/file-simple`
**Purpose**: Enhanced MT4 file analysis with detailed R-Multiple calculations
**Content Type**: `multipart/form-data`
**File Size Limit**: 50MB
**Supported Formats**: `.htm`, `.html`

**Request**:
```
POST /api/v1/mt4/analyze/file-simple
Content-Type: multipart/form-data

file: [MT4 HTML file]
```

**Response Structure**:
```json
{
    "success": true,
    "message": "Analysis completed successfully",
    "data": {
        "account_info": {
            "account_number": "12345678",
            "account_name": "Standard Account", 
            "currency": "USD",
            "leverage": "1:100",
            "report_date": "N/A"
        },
        "trade_statistics": {
            "total_trades": 14,
            "profit_trades_count": 5,
            "loss_trades_count": 9,
            "profit_trades_percentage": 35.71
        },
        "financial_summary": {
            "balance": 10000.0,
            "equity": 9713.83,
            "closed_trade_pnl": -286.17,
            "floating_pnl": 0.0,
            "free_margin": 9713.83
        },
        "calculated_metrics": {
            "total_net_profit": -286.17,
            "profit_factor": 0.85,
            "win_rate": 35.71,
            "expected_payoff": -20.44,
            "maximum_drawdown_percentage": 2.86,
            "recovery_factor": 0.0,
            "risk_reward_ratio": 1.0,
            "kelly_percentage": 0.0,
            "standard_deviation": 0.0,
            "skewness": 0.0,
            "kurtosis": 0.0
        },
        "r_multiple_statistics": {
            "total_valid_r_trades": 13,
            "winning_r_trades": 1,
            "losing_r_trades": 12,
            "r_win_rate": 7.69,
            "average_r_multiple": -0.447,
            "average_winning_r": 0.126,
            "average_losing_r": -0.495,
            "best_r_multiple": 0.126,
            "worst_r_multiple": -1.000,
            "total_r_profit": 0.126,
            "total_r_loss": -5.940,
            "r_expectancy": -0.4470
        },
        "r_multiple_data": [
            {
                "ticket": "782680520",
                "r_multiple": -1.000,
                "trade_type": "buy",
                "risk_amount": 41.38,
                "profit": -41.38,
                "is_winner": false
            }
        ],
        "closed_trades": [
            {
                "ticket": "782680520",
                "type": "buy",
                "size": 1.00,
                "profit": -41.38,
                "entry_price": 108177.74,
                "stop_loss": 108136.36,
                "take_profit": 0.0,
                "risk_per_share": 41.38,
                "reward_per_share": 0,
                "risk_amount": 41.38,
                "r_multiple": -1.000,
                "is_valid_r_setup": true,
                "potential_reward": 0,
                "theoretical_r_multiple": 0.0
            }
        ],
        "open_trades": []
    },
    "total_trades": 14,
    "processing_time": 0.1
}
```

**Status Codes**:
- `200`: Analysis successful
- `400`: Invalid file or parameters
- `413`: File too large
- `500`: Processing error

**Error Response Example**:
```json
{
    "success": false,
    "message": "Analysis failed: Invalid HTML content",
    "error_code": "PROCESSING_ERROR",
    "details": {
        "error": "BeautifulSoup parsing failed"
    },
    "path": "/api/v1/mt4/analyze/file-simple"
}
```

### 3. Risk Management Endpoints

#### `POST /api/v1/mt4/risk-calculator`
**Purpose**: Comprehensive risk calculation for trade planning
**Content Type**: `application/json`

**Request Body**:
```json
{
    "entry_price": 1.2500,
    "stop_loss": 1.2450,
    "take_profit": 1.2600,
    "trade_type": "buy",
    "account_balance": 10000.0,
    "risk_percentage": 2.0,
    "position_size": null
}
```

**Field Validation**:
- `entry_price`: Required, > 0
- `stop_loss`: Required, > 0
- `take_profit`: Optional, > 0
- `trade_type`: Required, "buy" or "sell"
- `account_balance`: Optional, ≥ 0
- `risk_percentage`: Default 2.0, range 0.1-10.0
- `position_size`: Optional, > 0

**Response Structure**:
```json
{
    "success": true,
    "message": "Risk calculation completed successfully",
    "data": {
        "trade_setup": {
            "entry_price": 1.25,
            "stop_loss": 1.245,
            "take_profit": 1.26,
            "trade_type": "buy",
            "is_valid_setup": true
        },
        "risk_metrics": {
            "risk_per_share": 0.005,
            "reward_per_share": 0.01,
            "total_risk": 100.0,
            "total_reward": 200.0,
            "r_multiple": 2.0,
            "risk_reward_ratio": 2.0,
            "required_win_rate": 33.33
        },
        "position_analysis": {
            "position_size": 20000.0,
            "optimal_position_size": 20000.0,
            "max_position_size": 100000.0,
            "position_value": 25000.0,
            "risk_level": "MEDIUM"
        },
        "account_analysis": {
            "account_balance": 10000.0,
            "risk_percentage": 2.0,
            "recommendations": [
                "Excellent risk/reward ratio of 1:2.00"
            ]
        }
    }
}
```

**Risk Level Classification**:
- **LOW**: ≤ 1% of account balance
- **MEDIUM**: 1-2% of account balance  
- **HIGH**: 2-5% of account balance
- **EXTREME**: > 5% of account balance

**Status Codes**:
- `200`: Calculation successful
- `400`: Invalid parameters
- `422`: Validation error
- `500`: Calculation error

---

## 📊 Data Models Reference

### Request Models

#### RiskCalculatorRequest
```python
{
    "entry_price": float,        # Required, > 0
    "stop_loss": float,          # Required, > 0  
    "take_profit": float,        # Optional, > 0
    "trade_type": str,           # Required, "buy" | "sell"
    "account_balance": float,    # Optional, ≥ 0
    "risk_percentage": float,    # Default 2.0, range 0.1-10.0
    "position_size": float       # Optional, > 0
}
```

### Response Models

#### Enhanced Analysis Response
**Contains**: Complete trading analysis with individual trade R-Multiple data

**Key Sections**:
1. **account_info**: MT4 account details
2. **trade_statistics**: Trade counts and percentages
3. **financial_summary**: Balance and P/L information
4. **calculated_metrics**: 45+ trading performance metrics
5. **r_multiple_statistics**: Aggregate R-Multiple analysis
6. **r_multiple_data**: Individual trade R-Multiple details
7. **closed_trades**: Enhanced trade data with R-calculations
8. **open_trades**: Current open positions

#### Risk Calculator Response
**Contains**: Comprehensive pre-trade risk analysis

**Key Sections**:
1. **trade_setup**: Validated trade parameters
2. **risk_metrics**: Risk/reward calculations
3. **position_analysis**: Position sizing recommendations
4. **account_analysis**: Account impact assessment

---

## 🔧 Configuration Reference

### Environment Variables
```bash
# Application Configuration
DEBUG=False                          # Enable debug mode
LOG_LEVEL=INFO                      # Logging level
PROJECT_NAME="MT4 Analysis Backend" # Application name

# Server Configuration  
HOST=0.0.0.0                        # Server host
PORT=5501                           # Server port

# File Upload Limits
MAX_UPLOAD_SIZE=52428800            # 50MB in bytes
MAX_TRADES_PER_REQUEST=10000        # Maximum trades per analysis

# Security
SECRET_KEY=your-secret-key-here     # Application secret key

# CORS Origins (comma-separated)
BACKEND_CORS_ORIGINS=http://localhost:5501,http://127.0.0.1:5501
```

### Application Settings
```python
# Default Configuration Values
{
    "PROJECT_NAME": "MT4 Analysis Backend",
    "VERSION": "1.0.0",
    "DEBUG": False,
    "API_V1_STR": "/api/v1",
    "MAX_UPLOAD_SIZE": 50 * 1024 * 1024,  # 50MB
    "MAX_TRADES_PER_REQUEST": 10000,
    "LOG_LEVEL": "INFO",
    "LOG_FORMAT": "detailed"
}
```

---

## 🎯 Complete Backend Achievement Summary

### 1. Professional API Implementation
- ✅ **RESTful API design** with proper HTTP methods and status codes
- ✅ **Comprehensive error handling** with structured responses
- ✅ **Input validation** using Pydantic models
- ✅ **API documentation** with Swagger UI and ReDoc
- ✅ **Health monitoring** endpoints for production deployment

### 2. Advanced Trading Analytics
- ✅ **Individual trade R-Multiple calculation** for each trade
- ✅ **Comprehensive R-Multiple statistics** (13 different metrics)
- ✅ **Risk setup validation** for proper stop loss positioning
- ✅ **Enhanced trade data structure** with detailed risk information
- ✅ **Professional trading metrics** (45+ calculations)

### 3. Mathematical Engine
- ✅ **Kelly Criterion** for optimal position sizing
- ✅ **Maximum Drawdown** calculation with equity curve analysis
- ✅ **Statistical analysis** (standard deviation, skewness, kurtosis)
- ✅ **Risk/Reward optimization** with required win rate calculations
- ✅ **Position sizing algorithms** for risk management

### 4. Production-Ready Features
- ✅ **File upload processing** with validation and cleanup
- ✅ **Background task management** for resource cleanup
- ✅ **Structured logging** for debugging and monitoring
- ✅ **Configuration management** with environment variables
- ✅ **CORS configuration** for frontend integration
- ✅ **Error recovery** and graceful failure handling

### 5. Data Processing Pipeline
- ✅ **Robust HTML parsing** with BeautifulSoup
- ✅ **Multi-table data extraction** handling various MT4 formats
- ✅ **Numeric data validation** with error recovery
- ✅ **Trade data normalization** into structured models
- ✅ **Comprehensive data validation** with detailed error reporting

---

*This API documentation provides complete reference for all endpoints, functions, and capabilities of the MT4 FastAPI backend system.*
