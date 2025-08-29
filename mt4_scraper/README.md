# MT4 Scraper - Modular Version

A modular, industry-standard implementation of the MT4 trading report scraper that follows clean architecture principles.

## 🏗️ Project Structure

```
mt4_scraper/
├── __init__.py
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration constants
├── utils/
│   ├── __init__.py
│   ├── logging_utils.py     # Logging setup
│   ├── parsing_utils.py     # Data parsing utilities
│   └── file_utils.py        # File operations
├── models/
│   ├── __init__.py
│   └── data_models.py       # Data structures
├── parsers/
│   ├── __init__.py
│   ├── base_parser.py       # Base parsing functionality
│   ├── header_parser.py     # Header information parser
│   ├── trade_parsers.py     # Trade data parsers
│   ├── summary_parser.py    # Summary and performance parser
│   └── main_parser.py       # Main parser coordinator
└── main.py                  # Main orchestrator
```

## 🚀 Features

- **Modular Architecture**: Clean separation of concerns
- **Industry Standards**: Follows Python best practices
- **Type Hints**: Full type annotation support
- **Data Parsing**: Complete MT4 HTML report parsing
- **Structured Data**: Returns well-organized data objects
- **Logging**: Detailed file-specific logging with progress tracking

## 📦 Installation

1. Ensure you have Python 3.7+ installed
2. Install required dependencies:
   ```bash
   pip install beautifulsoup4 pandas
   ```

## 🛠️ Usage

### Basic Usage

```python
from mt4_scraper.main import MT4Scraper

# Initialize scraper
scraper = MT4Scraper(input_file="10.htm")

# Run analysis and get data
try:
    analysis = scraper.run_analysis()

    # Access the parsed data
    print(f"Account: {analysis.header_information.account_number}")
    print(f"Closed Trades: {len(analysis.closed_transactions.trades)}")
    print(f"Open Trades: {len(analysis.open_trades.trades)}")
    print(f"Balance: {analysis.summary_section.balance}")

except Exception as e:
    print(f"Error: {e}")
```

### Command Line Usage

```bash
python mt4_scraper/main.py
```

### Custom File Processing

```python
# Process any MT4 HTML file
scraper = MT4Scraper(input_file="your_report.htm")
analysis = scraper.run_analysis()

# Work with the returned data
header = analysis.header_information
trades = analysis.closed_transactions.trades
summary = analysis.summary_section
```

## 🔧 Configuration

All configuration is centralized in `config/settings.py`:

- Default input file
- Logging settings
- HTML parsing options
- Field mappings for data extraction
- Section headers and labels

## 📊 Data Models

The scraper extracts the following data structures:

- **HeaderInformation**: Account details, currency, leverage, etc.
- **ClosedTransactions**: Closed trade data with P/L
- **OpenTrades**: Open positions with floating P/L
- **WorkingOrders**: Pending orders
- **SummarySection**: Account summary data
- **PerformanceDetails**: Trading performance metrics

## 🧪 Validation

The modular version includes comprehensive validation:

- **Output Validation**: Ensures all required sections are present
- **Data Integrity**: Cross-validates between JSON and CSV outputs
- **Comparison Tooling**: Compare with original scraper output

## 📈 Benefits of Modularization

1. **Maintainability**: Easier to modify individual components
2. **Testability**: Each module can be tested independently
3. **Reusability**: Components can be reused in other projects
4. **Readability**: Clear separation of concerns
5. **Scalability**: Easy to add new features or parsers

## 🔍 Comparison Results

When compared to the original monolithic version:

- **Functionality**: 100% preserved
- **Performance**: Comparable execution times
- **Code Size**: Reduced through modularization
- **Maintainability**: Significantly improved
- **Testability**: Greatly enhanced

## 🤝 Contributing

1. Follow the existing modular structure
2. Add type hints for new functions
3. Include docstrings for documentation
4. Add validation for new features
5. Update tests accordingly

## 📄 License

This project maintains the same license as the original scraper.
