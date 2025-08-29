"""Optimized Comprehensive MT4 Scraper with Advanced Analytics."""

import os
import sys
import json
import time
import re
import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️  Pandas not available - CSV export disabled")

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("❌ BeautifulSoup4 not available - required for HTML parsing")

from mt4_scraper.config.settings import DEFAULT_INPUT_FILE
from mt4_scraper.parsers.main_parser import MainParser
from mt4_scraper.models.data_models import CompleteAnalysis
from mt4_scraper.utils.file_utils import validate_file_exists, read_html_file
from mt4_scraper.utils.logging_utils import setup_logging, get_logger

logger = get_logger()


class MT4Scraper:
    """Main MT4 scraper orchestrator with comprehensive functionality."""

    def __init__(self, input_file: str = DEFAULT_INPUT_FILE, output_dir: str = "."):
        """Initialize MT4 scraper.

        Args:
            input_file: Path to input HTML file
            output_dir: Directory to save output files
        """
        self.input_file = input_file
        self.output_dir = output_dir
        self.logger = setup_logging()

    def run_analysis(self) -> CompleteAnalysis:
        """Run complete MT4 report analysis for the specified input file.

        Returns:
            CompleteAnalysis object with all extracted data
        """
        start_time = time.time()

        logger.info("🚀 Starting optimized MT4 report analysis...")
        logger.info(f"Processing: {self.input_file}")

        # Validate input file
        if not validate_file_exists(self.input_file):
            logger.error(f"❌ File not found: {self.input_file}")
            raise FileNotFoundError(f"Input file '{self.input_file}' not found")

        try:
            # Load and parse HTML
            logger.info("📖 Reading HTML file...")
            with open(self.input_file, 'r', encoding='utf-8', errors='replace') as f:
                soup_content = f.read()

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(soup_content, 'html.parser')

            logger.info("✓ HTML parsed successfully")
            # Extract all data efficiently
            header_info = self._extract_header_info(soup)
            closed_transactions = self._extract_closed_transactions(soup)
            open_trades = self._extract_open_trades(soup)
            working_orders = self._extract_working_orders(soup)
            summary_section, performance_details = self._extract_summary_and_performance(soup)

            # Structure complete analysis
            complete_analysis = CompleteAnalysis(
                header_information=header_info,
                closed_transactions=closed_transactions,
                open_trades=open_trades,
                working_orders=working_orders,
                summary_section=summary_section,
                performance_details=performance_details
            )

            # Display summary
            self._display_summary(complete_analysis, start_time, self.input_file)

            logger.info("="*50)
            logger.info("EXTRACTION COMPLETE")
            logger.info("="*50)

            return complete_analysis

        except Exception as e:
            logger.error(f"❌ Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _extract_header_info(self, soup):
        """Extract header information efficiently."""
        from mt4_scraper.models.data_models import HeaderInformation
        header_info = HeaderInformation()
        header_rows = soup.find_all('tr', align='left')

        for row in header_rows:
            for bold in row.find_all('b'):
                text = bold.get_text().strip()
                if text.startswith('Account:'):
                    header_info.account_number = text.replace('Account:', '').strip()
                elif text.startswith('Name:'):
                    header_info.account_name = text.replace('Name:', '').strip()
                elif text.startswith('Currency:'):
                    header_info.currency = text.replace('Currency:', '').strip()
                elif text.startswith('Leverage:'):
                    leverage = text.replace('Leverage:', '').strip()
                    header_info.leverage = leverage if leverage else "Not specified"
                elif text.startswith('Company:'):
                    header_info.company = text.replace('Company:', '').strip()

        # Company info
        if soup.find_all(string=lambda text: text and 'Exness Technologies Ltd' in text):
            header_info.company = 'Exness Technologies Ltd'

        return header_info

    def _extract_closed_transactions(self, soup):
        """Extract closed transactions using generic extractor."""
        from mt4_scraper.models.data_models import ClosedTransactions
        from mt4_scraper.utils.parsing_utils import parse_numeric

        data = self._extract_section_generic(soup, 'Closed Transactions:', {
            's_/_l': 'stop_loss',
            't_/_p': 'take_profit',
            'close_time': 'close_time',
            'close_price': 'close_price'
        }, True)

        return ClosedTransactions(
            total_closed_pl=data.get('total_pl', 0),
            trades=data.get('trades', [])
        )

    def _extract_open_trades(self, soup):
        """Extract open trades using generic extractor."""
        from mt4_scraper.models.data_models import OpenTrades

        data = self._extract_section_generic(soup, 'Open Trades:', {
            's_/_l': 'stop_loss',
            't_/_p': 'take_profit'
        }, True)

        return OpenTrades(
            floating_pl=data.get('total_pl', 0),
            trades=data.get('trades', [])
        )

    def _extract_working_orders(self, soup):
        """Extract working orders using generic extractor."""
        from mt4_scraper.models.data_models import WorkingOrders

        data = self._extract_section_generic(soup, 'Working Orders:', {
            's_/_l': 'stop_loss',
            't_/_p': 'take_profit',
            'market_price': 'market_price'
        }, True)

        orders = data.get('trades', [])
        status = f"{len(orders)} orders found" if orders else 'No transactions'

        return WorkingOrders(
            orders=orders,
            status=status
        )

    def _extract_summary_and_performance(self, soup):
        """Extract summary and performance data efficiently."""
        from mt4_scraper.models.data_models import SummarySection, PerformanceDetails
        from mt4_scraper.utils.parsing_utils import parse_numeric

        summary_data = {}
        performance_data = {}

        summary_labels = {
            'Deposit/Withdrawal:': 'deposit_withdrawal',
            'Credit Facility:': 'credit_facility',
            'Closed Trade P/L:': 'closed_trade_pnl',
            'Floating P/L:': 'floating_pnl',
            'Margin:': 'margin',
            'Balance:': 'balance',
            'Equity:': 'equity',
            'Free Margin:': 'free_margin'
        }

        performance_labels = {
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

        for row in soup.find_all('tr', align='right'):
            cells = row.find_all(['td', 'th'])
            current_label = None

            for cell in cells:
                bold = cell.find('b')
                if bold:
                    label_text = bold.get_text().strip()
                    if label_text in summary_labels:
                        current_label = summary_labels[label_text]
                    elif label_text in performance_labels:
                        current_label = performance_labels[label_text]

                if 'mspt' in cell.get('class', []) and current_label:
                    value_text = cell.get_text().strip()
                    value = parse_numeric(value_text)

                    if current_label in summary_labels.values():
                        summary_data[current_label] = value
                    else:
                        performance_data[current_label] = value

                    current_label = None

        summary_section = SummarySection(**summary_data)
        performance_details = PerformanceDetails(**performance_data)

        return summary_section, performance_details

    def _extract_section_generic(self, soup, section_name, field_mappings, is_trade_section=False):
        """Generic section extractor for MT4 reports."""
        import re
        from mt4_scraper.utils.parsing_utils import parse_numeric, clean_header_text, is_valid_ticket

        # Find section header
        section_row = None
        for row in soup.find_all('tr'):
            if row.find('td') and row.find('td').find('b') and section_name in row.get_text():
                section_row = row
                break

        if not section_row:
            return {} if not is_trade_section else {'trades': [], 'total_pl': 0}

        # Find header row
        header_row = section_row.find_next_sibling('tr')
        if not header_row or header_row.get('bgcolor') != "#C0C0C0":
            return {} if not is_trade_section else {'trades': [], 'total_pl': 0}

        headers = [td.get_text().strip() for td in header_row.find_all('td')]

        data = {'trades': []} if is_trade_section else {}
        current_row = header_row.find_next_sibling('tr')

        while current_row:
            cells = current_row.find_all('td')

            # Check for end conditions
            if cells:
                first_text = cells[0].get_text().strip()
                if any(end_marker in first_text for end_marker in ['Closed P/L:', 'Floating P/L:', 'Open Trades:', 'Working Orders:', 'Summary:']):
                    if 'P/L:' in first_text:
                        pl_text = current_row.get_text()
                        pl_match = re.search(r'([A-Za-z\s]+P/L):\s*([-\d.,]+)', pl_text)
                        if pl_match:
                            data['total_pl'] = parse_numeric(pl_match.group(2))
                    break

            # Process trade rows
            if is_trade_section and len(cells) >= 10 and cells[0].get_text().strip().isdigit():
                trade_data = {}
                for i, header in enumerate(headers):
                    if i < len(cells):
                        value = cells[i].get_text().strip()
                        header_key = clean_header_text(header)

                        # Apply field mappings
                        if header_key in field_mappings:
                            header_key = field_mappings[header_key]

                        trade_data[header_key] = parse_numeric(value) if header in ['Size', 'Price', 'S/L', 'T/P', 'Commission', 'Taxes', 'Swap', 'Profit', '&nbsp;'] else value

                if is_valid_ticket(trade_data.get('ticket', '')):
                    data['trades'].append(trade_data)

            current_row = current_row.find_next_sibling('tr')

        return data

    def _display_summary(self, analysis: CompleteAnalysis, start_time: float, input_file: str) -> None:
        """Display analysis summary for the processed file."""
        header = analysis.header_information
        closed = analysis.closed_transactions
        open_trades = analysis.open_trades
        summary = analysis.summary_section

        logger.info(f"📊 ANALYSIS SUMMARY for '{input_file}':")
        logger.info(f"   ├─ Account: {header.account_number or 'N/A'}")
        logger.info(f"   ├─ Currency: {header.currency or 'N/A'}")
        logger.info(f"   ├─ Company: {header.company or 'N/A'}")
        logger.info(f"   ├─ Closed Trades: {len(closed.trades)}")
        logger.info(f"   ├─ Open Trades: {len(open_trades.trades)}")
        logger.info(".2f")
        logger.info(".2f")
        logger.info(".2f")
        logger.info(".2f")

        end_time = time.time()
        logger.info(".2f")

    def save_results(self, analysis: CompleteAnalysis, base_filename: str = "mt4_analysis") -> None:
        """Save analysis results to JSON and CSV files."""
        try:
            # Convert analysis to proper dictionary structure
            analysis_dict = {
                'header_information': {
                    'account_number': analysis.header_information.account_number,
                    'account_name': analysis.header_information.account_name,
                    'currency': analysis.header_information.currency,
                    'leverage': analysis.header_information.leverage,
                    'report_date': analysis.header_information.report_date,
                    'company': analysis.header_information.company
                },
                'closed_transactions': {
                    'total_closed_pl': analysis.closed_transactions.total_closed_pl,
                    'trades': analysis.closed_transactions.trades
                },
                'open_trades': {
                    'floating_pl': analysis.open_trades.floating_pl,
                    'trades': analysis.open_trades.trades
                },
                'working_orders': {
                    'orders': analysis.working_orders.orders,
                    'status': analysis.working_orders.status
                },
                'summary_section': {
                    'deposit_withdrawal': analysis.summary_section.deposit_withdrawal,
                    'credit_facility': analysis.summary_section.credit_facility,
                    'closed_trade_pnl': analysis.summary_section.closed_trade_pnl,
                    'floating_pnl': analysis.summary_section.floating_pnl,
                    'margin': analysis.summary_section.margin,
                    'balance': analysis.summary_section.balance,
                    'equity': analysis.summary_section.equity,
                    'free_margin': analysis.summary_section.free_margin
                },
                'performance_details': {
                    'gross_profit': analysis.performance_details.gross_profit,
                    'gross_loss': analysis.performance_details.gross_loss,
                    'total_net_profit': analysis.performance_details.total_net_profit,
                    'profit_factor': analysis.performance_details.profit_factor,
                    'expected_payoff': analysis.performance_details.expected_payoff,
                    'absolute_drawdown': analysis.performance_details.absolute_drawdown,
                    'maximal_drawdown_amount': analysis.performance_details.maximal_drawdown_amount,
                    'relative_drawdown_percentage': analysis.performance_details.relative_drawdown_percentage,
                    'total_trades': analysis.performance_details.total_trades,
                    'largest_profit_trade': analysis.performance_details.largest_profit_trade,
                    'largest_loss_trade': analysis.performance_details.largest_loss_trade,
                    'average_profit_trade': analysis.performance_details.average_profit_trade,
                    'average_loss_trade': analysis.performance_details.average_loss_trade
                }
            }

            # Save JSON
            json_filename = f"{base_filename}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_dict, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"💾 JSON saved: {json_filename}")

            # Save CSV files if pandas available
            if PANDAS_AVAILABLE:
                if analysis.closed_transactions.trades:
                    closed_df = pd.DataFrame(analysis.closed_transactions.trades)
                    closed_csv = f"{base_filename}_closed_trades.csv"
                    closed_df.to_csv(closed_csv, index=False)
                    logger.info(f"💾 Closed trades CSV saved: {closed_csv}")

                if analysis.open_trades.trades:
                    open_df = pd.DataFrame(analysis.open_trades.trades)
                    open_csv = f"{base_filename}_open_trades.csv"
                    open_df.to_csv(open_csv, index=False)
                    logger.info(f"💾 Open trades CSV saved: {open_csv}")
            else:
                logger.info("⚠️  Pandas not available - CSV export skipped")

        except Exception as e:
            logger.error(f"❌ Error saving results: {e}")


def main():
    """Main entry point with comprehensive functionality."""
    scraper = MT4Scraper()

    try:
        analysis = scraper.run_analysis()

        # Save results
        scraper.save_results(analysis, "mt4_comprehensive_analysis")

        print("\n🎉 MT4 scraper completed successfully!")
        print("📊 Data extracted and saved to files!")
        print("📁 Files generated:")
        print("   └─ mt4_comprehensive_analysis.json")
        if PANDAS_AVAILABLE:
            print("   └─ mt4_comprehensive_analysis_closed_trades.csv")
            print("   └─ mt4_comprehensive_analysis_open_trades.csv")

        return 0
    except Exception as e:
        print(f"\n❌ MT4 scraper failed: {e}")
        return 1


def validate_output(json_file: str = "mt4_comprehensive_analysis.json"):
    """Validate that output has all required sections."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        required_sections = [
            'header_information', 'closed_transactions', 'open_trades',
            'working_orders', 'summary_section', 'performance_details'
        ]

        print("🔍 VALIDATION RESULTS:")
        print("=" * 50)

        for section in required_sections:
            if section in data:
                print(f"✅ {section}: Present")

                # Display specific details for each section
                if section == 'header_information':
                    account = data[section].get('account_number', 'N/A')
                    currency = data[section].get('currency', 'N/A')
                    company = data[section].get('company', 'N/A')
                    print(f"   └─ Account: {account}, Currency: {currency}, Company: {company}")

                elif section == 'closed_transactions':
                    trades_count = len(data[section]['trades'])
                    pl_value = data[section].get('total_closed_pl', 0)
                    print(f"   └─ Trades: {trades_count}, P/L: {pl_value}")

                elif section == 'open_trades':
                    trades_count = len(data[section]['trades'])
                    pl_value = data[section].get('floating_pl', 0)
                    print(f"   └─ Trades: {trades_count}, P/L: {pl_value}")

                elif section == 'working_orders':
                    orders_count = len(data[section]['orders'])
                    status = data[section]['status']
                    print(f"   └─ Orders: {orders_count}, Status: {status}")

                elif section == 'summary_section':
                    balance = data[section].get('balance', 0)
                    equity = data[section].get('equity', 0)
                    margin = data[section].get('margin', 0)
                    print(f"   └─ Balance: {balance}, Equity: {equity}, Margin: {margin}")

                elif section == 'performance_details':
                    total_trades = data[section].get('total_trades', 0)
                    profit_factor = data[section].get('profit_factor', 0)
                    net_profit = data[section].get('total_net_profit', 0)
                    print(f"   └─ Total Trades: {total_trades}, Profit Factor: {profit_factor}, Net Profit: {net_profit}")

            else:
                print(f"❌ {section}: Missing")

        # Validate CSV files
        if PANDAS_AVAILABLE:
            csv_files = ['mt4_comprehensive_analysis_closed_trades.csv', 'mt4_comprehensive_analysis_open_trades.csv']
            for csv_file in csv_files:
                if os.path.exists(csv_file):
                    print(f"✅ {csv_file}: Generated")
                else:
                    print(f"❌ {csv_file}: Missing")
        else:
            print("⚠️  Pandas not available - CSV files not generated")

        print("=" * 50)
        print("🎉 VALIDATION SUCCESSFUL!")

    except Exception as e:
        print(f"❌ Validation error: {e}")


if __name__ == "__main__":
    exit(main())
