"""
Trade parser for MT4 HTML statements.
Extracts both open and closed trades data.
"""

from typing import List, Dict, Any, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from parsers.base_parser import BaseParser
from models.data_models import TradeData, TradeStatistics
from utils.parsing_utils import (
    parse_numeric_value,
    clean_header_name,
    validate_trade_data,
    safe_get_text
)
from config.settings import MT4Config


class TradeParser(BaseParser):
    """Parser for trade data sections."""

    def parse(self) -> List[TradeData]:
        """
        Main parse method - returns both closed and open trades combined.

        Returns:
            List[TradeData]: Combined list of all trades
        """
        all_trades = []
        all_trades.extend(self.parse_closed_trades())
        all_trades.extend(self.parse_open_trades())
        return all_trades

    def parse_closed_trades(self) -> List[TradeData]:
        """
        Parse closed trades data.

        Returns:
            List[TradeData]: List of closed trade objects
        """
        self.log_info("Parsing closed trades")

        closed_trades = []

        try:
            # Find the closed trades section
            closed_section = self._find_section_by_header('Closed Transactions:')
            if not closed_section:
                self.log_warning("No closed trades section found")
                return closed_trades

            # Find header row
            header_row = self._find_header_row(closed_section)
            if not header_row:
                self.log_warning("No header row found in closed trades")
                return closed_trades

            headers = [safe_get_text(td) for td in header_row.find_all('td')]
            self.log_debug(f"Found closed trades headers: {headers}")

            # Process data rows
            trades_data = self._process_trade_rows(header_row, headers)
            closed_trades = [self._create_trade_object(trade_dict) for trade_dict in trades_data]

            self.log_info(f"Successfully parsed {len(closed_trades)} closed trades")

        except Exception as e:
            self.log_error(f"Error parsing closed trades: {e}")

        return closed_trades

    def parse_open_trades(self) -> List[TradeData]:
        """
        Parse open trades data.

        Returns:
            List[TradeData]: List of open trade objects
        """
        self.log_info("Parsing open trades")

        open_trades = []

        try:
            # Find the open trades section
            open_section = self._find_section_by_header('Open Trades:')
            if not open_section:
                self.log_warning("No open trades section found")
                return open_trades

            # Find header row
            header_row = self._find_header_row(open_section)
            if not header_row:
                self.log_warning("No header row found in open trades")
                return open_trades

            headers = [safe_get_text(td) for td in header_row.find_all('td')]
            self.log_debug(f"Found open trades headers: {headers}")

            # Process data rows
            trades_data = self._process_trade_rows(header_row, headers)
            open_trades = [self._create_trade_object(trade_dict) for trade_dict in trades_data]

            self.log_info(f"Successfully parsed {len(open_trades)} open trades")

        except Exception as e:
            self.log_error(f"Error parsing open trades: {e}")

        return open_trades

    def parse_trade_statistics(self) -> TradeStatistics:
        """
        Parse trade statistics from the HTML.

        Returns:
            TradeStatistics: Structured trade statistics
        """
        self.log_info("Parsing trade statistics")

        stats = TradeStatistics()
        labels = self.config.TRADE_STATISTICS_LABELS

        try:
            # Find all rows in the document
            rows = self.soup.find_all('tr')

            for row in rows:
                # Only process rows with right alignment
                if 'right' not in str(row.get('align', '')):
                    continue

                cells = row.find_all(['td', 'th'])
                current_label = None

                for cell in cells:
                    # Check if cell contains a bold element with a label
                    bold = cell.find('b')
                    if bold:
                        label_text = safe_get_text(bold)
                        if label_text in labels:
                            current_label = label_text

                    # Check if cell is a value cell
                    if self.config.MSPT_CLASS in cell.get('class', []) and current_label:
                        value_text = safe_get_text(cell)
                        self._parse_trade_stat_value(current_label, value_text, stats)
                        current_label = None

            self.log_info("Successfully parsed trade statistics")

        except Exception as e:
            self.log_error(f"Error parsing trade statistics: {e}")

        return stats

    def _find_section_by_header(self, header_text: str) -> Optional[Any]:
        """
        Find a section by its header text.

        Args:
            header_text: Header text to search for

        Returns:
            Section row element or None
        """
        for row in self.soup.find_all('tr'):
            td = row.find('td')
            if td and td.find('b') and header_text in safe_get_text(td):
                return row
        return None

    def _find_header_row(self, section_row: Any) -> Optional[Any]:
        """
        Find the header row following a section row.

        Args:
            section_row: Section header row

        Returns:
            Header row element or None
        """
        current_row = section_row.find_next_sibling('tr')
        while current_row:
            if current_row.get('bgcolor') == self.config.HEADER_ROW_BG_COLOR:
                return current_row
            current_row = current_row.find_next_sibling('tr')
        return None

    def _process_trade_rows(self, header_row: Any, headers: List[str]) -> List[Dict[str, Any]]:
        """
        Process trade data rows.

        Args:
            header_row: Header row element
            headers: List of header names

        Returns:
            List of trade data dictionaries
        """
        trades_data = []
        current_row = header_row.find_next_sibling('tr')

        while current_row:
            cells = current_row.find_all('td')

            # Check for section boundaries
            if self._is_section_boundary(cells):
                break

            # Skip rows with wrong number of cells
            if len(cells) != len(headers):
                current_row = current_row.find_next_sibling('tr')
                continue

            # Validate first cell (ticket number)
            ticket_text = safe_get_text(cells[0])
            if 'title=' in str(cells[0]):
                ticket_text = cells[0].get_text().strip()

            if not ticket_text.isdigit():
                current_row = current_row.find_next_sibling('tr')
                continue

            # Extract trade data
            trade_data = {}
            for i, header in enumerate(headers):
                if i < len(cells):
                    value = safe_get_text(cells[i])
                    header_key = clean_header_name(header)

                    # Special handling for duplicate "Price" columns
                    # First "Price" column is entry price, second is close price
                    if header_key == 'price':
                        if i == 5:  # Entry price column
                            header_key = 'price'
                        elif i == 9:  # Close price column
                            header_key = 'close_price'
                        else:
                            header_key = f'price_{i}'  # Fallback

                    # Special handling for "Close Time" column
                    if header_key == 'close_time':
                        header_key = 'close_time'

                    # Parse numeric values for appropriate columns
                    if header in self.config.get_numeric_columns():
                        trade_data[header_key] = parse_numeric_value(value)
                    else:
                        trade_data[header_key] = value

            # Only add if valid
            if trade_data.get('ticket') and validate_trade_data(trade_data):
                trades_data.append(trade_data)

            current_row = current_row.find_next_sibling('tr')

        return trades_data

    def _is_section_boundary(self, cells: List[Any]) -> bool:
        """
        Check if the current row represents a section boundary.

        Args:
            cells: Row cells

        Returns:
            True if this is a section boundary
        """
        if len(cells) == 1 and cells[0].get('colspan'):
            return True

        if len(cells) > 0 and cells[0].find('b'):
            first_cell_text = safe_get_text(cells[0])
            section_headers = list(self.config.SECTION_HEADERS.values())
            if any(section in first_cell_text for section in section_headers):
                return True

        return False

    def _create_trade_object(self, trade_dict: Dict[str, Any]) -> TradeData:
        """
        Create a TradeData object from dictionary.

        Args:
            trade_dict: Trade data dictionary

        Returns:
            TradeData object
        """
        return TradeData(**trade_dict)

    def _parse_trade_stat_value(self, label: str, value_text: str, stats: TradeStatistics) -> None:
        """
        Parse trade statistics value based on label.

        Args:
            label: Label text
            value_text: Raw value text
            stats: TradeStatistics object to update
        """
        from utils import extract_percentage_and_count

        if label == 'Total Trades:':
            stats.total_trades = int(parse_numeric_value(value_text))
        elif label == 'Short Positions (won %):':
            stats.short_positions_count, stats.short_positions_win_rate = extract_percentage_and_count(value_text)
        elif label == 'Long Positions (won %):':
            stats.long_positions_count, stats.long_positions_win_rate = extract_percentage_and_count(value_text)
        elif label == 'Profit Trades (% of total):':
            stats.profit_trades_count, stats.profit_trades_percentage = extract_percentage_and_count(value_text)
        elif label == 'Loss trades (% of total):':
            stats.loss_trades_count, stats.loss_trades_percentage = extract_percentage_and_count(value_text)

    def print_trades_summary(self, trades: List[TradeData], title: str) -> None:
        """
        Print trades summary.

        Args:
            trades: List of TradeData objects
            title: Section title
        """
        print(f"\n{title}:")
        print("-" * 50)

        for trade in trades:
            item = trade.item.upper() if trade.item else 'N/A'
            size = trade.size
            trade_type = trade.type.upper() if trade.type else 'N/A'
            profit = trade.profit
            print(f"  Trade #{trade.ticket}: {trade_type} {size} {item} - P/L: {profit:,.2f}")

        print(f"  Total {title.split()[-1]}: {len(trades)}")
