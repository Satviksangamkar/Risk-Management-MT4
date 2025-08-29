"""
MT4 Parser Service
HTML parsing and data extraction for MT4 statements
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup

from app.models.domain.mt4_models import (
    TradeData, AccountInfo, FinancialSummary,
    PerformanceMetrics, TradeStatistics, TradeType
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class MT4ParserService:
    """Service for parsing MT4 HTML statements"""

    def __init__(self):
        # Pre-compiled regex patterns for performance
        self.numeric_pattern = re.compile(r'-?\d*\.?\d+')
        self.whitespace_pattern = re.compile(r'\s+')

        # Column mapping for trade data
        self.trade_columns = {
            'ticket': 0,
            'open_time': 1,
            'type': 2,
            'size': 3,
            'item': 4,
            'price': 5,
            's_l': 6,
            't_p': 7,
            'close_time': 8,
            'close_price': 9,
            'commission': 10,
            'taxes': 11,
            'swap': 12,
            'profit': 13
        }

        # Numeric columns for parsing
        self.numeric_columns = {
            'size', 'price', 's_l', 't_p', 'close_price',
            'commission', 'taxes', 'swap', 'profit'
        }

    def parse_html_statement(self, html_content: str) -> Dict[str, Any]:
        """
        Parse complete MT4 HTML statement
        Returns comprehensive trading data dictionary
        """
        logger.info("Starting MT4 HTML statement parsing")

        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract account information
        account_info = self._extract_account_info(soup)

        # Extract financial summary
        financial_summary = self._extract_financial_summary(soup)

        # Extract performance metrics
        performance_metrics = self._extract_performance_metrics(soup)

        # Extract trade statistics
        trade_statistics = self._extract_trade_statistics(soup)

        # Extract trades
        trades = self._extract_trades(soup)

        logger.info(f"Successfully parsed {len(trades)} trades")

        return {
            'account_info': account_info,
            'financial_summary': financial_summary,
            'performance_metrics': performance_metrics,
            'trade_statistics': trade_statistics,
            'trades': trades,
            'closed_trades': [t for t in trades if t.is_closed_trade],
            'open_trades': [t for t in trades if t.is_open_trade]
        }

    def _extract_account_info(self, soup: BeautifulSoup) -> AccountInfo:
        """Extract account information from HTML"""
        account_info = AccountInfo()

        # Find account information table or section
        account_section = soup.find('table') or soup.find('div', class_=re.compile(r'account'))

        if account_section:
            text_content = account_section.get_text()

            # Extract account details using regex patterns
            patterns = {
                'account_number': r'Account:\s*(\w+)',
                'account_name': r'Name:\s*([^\n\r]+)',
                'currency': r'Currency:\s*([A-Z]{3})',
                'leverage': r'Leverage:\s*([^\n\r]+)'
            }

            for field, pattern in patterns.items():
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    setattr(account_info, field, match.group(1).strip())

        return account_info

    def _extract_financial_summary(self, soup: BeautifulSoup) -> FinancialSummary:
        """Extract financial summary from HTML"""
        financial_summary = FinancialSummary()

        # Get all text from the HTML for pattern matching
        full_text = soup.get_text()

        # Extract financial data using improved patterns that handle HTML formatting
        html_source = str(soup)
        patterns = {
            'deposit_withdrawal': r'Deposit/Withdrawal:</b></td>.*?<b>([-+]?[\d,\s]*\.?\d+)</b>',
            'credit_facility': r'Credit Facility:</b></td>.*?<b>([-+]?[\d,\s]*\.?\d+)</b>',
            'closed_trade_pnl': r'Closed Trade P/L:</b></td>.*?<b>([-+]?[\d,\s]*\.?\d+)</b>',
            'floating_pnl': r'Floating P/L:</b></td>.*?<b>([-+]?[\d,\s]*\.?\d+)</b>',
            'margin': r'Margin:</b></td>.*?<b>([-+]?[\d,\s]*\.?\d+)</b>',
            'balance': r'Balance:</b></td>.*?<b>([-+]?[\d,\s]*\.?\d+)</b>',
            'equity': r'Equity:</b></td>.*?<b>([-+]?[\d,\s]*\.?\d+)</b>',
            'free_margin': r'Free Margin:</b></td>.*?<b>([-+]?[\d,\s]*\.?\d+)</b>'
        }

        # Extract using HTML source patterns
        for field, pattern in patterns.items():
            match = re.search(pattern, html_source, re.IGNORECASE | re.DOTALL)
            if match:
                value = self._parse_numeric_value(match.group(1))
                setattr(financial_summary, field, value)

        # Fallback to text-based patterns
        text_patterns = {
            'deposit_withdrawal': r'Deposit/Withdrawal:\s*([-+]?[\d,\s]*\.?\d+)',
            'credit_facility': r'Credit Facility:\s*([-+]?[\d,\s]*\.?\d+)',
            'closed_trade_pnl': r'Closed Trade P/L:\s*([-+]?[\d,\s]*\.?\d+)',
            'floating_pnl': r'Floating P/L:\s*([-+]?[\d,\s]*\.?\d+)',
            'margin': r'Margin:\s*([-+]?[\d,\s]*\.?\d+)',
            'balance': r'Balance:\s*([-+]?[\d,\s]*\.?\d+)',
            'equity': r'Equity:\s*([-+]?[\d,\s]*\.?\d+)',
            'free_margin': r'Free Margin:\s*([-+]?[\d,\s]*\.?\d+)'
        }

        for field, pattern in text_patterns.items():
            if getattr(financial_summary, field) == 0.0:  # Only if not already found
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    value = self._parse_numeric_value(match.group(1))
                    setattr(financial_summary, field, value)

        return financial_summary

    def _extract_performance_metrics(self, soup: BeautifulSoup) -> PerformanceMetrics:
        """Extract performance metrics from HTML"""
        performance_metrics = PerformanceMetrics()

        # Get all text from the HTML for pattern matching
        full_text = soup.get_text()

        # Extract performance data from the text using both HTML and text patterns
        html_source = str(soup)
        
        # HTML patterns for more precise extraction
        html_patterns = {
            'gross_profit': r'Gross Profit:</b></td>.*?<b>([-+]?[\d,\s]*\.?\d+)</b>',
            'gross_loss': r'Gross Loss:</b></td>.*?<b>([-+]?[\d,\s]*\.?\d+)</b>',
            'total_net_profit': r'Total Net Profit:</b></td>.*?<b>([-+]?[\d,\s]*\.?\d+)</b>',
            'profit_factor': r'Profit Factor:</b></td>.*?<b>([-+]?[\d,\s]*\.?\d+)</b>',
            'expected_payoff': r'Expected Payoff:</b></td>.*?<b>([-+]?[\d,\s]*\.?\d+)</b>',
            'absolute_drawdown': r'Absolute Drawdown:</b></td>.*?<b>([-+]?[\d,\s]*\.?\d+)</b>',
            'maximal_drawdown_amount': r'Maximal Drawdown:</b></td>.*?<b>([-+]?[\d,\s]*\.?\d+)',
            'maximal_drawdown_percentage': r'Maximal Drawdown.*?\(\s*(\d+\.?\d*)\s*%\)',
            'relative_drawdown_amount': r'Relative Drawdown.*?:\s*([-+]?[\d,\s]*\.?\d+)',
            'relative_drawdown_percentage': r'Relative Drawdown.*?\(\s*(\d+\.?\d*)\s*%\)'
        }

        # Try HTML patterns first
        for field, pattern in html_patterns.items():
            match = re.search(pattern, html_source, re.IGNORECASE | re.DOTALL)
            if match:
                if 'percentage' in field:
                    value = float(match.group(1))
                else:
                    value = self._parse_numeric_value(match.group(1))
                setattr(performance_metrics, field, value)

        # Fallback to text patterns
        patterns = {
            'gross_profit': r'Gross Profit:\s*([-+]?[\d,\s]*\.?\d+)',
            'gross_loss': r'Gross Loss:\s*([-+]?[\d,\s]*\.?\d+)',
            'total_net_profit': r'Total Net Profit:\s*([-+]?[\d,\s]*\.?\d+)',
            'profit_factor': r'Profit Factor:\s*([-+]?[\d,\s]*\.?\d+)',
            'expected_payoff': r'Expected Payoff:\s*([-+]?[\d,\s]*\.?\d+)',
            'absolute_drawdown': r'Absolute Drawdown:\s*([-+]?[\d,\s]*\.?\d+)',
            'maximal_drawdown_amount': r'Maximal Drawdown:\s*([-+]?[\d,\s]*\.?\d+)',
            'maximal_drawdown_percentage': r'Maximal Drawdown.*?\(\s*(\d+\.?\d*)\s*%\)',
            'relative_drawdown_amount': r'Relative Drawdown.*?:\s*([-+]?[\d,\s]*\.?\d+)',
            'relative_drawdown_percentage': r'Relative Drawdown.*?\(\s*(\d+\.?\d*)\s*%\)'
        }

        # Apply fallback patterns only if not already found
        for field, pattern in patterns.items():
            if getattr(performance_metrics, field) == 0.0:  # Only if not already found
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    if 'percentage' in field:
                        value = float(match.group(1))
                    else:
                        value = self._parse_numeric_value(match.group(1))
                    setattr(performance_metrics, field, value)

        return performance_metrics

    def _extract_trade_statistics(self, soup: BeautifulSoup) -> TradeStatistics:
        """Extract trade statistics from HTML"""
        trade_statistics = TradeStatistics()

        # Get all text from the HTML for pattern matching
        full_text = soup.get_text()

        # Extract trade statistics using both HTML and text patterns
        html_source = str(soup)
        
        # HTML patterns for more precise extraction
        html_patterns = {
            'total_trades': r'Total Trades:</b></td>.*?<b>(\d+)</b>',
            'short_positions_count': r'Short Positions.*?:</b></td>.*?<b>(\d+)',
            'short_positions_win_rate': r'Short Positions.*?\(\s*(\d+\.?\d*)\s*%\)',
            'long_positions_count': r'Long Positions.*?:</b></td>.*?<b>(\d+)',
            'long_positions_win_rate': r'Long Positions.*?\(\s*(\d+\.?\d*)\s*%\)',
            'profit_trades_count': r'Profit Trades.*?:</b></td>.*?<b>(\d+)',
            'profit_trades_percentage': r'Profit Trades.*?\(\s*(\d+\.?\d*)\s*%\)',
            'loss_trades_count': r'Loss trades.*?:</b></td>.*?<b>(\d+)',
            'loss_trades_percentage': r'Loss trades.*?\(\s*(\d+\.?\d*)\s*%\)'
        }

        # Try HTML patterns first
        for field, pattern in html_patterns.items():
            match = re.search(pattern, html_source, re.IGNORECASE | re.DOTALL)
            if match:
                if 'win_rate' in field or 'percentage' in field:
                    value = float(match.group(1))
                else:
                    value = int(match.group(1))
                setattr(trade_statistics, field, value)

        # Fallback to text patterns
        patterns = {
            'total_trades': r'Total Trades:\s*(\d+)',
            'short_positions_count': r'Short Positions.*?:\s*(\d+)',
            'short_positions_win_rate': r'Short Positions.*?\(\s*(\d+\.?\d*)\s*%\)',
            'long_positions_count': r'Long Positions.*?:\s*(\d+)',
            'long_positions_win_rate': r'Long Positions.*?\(\s*(\d+\.?\d*)\s*%\)',
            'profit_trades_count': r'Profit Trades.*?:\s*(\d+)',
            'profit_trades_percentage': r'Profit Trades.*?\(\s*(\d+\.?\d*)\s*%\)',
            'loss_trades_count': r'Loss trades.*?:\s*(\d+)',
            'loss_trades_percentage': r'Loss trades.*?\(\s*(\d+\.?\d*)\s*%\)'
        }

        # Apply fallback patterns only if not already found
        for field, pattern in patterns.items():
            current_value = getattr(trade_statistics, field)
            if current_value == 0 or current_value == 0.0:  # Only if not already found
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    if 'win_rate' in field or 'percentage' in field:
                        value = float(match.group(1))
                    else:
                        value = int(match.group(1))
                    setattr(trade_statistics, field, value)

        return trade_statistics

    def _extract_trades(self, soup: BeautifulSoup) -> List[TradeData]:
        """Extract trade data from HTML tables"""
        trades = []

        # Find all tables and look for trade data
        all_tables = soup.find_all('table')

        for table in all_tables:
            rows = table.find_all('tr')

            # Look for the "Closed Transactions" header to identify trade tables
            for i, row in enumerate(rows):
                row_text = row.get_text().strip()
                if 'closed transactions' in row_text.lower():
                    # Found the closed transactions section
                    # The next row should be the header, then the trade data starts
                    header_row_index = i + 1
                    if header_row_index < len(rows):
                        # Verify this is a header row with trade columns
                        header_cells = rows[header_row_index].find_all(['td', 'th'])
                        header_texts = [cell.get_text().strip().lower() for cell in header_cells]

                        # Check if this looks like a trade header
                        if any('ticket' in text for text in header_texts) and \
                           any('profit' in text for text in header_texts):
                            # This is the trade table, extract trades starting from next row
                            for trade_row in rows[header_row_index + 1:]:
                                cells = trade_row.find_all(['td', 'th'])
                                if len(cells) >= 10:  # Minimum cells for a trade row
                                    trade_data = self._parse_trade_row(cells)
                                    if trade_data.ticket:  # Only add valid trades
                                        trades.append(trade_data)
                    break  # Stop looking after finding closed transactions

        # If no trades found with the above method, try the fallback approach
        if not trades:
            for table in all_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text().strip() for cell in cells]

                    # Check if this looks like a trade row
                    if self._is_trade_row(cell_texts):
                        trade_data = self._parse_trade_from_text(cell_texts)
                        if trade_data.ticket:
                            trades.append(trade_data)

        return trades

    def _parse_trade_row(self, cells) -> TradeData:
        """Parse trade data from table cells"""
        trade_data = TradeData()

        for column_name, column_index in self.trade_columns.items():
            if column_index < len(cells):
                cell_text = cells[column_index].get_text().strip()

                if column_name in self.numeric_columns:
                    value = self._parse_numeric_value(cell_text)
                    setattr(trade_data, column_name, value)
                else:
                    setattr(trade_data, column_name, cell_text)

        # Determine trade type
        if trade_data.type and trade_data.type.strip():
            try:
                trade_data.type = TradeType(trade_data.type.lower().strip())
            except ValueError:
                # Skip invalid trade types (like header rows)
                return TradeData()  # Return empty trade data to skip
        else:
            return TradeData()  # Return empty trade data to skip

        return trade_data

    def _parse_trade_from_text(self, cell_texts: List[str]) -> TradeData:
        """Parse trade data from text cells"""
        trade_data = TradeData()

        # Try to identify trade data from text patterns
        for i, text in enumerate(cell_texts):
            text_lower = text.lower()

            # Identify trade type
            if 'buy' in text_lower:
                trade_data.type = TradeType.BUY
            elif 'sell' in text_lower:
                trade_data.type = TradeType.SELL

            # Try to extract numeric values
            if self._is_numeric_field(text):
                value = self._parse_numeric_value(text)
                # Assign to appropriate field based on position and content
                self._assign_numeric_field(trade_data, value, i, text)

        return trade_data

    def _find_section_by_header(self, soup: BeautifulSoup, headers: List[str]) -> Optional[Any]:
        """Find HTML section by header text"""
        for header in headers:
            # Try different header tags
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'th', 'td', 'div', 'span']:
                element = soup.find(tag, string=re.compile(header, re.IGNORECASE))
                if element:
                    # Return parent section
                    return element.find_parent(['table', 'div', 'section']) or element

        return None

    def _parse_numeric_value(self, text: str) -> float:
        """Parse numeric value from text"""
        if not text or text.strip() == '':
            return 0.0

        # Remove commas, spaces, and other formatting, keep numbers, dots, and minus signs
        clean_text = re.sub(r'[^\d.-]', '', text.strip().replace(' ', '').replace(',', ''))

        try:
            return float(clean_text)
        except ValueError:
            return 0.0

    def _is_trade_row(self, cell_texts: List[str]) -> bool:
        """Check if a row contains trade data"""
        text_combined = ' '.join(cell_texts).lower()

        # Look for trade indicators
        trade_indicators = ['buy', 'sell', 'lot', 'profit', 'loss', 'commission']

        return any(indicator in text_combined for indicator in trade_indicators)

    def _is_numeric_field(self, text: str) -> bool:
        """Check if text contains numeric data"""
        return bool(self.numeric_pattern.search(text))

    def _assign_numeric_field(self, trade_data: TradeData, value: float, position: int, original_text: str):
        """Assign numeric value to appropriate trade field"""
        # This is a simplified assignment - in production you'd want more sophisticated logic
        if 'profit' in original_text.lower():
            trade_data.profit = value
        elif 'size' in original_text.lower() or 'lot' in original_text.lower():
            trade_data.size = value
        elif 'price' in original_text.lower():
            if 'close' in original_text.lower():
                trade_data.close_price = value
            else:
                trade_data.price = value
        elif 'sl' in original_text.lower():
            trade_data.s_l = value
        elif 'tp' in original_text.lower():
            trade_data.t_p = value
