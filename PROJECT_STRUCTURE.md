# 🚀 MT4 Calculator - Professional Trading Platform

## 📁 Complete Project Structure

```
MT4_CALCULATOR/
├── 📂 mt4_fastapi_backend/          # 🔧 FastAPI Backend Server
│   ├── 📂 app/                      # Main application package
│   │   ├── 📂 api/                  # API routes and endpoints
│   │   │   ├── 📂 dependencies/     # FastAPI dependencies
│   │   │   │   └── services.py      # Service dependency injection
│   │   │   └── 📂 v1/               # API version 1
│   │   │       ├── api.py           # Main API router
│   │   │       └── 📂 endpoints/    # Individual endpoint modules
│   │   │           └── mt4_analysis.py  # MT4 analysis endpoints
│   │   ├── 📂 core/                 # Core application modules
│   │   │   ├── config.py            # Application configuration
│   │   │   ├── errors.py            # Error handling
│   │   │   └── logging.py           # Logging configuration
│   │   ├── 📂 models/               # Data models
│   │   │   ├── 📂 domain/           # Domain models
│   │   │   │   └── mt4_models.py    # MT4 trading data models
│   │   │   ├── 📂 requests/         # Request models
│   │   │   │   ├── mt4_requests.py  # MT4 analysis requests
│   │   │   │   └── risk_requests.py # Risk calculator requests
│   │   │   └── 📂 responses/        # Response models
│   │   │       └── mt4_responses.py # API response models
│   │   ├── 📂 services/             # Business logic services
│   │   │   ├── 📂 calculations/     # Calculation services
│   │   │   │   └── mt4_calculator_service.py  # Trading calculations
│   │   │   ├── 📂 parsing/          # HTML parsing services
│   │   │   │   └── mt4_parser_service.py      # MT4 HTML parser
│   │   │   ├── 📂 validation/       # Data validation services
│   │   │   │   └── mt4_validation_service.py  # Data validation
│   │   │   └── mt4_service.py       # Main MT4 orchestration service
│   │   └── 📂 utils/                # Utility modules
│   │       └── file_utils.py        # File handling utilities
│   ├── main.py                      # 🎯 Main application entry point
│   ├── requirements.txt             # Python dependencies
│   └── 📂 uploads/                  # File upload directory
│
├── 📂 mt4_frontend/                 # 🎨 Tradezella-Inspired Frontend
│   ├── index.html                   # Main HTML page
│   ├── styles.css                   # Professional dark theme CSS
│   ├── script.js                    # Frontend JavaScript logic
│   └── README.md                    # Frontend documentation
│
├── 📂 logs/                         # 📊 Application logs
├── 10.htm                           # 📄 Sample MT4 file for testing
├── start_mt4_app.bat               # 🚀 Quick start script
└── test_port_5500.py               # 🧪 Integration test script
```

## 🔥 Key Features

### 🏗️ **Backend (FastAPI)**
- **Professional REST API** with comprehensive MT4 analysis
- **Enhanced R-Multiple calculations** for each trade
- **Risk management tools** and position sizing
- **File upload processing** for MT4 HTML statements
- **Comprehensive error handling** and logging
- **Pydantic data validation** and serialization
- **CORS configuration** for frontend integration
- **Health monitoring** endpoints

### 🎨 **Frontend (Tradezella-Inspired)**
- **Professional dark theme** trading platform interface
- **Modern card-based layout** with hover effects
- **Comprehensive R-Multiple analysis display**
- **Individual trade analysis table** with detailed metrics
- **Real-time status indicators** and notifications
- **Responsive design** for all devices
- **Professional typography** with monospace trading data
- **Smooth animations** and micro-interactions

## 🚀 **Quick Start**

1. **Activate Environment:**
   ```bash
   ult_trz\Scripts\activate
   ```

2. **Start Backend:**
   ```bash
   cd mt4_fastapi_backend
   python main.py
   ```

3. **Access Frontend:**
   - Open: http://localhost:5501
   - Upload MT4 `.htm` files
   - View comprehensive analysis

## 📊 **What You Get**

### **Backend API Endpoints:**
- `POST /api/v1/mt4/analyze/file-simple` - File analysis
- `POST /api/v1/mt4/risk-calculator` - Risk calculations
- `GET /api/v1/mt4/health` - Service health
- `GET /health` - Application health
- `GET /docs` - API documentation

### **Frontend Features:**
- 📋 Account Information Display
- 📊 Trading Summary with Win/Loss rates
- 💰 Financial Summary with P/L breakdown
- 🏆 Performance Metrics with advanced calculations
- 🛡️ Risk Analysis with comprehensive data
- 📈 Enhanced R-Multiple Matrix
- 📋 Individual Trade Analysis Table

## 🎯 **Perfect for:**
- Professional traders analyzing MT4 statements
- Trading performance evaluation
- Risk management and position sizing
- R-Multiple analysis and trade optimization
- Modern trading platform experience
