#!/usr/bin/env python3
"""
ULTRA-OPTIMIZED MT4 CALCULATOR - STREAMLINED MAIN ENTRY POINT
Production-ready, memory-efficient, single-pass calculation system
Combines all optimized components into a unified, professional solution
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Optimized imports with fallback
try:
    from optimized_mt4_calculator import (
        UltraFastMT4Calculator,
        display_ultra_fast_results,
        UltraFastTradeData,
        UltraFastTradeMetrics
    )
except ImportError:
    print("❌ Error: Optimized calculator not found")
    sys.exit(1)

class OptimizedMT4Processor:
    """Streamlined processor combining all optimized components."""

    def __init__(self, html_file_path: Optional[str] = None):
        """Initialize with optional file path."""
        self.html_file = Path(html_file_path or r"D:\D Drive\ULTIMATE CALCULATOR\10.htm")
        self.calculator = UltraFastMT4Calculator(str(self.html_file))

    def validate_file(self) -> bool:
        """Validate input file exists and is accessible."""
        if not self.html_file.exists():
            print(f"❌ Error: File not found - {self.html_file}")
            return False

        if not self.html_file.is_file():
            print(f"❌ Error: Path is not a file - {self.html_file}")
            return False

        # Check file size (should not be empty)
        if self.html_file.stat().st_size == 0:
            print(f"❌ Error: File is empty - {self.html_file}")
            return False

        return True

    def process_statement(self) -> Optional[UltraFastTradeMetrics]:
        """Process MT4 statement with comprehensive error handling."""
        try:
            print("🚀 INITIALIZING ULTRA-FAST MT4 PROCESSOR...")

            # Validate file
            if not self.validate_file():
                return None

            print(f"✅ File validated: {self.html_file.name} ({self.html_file.stat().st_size} bytes)")

            # Extract trades
            print("📊 EXTRACTING TRADES WITH ULTRA-FAST PARSING...")
            trades = self.calculator.extract_trades_ultra_fast()

            if not trades:
                print("❌ Error: No trades found in HTML file")
                return None

            print(f"✅ Successfully extracted {len(trades)} trades")

            # Filter and analyze
            closed_trades = [t for t in trades if t.is_closed]
            open_trades = [t for t in trades if not t.is_closed]

            print(f"✅ Identified {len(closed_trades)} closed trades")
            print(f"✅ Identified {len(open_trades)} open trades")

            if not closed_trades:
                print("⚠️ Warning: No closed trades found for analysis")
                return None

            # Calculate all metrics in single pass
            print("🧮 CALCULATING ALL 45 METRICS IN SINGLE PASS...")
            metrics = self.calculator.calculate_all_metrics_ultra_fast(trades)

            print("✅ All metrics calculated successfully")
            return metrics

        except Exception as e:
            print(f"❌ Processing error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def run_complete_analysis(self) -> bool:
        """Run complete analysis and display results."""
        try:
            # Process statement
            metrics = self.process_statement()
            if not metrics:
                return False

            # Get trade counts
            trades = self.calculator.extract_trades_ultra_fast()
            closed_trades = [t for t in trades if t.is_closed]

            # Display results
            display_ultra_fast_results(metrics, len(trades), len(closed_trades))

            return True

        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return False

def main():
    """Main entry point for optimized MT4 calculator."""
    print("=" * 100)
    print("🎯 ULTRA-OPTIMIZED MT4 STATEMENT ANALYZER")
    print("🚀 Production Version - Memory Efficient - Single Pass")
    print("=" * 100)

    # Initialize processor
    processor = OptimizedMT4Processor()

    # Run complete analysis
    success = processor.run_complete_analysis()

    if success:
        print("\n" + "=" * 100)
        print("🎉 ANALYSIS COMPLETED SUCCESSFULLY!")
        print("📊 All 45 metrics calculated and displayed")
        print("⚡ Ultra-fast processing completed")
        print("=" * 100)
        return 0
    else:
        print("\n" + "=" * 100)
        print("❌ ANALYSIS FAILED!")
        print("Please check the error messages above")
        print("=" * 100)
        return 1

if __name__ == "__main__":
    sys.exit(main())
