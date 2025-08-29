"""
Performance metrics parser for MT4 HTML statements.
Extracts performance data like profit/loss, drawdown, profit factor, etc.
"""

from typing import Dict, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from parsers.base_parser import BaseParser
from models.data_models import PerformanceMetrics
from utils.parsing_utils import parse_numeric_value, safe_get_text
from config.settings import MT4Config


class PerformanceParser(BaseParser):
    """Parser for performance metrics section."""

    def parse(self) -> PerformanceMetrics:
        """
        Parse performance metrics from the HTML.

        Returns:
            PerformanceMetrics: Structured performance data
        """
        self.log_info("Parsing performance metrics")

        performance_data = PerformanceMetrics()
        labels = self.config.PERFORMANCE_LABELS

        # Define label to attribute mapping
        label_mapping = {
            'Gross Profit:': 'gross_profit',
            'Gross Loss:': 'gross_loss',
            'Total Net Profit:': 'total_net_profit',
            'Profit Factor:': 'profit_factor',
            'Expected Payoff:': 'expected_payoff',
            'Absolute Drawdown:': 'absolute_drawdown',
            'Maximal Drawdown:': 'maximal_drawdown_amount',  # Will be handled by custom parser
            'Relative Drawdown:': 'relative_drawdown_percentage'  # Will be handled by custom parser
        }

        try:
            # Use the generic parsing method with custom value parser for drawdown values
            self.parse_labeled_data(labels, label_mapping, performance_data, self._custom_value_parser)
            self.log_info("Successfully parsed performance metrics")

        except Exception as e:
            self.log_error(f"Error parsing performance metrics: {e}")

        return performance_data

    def _custom_value_parser(self, value_text: str, label: str, data_object: PerformanceMetrics) -> float:
        """
        Custom value parser for performance metrics, handling special cases like drawdown values.

        Args:
            value_text: Raw text value
            label: Label text
            data_object: Performance data object

        Returns:
            float: Parsed value
        """
        if label == 'Maximal Drawdown:':
            self._parse_maximal_drawdown(value_text, data_object)
            return data_object.maximal_drawdown_amount
        elif label == 'Relative Drawdown:':
            self._parse_relative_drawdown(value_text, data_object)
            return data_object.relative_drawdown_percentage
        else:
            return self.parse_numeric_value(value_text)

    def _parse_maximal_drawdown(self, value_text: str, performance_data: PerformanceMetrics) -> None:
        """
        Parse maximal drawdown value which may contain both amount and percentage.

        Args:
            value_text: Text containing the drawdown value
            performance_data: Performance data object to update
        """
        if '(' in value_text and '%' in value_text:
            # Format: "40.00 (0.02%)"
            amount_part = value_text.split('(')[0].strip()
            percentage_part = value_text.split('(')[1].split('%')[0].strip()
            amount = parse_numeric_value(amount_part)
            percentage = parse_numeric_value(percentage_part)
            performance_data.maximal_drawdown_amount = amount
            performance_data.maximal_drawdown_percentage = percentage
            self.log_debug(f"Parsed maximal drawdown: {amount} ({percentage}%)")
        else:
            amount = parse_numeric_value(value_text)
            performance_data.maximal_drawdown_amount = amount
            self.log_debug(f"Parsed maximal drawdown: {amount}")

    def _parse_relative_drawdown(self, value_text: str, performance_data: PerformanceMetrics) -> None:
        """
        Parse relative drawdown value which may contain both percentage and amount.

        Args:
            value_text: Text containing the drawdown value
            performance_data: Performance data object to update
        """
        if '(' in value_text and '%' in value_text:
            if '%' in value_text.split('(')[0]:
                # Percentage comes first: "0.02% (40.00)"
                percentage_part = value_text.split('%')[0].strip()
                amount_part = value_text.split('(')[1].split(')')[0].strip()
            else:
                # Amount comes first: "40.00 (0.02%)"
                amount_part = value_text.split('(')[0].strip()
                percentage_part = value_text.split('(')[1].split('%')[0].strip()

            amount = parse_numeric_value(amount_part)
            percentage = parse_numeric_value(percentage_part)
            performance_data.relative_drawdown_amount = amount
            performance_data.relative_drawdown_percentage = percentage
            self.log_debug(f"Parsed relative drawdown: {percentage}% ({amount})")
        else:
            percentage = parse_numeric_value(value_text)
            performance_data.relative_drawdown_percentage = percentage
            self.log_debug(f"Parsed relative drawdown: {percentage}%")

    def _set_performance_value(self, label: str, value: float, performance_data: PerformanceMetrics) -> None:
        """
        Set performance value based on label.

        Args:
            label: Label text
            value: Parsed numeric value
            performance_data: Performance data object to update
        """
        label_mapping = {
            'Gross Profit:': 'gross_profit',
            'Gross Loss:': 'gross_loss',
            'Total Net Profit:': 'total_net_profit',
            'Profit Factor:': 'profit_factor',
            'Expected Payoff:': 'expected_payoff',
            'Absolute Drawdown:': 'absolute_drawdown'
        }

        if label in label_mapping:
            attr_name = label_mapping[label]
            setattr(performance_data, attr_name, value)
            self.log_debug(f"Parsed {attr_name}: {value}")

    def print_summary(self, performance_data: PerformanceMetrics) -> None:
        """
        Print performance metrics summary.

        Args:
            performance_data: PerformanceMetrics object to display
        """
        # Use generic print method with custom formatters
        field_formatters = {
            'gross_profit': 'currency',
            'gross_loss': 'currency',
            'total_net_profit': 'currency',
            'expected_payoff': 'currency',
            'absolute_drawdown': 'currency',
            'maximal_drawdown_percentage': 'percentage',
            'relative_drawdown_percentage': 'percentage'
        }
        self.print_section_summary(3, "Performance Metrics", performance_data, field_formatters)

        # Handle special drawdown formatting
        if performance_data.maximal_drawdown_amount > 0:
            if performance_data.maximal_drawdown_percentage > 0:
                print(f"  Maximal Drawdown: {performance_data.maximal_drawdown_amount:,.2f} ({performance_data.maximal_drawdown_percentage:.2f}%)")
            else:
                print(f"  Maximal Drawdown: {performance_data.maximal_drawdown_amount:,.2f}")

        if performance_data.relative_drawdown_percentage > 0:
            if performance_data.relative_drawdown_amount > 0:
                print(f"  Relative Drawdown: {performance_data.relative_drawdown_percentage:.2f}% ({performance_data.relative_drawdown_amount:,.2f})")
            else:
                print(f"  Relative Drawdown: {performance_data.relative_drawdown_percentage:.2f}%")
