#!/usr/bin/env python3
"""
Clean Main Entry Point for MT4 Calculator
No circular imports, direct execution.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Direct imports to avoid circular dependencies
from final_working_demo import main

if __name__ == "__main__":
    print("🚀 MT4 CALCULATOR - CLEAN MAIN ENTRY POINT")
    print("=" * 50)
    main()
