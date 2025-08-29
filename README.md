# 🚀 MT4 Risk Management Calculator

A comprehensive risk management and trading analysis tool for MT4 trading statements.

## 📋 Project Overview

This project provides a complete solution for analyzing MT4 trading statements with advanced R-Multiple calculations and risk management tools. It consists of two main components:

1. **FastAPI Backend**: Processes MT4 HTML statements and performs advanced calculations
2. **Web Frontend**: User-friendly interface for uploading statements and viewing analysis

## 🔍 Key Features

- **📊 R-Multiple Analysis**: Calculate R-Multiple for each trade and comprehensive statistics
- **🛡️ Risk Management Calculator**: Position sizing and pre-trade risk assessment
- **📈 Trading Performance Metrics**: 45+ trading metrics with professional formulas
- **📱 Modern UI**: Tradezella-inspired dark theme with responsive design
- **🔄 File Upload**: Easy HTML statement upload and processing
- **📋 Individual Trade Analysis**: Detailed breakdown of each trade's risk metrics

## 🏗️ Architecture

```
project/
├── mt4_fastapi_backend/     # Python FastAPI backend
│   ├── app/                 # Core application code
│   │   ├── api/             # API endpoints
│   │   ├── core/            # Core configuration
│   │   ├── models/          # Data models
│   │   └── services/        # Business logic
│   ├── main.py              # Application entry point
│   └── requirements.txt     # Python dependencies
└── mt4_frontend/            # Web frontend
    ├── index.html           # Main HTML file
    ├── styles.css           # CSS styling
    └── script.js            # JavaScript functionality
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Web browser (Chrome, Firefox, Edge)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Satviksangamkar/Risk-Management-MT4.git
   cd Risk-Management-MT4
   ```

2. Install Python dependencies:
   ```bash
   cd mt4_fastapi_backend
   pip install -r requirements.txt
   ```

3. Start the server:
   ```bash
   python main.py
   ```

4. Access the application:
   Open your browser and navigate to `http://localhost:5501`

## 📊 Usage

1. **Upload MT4 Statement**:
   - Click "Choose File" and select your MT4 HTML statement
   - Click "Analyze" to process the file

2. **View Analysis Results**:
   - Account information
   - Trading summary
   - Financial metrics
   - R-Multiple statistics
   - Individual trade analysis

3. **Use Risk Calculator**:
   - Enter trade parameters
   - Get position sizing recommendations
   - View risk assessment

## 📚 Documentation

- [Backend Technical Documentation](mt4_fastapi_backend/README.md)
- [API Documentation](mt4_fastapi_backend/API_DOCUMENTATION.md)
- [Function Reference](mt4_fastapi_backend/FUNCTION_REFERENCE.md)

## 🔧 Technical Details

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Data Processing**: BeautifulSoup4
- **Mathematical Engine**: Custom R-Multiple calculation algorithms

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
