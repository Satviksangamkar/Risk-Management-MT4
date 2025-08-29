"""
Account information parser for MT4 HTML statements.
Extracts account details like number, name, currency, leverage, and report date.
"""

import re
from typing import Dict, Any, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from parsers.base_parser import BaseParser
from models.data_models import AccountInfo
from config.settings import MT4Config


class AccountParser(BaseParser):
    """Parser for account information section."""

    def parse(self) -> AccountInfo:
        """
        Parse account information from the HTML.

        Returns:
            AccountInfo: Structured account information
        """
        self.log_info("Parsing account information")

        account_info = AccountInfo()

        try:
            # Find the account info row
            account_row = self.soup.find('tr', align='left')
            if not account_row:
                self.log_warning("No account information row found")
                return account_info

            # Extract all bold text from the row
            bold_elements = account_row.find_all('b')

            for element in bold_elements:
                text = self.get_text_safely(element)

                # Extract Account number
                if text.startswith('Account:'):
                    account_info.account_number = text.replace('Account:', '').strip()
                    self.log_debug(f"Found account number: {account_info.account_number}")

                # Extract Name
                elif text.startswith('Name:'):
                    account_info.account_name = text.replace('Name:', '').strip()
                    self.log_debug(f"Found account name: {account_info.account_name}")

                # Extract Currency
                elif text.startswith('Currency:'):
                    account_info.currency = text.replace('Currency:', '').strip()
                    self.log_debug(f"Found currency: {account_info.currency}")

                # Extract Leverage (handle empty case)
                elif text.startswith('Leverage:'):
                    leverage_text = text.replace('Leverage:', '').strip()
                    if '<!--LEVERAGE-->' in str(element.parent) or not leverage_text:
                        account_info.leverage = "Not specified"
                    else:
                        account_info.leverage = leverage_text
                    self.log_debug(f"Found leverage: {account_info.leverage}")

                # Extract date/time using regex pattern
                elif re.search(self.config.DATETIME_PATTERN, text):
                    account_info.report_date = text
                    self.log_debug(f"Found report date: {account_info.report_date}")

            # Log completion
            if account_info.is_complete():
                self.log_info("Successfully parsed complete account information")
            else:
                self.log_warning("Account information parsing incomplete")

        except Exception as e:
            self.log_error(f"Error parsing account information: {e}")

        return account_info

    def print_summary(self, account_info: AccountInfo) -> None:
        """
        Print account information summary.

        Args:
            account_info: AccountInfo object to display
        """
        print("\n1. ACCOUNT INFORMATION:")
        print("-" * 50)

        if account_info.account_number:
            print(f"  Account Number: {account_info.account_number}")
        if account_info.account_name:
            print(f"  Account Name: {account_info.account_name}")
        if account_info.currency:
            print(f"  Currency: {account_info.currency}")
        if account_info.leverage:
            print(f"  Leverage: {account_info.leverage}")
        if account_info.report_date:
            print(f"  Report Date: {account_info.report_date}")
