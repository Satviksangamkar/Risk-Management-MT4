#!/usr/bin/env python3
"""
Main entry point for MT4 Calculator Package
Allows running the application with: python -m mt4_refactored
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mt4_refactored.final_working_demo import main

if __name__ == "__main__":
    print("🚀 MT4 CALCULATOR - PACKAGE MAIN ENTRY POINT")
    print("=" * 55)
    main()
