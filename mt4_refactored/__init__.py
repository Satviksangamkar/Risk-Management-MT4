"""
MT4 HTML Statement Parser - Industry Standard Edition

A comprehensive, modular, and optimized parser for MT4 trading statements.
Provides structured data extraction with proper error handling, logging,
and industry-standard code organization.

Usage:
    from mt4_refactored.final_working_demo import main
    main()

    # Or run with:
    python -m mt4_refactored
"""

import sys
import os

# Add current directory to path for proper imports
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

__version__ = "2.0.0"
__author__ = "MT4 Parser Team"
__description__ = "Industry-standard MT4 HTML statement parser with service-oriented architecture"

# Import main function for easy access
from .final_working_demo import main

__all__ = [
    'main'
]
