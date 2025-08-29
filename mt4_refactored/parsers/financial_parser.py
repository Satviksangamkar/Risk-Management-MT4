"""
Financial summary parser for MT4 HTML statements.
Extracts financial data like balance, equity, margin, P/L, etc.
"""

from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from parsers.base_parser import BaseParser
from models.data_models import FinancialSummary
from utils.parsing_utils import parse_numeric_value, safe_get_text
from config.settings import MT4Config


class FinancialParser(BaseParser):
    """Parser for financial summary section."""

    def parse(self) -> FinancialSummary:
        """
        Parse financial summary from the HTML.

        Returns:
            FinancialSummary: Structured financial data
        """
        self.log_info("Parsing financial summary")

        financial_data = FinancialSummary()
        labels = self.config.FINANCIAL_LABELS

        # Define label to attribute mapping
        label_mapping = {
            'Deposit/Withdrawal:': 'deposit_withdrawal',
            'Credit Facility:': 'credit_facility',
            'Closed Trade P/L:': 'closed_trade_pnl',
            'Floating P/L:': 'floating_pnl',
            'Margin:': 'margin',
            'Balance:': 'balance',
            'Equity:': 'equity',
            'Free Margin:': 'free_margin'
        }

        try:
            # Use the generic parsing method from base class
            self.parse_labeled_data(labels, label_mapping, financial_data)
            self.log_info("Successfully parsed financial summary")

        except Exception as e:
            self.log_error(f"Error parsing financial summary: {e}")

        return financial_data

    def print_summary(self, financial_data: FinancialSummary) -> None:
        """
        Print financial summary.

        Args:
            financial_data: FinancialSummary object to display
        """
        # Use generic print method with custom formatters for currency fields
        field_formatters = {
            'deposit_withdrawal': 'currency',
            'credit_facility': 'currency',
            'closed_trade_pnl': 'currency',
            'floating_pnl': 'currency',
            'margin': 'currency',
            'balance': 'currency',
            'equity': 'currency',
            'free_margin': 'currency'
        }
        self.print_section_summary(2, "Financial Summary", financial_data, field_formatters)
