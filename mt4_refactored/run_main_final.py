#!/usr/bin/env python3
"""
Final run of MT4 calculator main application
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

print("🚀 MT4 CALCULATOR - MAIN APPLICATION RUN")
print("=" * 80)

# Check if 10.htm exists
htm_file = parent_dir / "10.htm"
print(f"📄 Target file: {htm_file}")
print(f"📊 File exists: {htm_file.exists()}")

if not htm_file.exists():
    print("❌ ERROR: 10.htm file not found!")
    sys.exit(1)

print(f"📏 File size: {htm_file.stat().st_size} bytes")
print("\n🔄 Running main application...")

try:
    # Import and run main application
    from mt4_refactored.main import main
    print("✅ Main application imported successfully")

    # Set command line arguments
    original_argv = sys.argv.copy()
    sys.argv = ['main.py', str(htm_file)]

    print("=" * 80)

    # Run the main application
    main()

    print("=" * 80)
    print("✅ MT4 Calculator main application completed successfully!")
    print("🎯 R-Multiple calculations use CLOSED TRADES ONLY")

    # Restore original argv
    sys.argv = original_argv

except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()

except Exception as e:
    print(f"❌ Runtime error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("🎉 MAIN APPLICATION RUN COMPLETE")
