"""
Main entry point for MT4 HTML statement parser.
Provides command-line interface and example usage.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Use absolute imports with robust fallback
try:
    from mt4_refactored.core.mt4_processor import MT4Processor
    from mt4_refactored.config.settings import MT4Config
    from mt4_refactored.utils.logging_utils import setup_logging
    from mt4_refactored.core.exceptions import (
        MT4ProcessingError,
        MT4ValidationError,
        MT4FileError,
        MT4ParsingError
    )
except ImportError:
    try:
        # Try direct module imports
        from core.mt4_processor import MT4Processor
        from config.settings import MT4Config
        from utils.logging_utils import setup_logging
        from core.exceptions import (
            MT4ProcessingError,
            MT4ValidationError,
            MT4FileError,
            MT4ParsingError
        )
    except ImportError as e:
        print(f"Import error: {e}")
        # Define basic exception classes for compatibility
        class MT4ProcessingError(Exception): pass
        class MT4ValidationError(Exception): pass
        class MT4FileError(Exception): pass
        class MT4ParsingError(Exception): pass
        # Try to use the final working demo as fallback
        print("Using fallback: final_working_demo.py")
        from final_working_demo import main as fallback_main
        fallback_main()
        exit(0)


def main():
    """Main entry point function."""
    # Set up logging
    setup_logging()

    # Get file path from command line or use default
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        file_path = MT4Config.get_default_file_path()

    print(f"Processing MT4 HTML file: {file_path}")

    # Validate file exists
    if not file_path.exists():
        print(f"Error: File not found - {file_path}")
        print("Please make sure the file exists at the specified location.")
        print(f"Current working directory: {Path.cwd()}")
        return

    # Validate file extension
    if not MT4Config.validate_file_extension(file_path):
        print(f"Error: File should be an HTML file (.htm or .html)")
        return

    print("="*80)
    print("MT4 STATEMENT PROCESSOR - INDUSTRY STANDARD EDITION")
    print("="*80)

    try:
        # Create processor and process file
        processor = MT4Processor()
        data = processor.process_file(file_path)

        # Print comprehensive summary
        print("\n" + "="*80)
        print("COMPREHENSIVE DATA SUMMARY")
        print("="*80)

        # Summary statistics
        total_open_trades = len(data.open_trades)
        total_closed_trades = len(data.closed_trades)
        total_profit = data.get_total_profit()

        print("\nFILE SUMMARY:")
        print(f"  Total Open Trades: {total_open_trades}")
        print(f"  Total Closed Trades: {total_closed_trades}")
        print(f"  Total Trading Profit: {total_profit:,.2f}")

        # Performance summary
        print("\nPERFORMANCE SUMMARY:")
        if data.calculated_metrics.win_rate > 0:
            print(f"  Win Rate: {data.calculated_metrics.win_rate:.2f}%")
        if data.calculated_metrics.profit_factor > 0:
            print(f"  Profit Factor: {data.calculated_metrics.profit_factor:.2f}")
        if data.calculated_metrics.kelly_percentage > 0:
            print(f"  Kelly Criterion: {data.calculated_metrics.kelly_percentage:.2f}%")
        if data.calculated_metrics.roi_percentage != 0:
            print(f"  Return on Investment: {data.calculated_metrics.roi_percentage:.2f}%")

        # Account summary
        print("\nACCOUNT SUMMARY:")
        print(f"  Balance: {data.financial_summary.balance:,.2f}")
        print(f"  Equity: {data.financial_summary.equity:,.2f}")
        print(f"  Free Margin: {data.financial_summary.free_margin:,.2f}")

        # R-Multiple summary
        if data.r_multiple_statistics.total_valid_r_trades > 0:
            print("\n🎯 R-MULTIPLE SUMMARY:")
            print(f"  Valid R-Trades: {data.r_multiple_statistics.total_valid_r_trades}")
            print(f"  R Win Rate: {data.r_multiple_statistics.r_win_rate:.1f}%")
            print(f"  Average R-Multiple: {data.r_multiple_statistics.average_r_multiple:.3f}R")
            print(f"  R Expectancy: {data.r_multiple_statistics.r_expectancy:.3f}R")
            print(f"  R Performance Rating: {data.r_multiple_statistics.get_r_performance_rating()}")

        print("\n" + "="*80)
        print("PROCESSING COMPLETED SUCCESSFULLY!")
        print(f"Total trades processed: {data.get_total_trades()}")
        print(f"Valid R-Multiple trades: {data.r_multiple_statistics.total_valid_r_trades}")
        print(f"Total portfolio value: {data.financial_summary.balance:,.2f} {data.account_info.currency}")
        print(f"Performance rating: {data.calculated_metrics.get_comprehensive_rating()}")
        if data.r_multiple_statistics.total_valid_r_trades > 0:
            print(f"R-Multiple rating: {data.r_multiple_statistics.get_r_performance_rating()}")
        print("="*80)

    except (MT4ProcessingError, MT4ValidationError, MT4FileError, MT4ParsingError) as e:
        print(f"MT4 Processing Error: {e}")
        if hasattr(e, 'details') and e.details:
            print(f"Details: {e.details}")
        return
    except Exception as e:
        print(f"Unexpected error processing file: {e}")
        return


if __name__ == "__main__":
    main()
