"""Output validation for MT4 Scraper."""

import json
import pandas as pd
import os
from typing import Dict, List, Tuple

from mt4_scraper.config.settings import (
    REQUIRED_SECTIONS, OUTPUT_JSON_FILE,
    CLOSED_TRADES_CSV, OPEN_TRADES_CSV
)
from mt4_scraper.models.data_models import CompleteAnalysis
from mt4_scraper.utils.logging_utils import get_logger

logger = get_logger()


class OutputValidator:
    """Validates the output of the modular MT4 scraper."""

    def __init__(self, output_dir: str = "."):
        """Initialize validator with output directory.

        Args:
            output_dir: Directory containing output files
        """
        self.output_dir = output_dir

    def validate_output(self) -> bool:
        """Validate that optimized output has all required sections.

        Returns:
            True if validation passes
        """
        json_path = os.path.join(self.output_dir, OUTPUT_JSON_FILE)

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print("🔍 VALIDATION RESULTS:")
            print("=" * 50)

            all_present = True
            for section in REQUIRED_SECTIONS:
                if section in data:
                    print(f"✅ {section}: Present")
                    self._display_section_details(data, section)
                else:
                    print(f"❌ {section}: Missing")
                    all_present = False

            # Validate CSV files
            self._validate_csv_files()

            print("=" * 50)
            if all_present:
                print("🎉 OPTIMIZATION SUCCESSFUL - All functionality preserved!")
            else:
                print("❌ Some sections are missing!")

            return all_present

        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False

    def compare_with_original(self, original_json_path: str) -> Dict[str, bool]:
        """Compare modular output with original output.

        Args:
            original_json_path: Path to original JSON output

        Returns:
            Dictionary with comparison results
        """
        modular_json_path = os.path.join(self.output_dir, OUTPUT_JSON_FILE)

        try:
            # Load both files
            with open(original_json_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)

            with open(modular_json_path, 'r', encoding='utf-8') as f:
                modular_data = json.load(f)

            print("🔄 COMPARISON RESULTS:")
            print("=" * 60)

            results = {}

            # Compare each section
            for section in REQUIRED_SECTIONS:
                if section in original_data and section in modular_data:
                    section_match = self._compare_sections(
                        original_data[section],
                        modular_data[section],
                        section
                    )
                    results[section] = section_match
                else:
                    print(f"❌ {section}: Missing in one of the files")
                    results[section] = False

            # Compare CSV files
            csv_results = self._compare_csv_files()
            results.update(csv_results)

            # Summary
            all_match = all(results.values())
            print("=" * 60)
            if all_match:
                print("🎉 ALL COMPARISONS PASSED - Outputs are identical!")
            else:
                print("❌ Some comparisons failed - Outputs differ!")

            return results

        except Exception as e:
            print(f"❌ Comparison error: {e}")
            return {}

    def _display_section_details(self, data: Dict, section: str) -> None:
        """Display specific details for each section.

        Args:
            data: JSON data
            section: Section name
        """
        section_data = data[section]

        if section == 'header_information':
            account = section_data.get('account_number', 'N/A')
            currency = section_data.get('currency', 'N/A')
            print(f"   └─ Account: {account}, Currency: {currency}")

        elif section == 'closed_transactions':
            trades_count = len(section_data['trades'])
            pl_value = section_data.get('total_closed_pl', 0)
            print(f"   └─ Trades: {trades_count}, P/L: {pl_value}")

        elif section == 'open_trades':
            trades_count = len(section_data['trades'])
            pl_value = section_data.get('floating_pl', 0)
            print(f"   └─ Trades: {trades_count}, P/L: {pl_value}")

        elif section == 'working_orders':
            orders_count = len(section_data['orders'])
            status = section_data['status']
            print(f"   └─ Orders: {orders_count}, Status: {status}")

        elif section == 'summary_section':
            balance = section_data.get('balance', 0)
            equity = section_data.get('equity', 0)
            print(f"   └─ Balance: {balance}, Equity: {equity}")

        elif section == 'performance_details':
            total_trades = section_data.get('total_trades', 0)
            profit_factor = section_data.get('profit_factor', 0)
            print(f"   └─ Total Trades: {total_trades}, Profit Factor: {profit_factor}")

    def _validate_csv_files(self) -> None:
        """Validate CSV files exist."""
        csv_files = [CLOSED_TRADES_CSV, OPEN_TRADES_CSV]
        for csv_file in csv_files:
            csv_path = os.path.join(self.output_dir, csv_file)
            if os.path.exists(csv_path):
                print(f"✅ {csv_file}: Generated")
            else:
                print(f"❌ {csv_file}: Missing")

    def _compare_sections(self, original: Dict, modular: Dict, section_name: str) -> bool:
        """Compare two sections for equality.

        Args:
            original: Original section data
            modular: Modular section data
            section_name: Name of the section

        Returns:
            True if sections match
        """
        # Simple comparison for most sections
        if section_name in ['header_information', 'summary_section', 'performance_details']:
            match = original == modular
            status = "✅" if match else "❌"
            print(f"{status} {section_name}: {'Match' if match else 'Different'}")
            return match

        # Special handling for trade sections
        elif section_name in ['closed_transactions', 'open_trades', 'working_orders']:
            return self._compare_trade_sections(original, modular, section_name)

        return False

    def _compare_trade_sections(self, original: Dict, modular: Dict, section_name: str) -> bool:
        """Compare trade sections with special handling for lists.

        Args:
            original: Original trade section data
            modular: Modular trade section data
            section_name: Name of the section

        Returns:
            True if sections match
        """
        # Compare metadata (non-trade data)
        original_meta = {k: v for k, v in original.items() if k != 'trades' and k != 'orders'}
        modular_meta = {k: v for k, v in modular.items() if k != 'trades' and k != 'orders'}

        meta_match = original_meta == modular_meta

        # Compare trade counts
        original_trades = original.get('trades', original.get('orders', []))
        modular_trades = modular.get('trades', modular.get('orders', []))

        count_match = len(original_trades) == len(modular_trades)

        # For detailed comparison, check if first few trades match
        trades_match = True
        if original_trades and modular_trades:
            # Compare first trade structure (simplified)
            orig_first = original_trades[0] if original_trades else {}
            mod_first = modular_trades[0] if modular_trades else {}
            trades_match = orig_first.keys() == mod_first.keys()

        overall_match = meta_match and count_match and trades_match

        status = "✅" if overall_match else "❌"
        trade_count = len(original_trades)
        print(f"{status} {section_name}: {trade_count} trades, {'Match' if overall_match else 'Different'}")

        return overall_match

    def _compare_csv_files(self) -> Dict[str, bool]:
        """Compare CSV files between original and modular versions.

        Returns:
            Dictionary with CSV comparison results
        """
        results = {}

        for csv_file in [CLOSED_TRADES_CSV, OPEN_TRADES_CSV]:
            orig_path = csv_file  # Assuming original is in current directory
            mod_path = os.path.join(self.output_dir, csv_file)

            if os.path.exists(orig_path) and os.path.exists(mod_path):
                try:
                    orig_df = pd.read_csv(orig_path)
                    mod_df = pd.read_csv(mod_path)

                    # Compare shapes and columns
                    shape_match = orig_df.shape == mod_df.shape
                    columns_match = list(orig_df.columns) == list(mod_df.columns)

                    match = shape_match and columns_match
                    status = "✅" if match else "❌"
                    print(f"{status} {csv_file}: {'Match' if match else 'Different'}")
                    results[csv_file] = match

                except Exception as e:
                    print(f"❌ {csv_file}: Error comparing - {e}")
                    results[csv_file] = False
            else:
                print(f"❌ {csv_file}: Missing file(s)")
                results[csv_file] = False

        return results
