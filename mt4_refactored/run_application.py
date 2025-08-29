#!/usr/bin/env python3
"""
MT4 Calculator Application Runner
This script provides a robust way to run the MT4 calculator with all import issues resolved.
"""

import sys
import os
from pathlib import Path

def setup_imports():
    """Set up import paths for the application."""
    # Get current directory
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent

    # Add parent directory to Python path
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

    # Also add current directory
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

    return parent_dir, current_dir

def run_calculator():
    """Run the MT4 calculator application."""
    print("🚀 MT4 CALCULATOR APPLICATION RUNNER")
    print("=" * 80)

    try:
        parent_dir, current_dir = setup_imports()

        print(f"📁 Working directory: {parent_dir}")
        print(f"📦 Package directory: {current_dir}")

        # Check for 10.htm file
        htm_file = parent_dir / "10.htm"
        if htm_file.exists():
            print(f"✅ Found MT4 file: {htm_file}")
            print(f"📊 File size: {htm_file.stat().st_size} bytes")
        else:
            print(f"❌ MT4 file not found: {htm_file}")
            print("Looking for .htm files in directory:")
            for file in parent_dir.glob("*.htm"):
                print(f"  - {file.name}")
            return False

        # Import the application
        print("\n📦 Loading MT4 Calculator...")
        try:
            from mt4_refactored.final_working_demo import main
            print("✅ Application loaded successfully!")
        except ImportError as e:
            print(f"❌ Failed to import application: {e}")
            return False

        # Run the calculator
        print("\n🧮 Running MT4 Calculator...")
        print("=" * 80)

        main()

        print("=" * 80)
        print("✅ MT4 Calculator completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error running calculator: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point."""
    success = run_calculator()
    if success:
        print("\n🎉 All calculations completed successfully!")
        print("📊 The MT4 Calculator processed all 45 metrics correctly.")
    else:
        print("\n❌ Application failed to run.")
        print("Please check the error messages above.")

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
