"""Configuration settings for MT4 Scraper."""

import os
from typing import Dict, List

# File paths and names
DEFAULT_INPUT_FILE = "10.htm"

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'
LOGGER_NAME = 'MT4Scraper'

# HTML parsing settings
ENCODING = 'utf-8'
ENCODING_ERRORS = 'replace'
HTML_PARSER = 'html.parser'

# Section headers in MT4 reports
SECTION_HEADERS = {
    'closed_transactions': 'Closed Transactions:',
    'open_trades': 'Open Trades:',
    'working_orders': 'Working Orders:',
}

# Field mappings for data extraction
CLOSED_TRANSACTIONS_FIELD_MAPPING = {
    's_/_l': 'stop_loss',
    't_/_p': 'take_profit',
    'close_time': 'close_time',
    'close_price': 'close_price'
}

OPEN_TRADES_FIELD_MAPPING = {
    's_/_l': 'stop_loss',
    't_/_p': 'take_profit'
}

WORKING_ORDERS_FIELD_MAPPING = {
    's_/_l': 'stop_loss',
    't_/_p': 'take_profit',
    'market_price': 'market_price'
}

# End markers for section parsing
SECTION_END_MARKERS = [
    'Closed P/L:', 'Floating P/L:', 'Open Trades:',
    'Working Orders:', 'Summary:'
]

# Numeric columns that need parsing
NUMERIC_COLUMNS = [
    'Size', 'Price', 'S/L', 'T/P', 'Commission',
    'Taxes', 'Swap', 'Profit', '&nbsp;'
]

# Summary section labels
SUMMARY_LABELS = {
    'Deposit/Withdrawal:': 'deposit_withdrawal',
    'Credit Facility:': 'credit_facility',
    'Closed Trade P/L:': 'closed_trade_pnl',
    'Floating P/L:': 'floating_pnl',
    'Margin:': 'margin',
    'Balance:': 'balance',
    'Equity:': 'equity',
    'Free Margin:': 'free_margin'
}

# Performance section labels
PERFORMANCE_LABELS = {
    'Gross Profit:': 'gross_profit',
    'Gross Loss:': 'gross_loss',
    'Total Net Profit:': 'total_net_profit',
    'Profit Factor:': 'profit_factor',
    'Expected Payoff:': 'expected_payoff',
    'Absolute Drawdown:': 'absolute_drawdown',
    'Maximal Drawdown:': 'maximal_drawdown_amount',
    'Relative Drawdown:': 'relative_drawdown_percentage',
    'Total Trades:': 'total_trades',
    'Largest profit trade:': 'largest_profit_trade',
    'Largest loss trade:': 'largest_loss_trade',
    'Average profit trade:': 'average_profit_trade',
    'Average loss trade:': 'average_loss_trade'
}

# Required sections for validation
REQUIRED_SECTIONS = [
    'header_information', 'closed_transactions', 'open_trades',
    'working_orders', 'summary_section', 'performance_details'
]


