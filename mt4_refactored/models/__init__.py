"""
Data models module for MT4 HTML statement parser.
"""

from .data_models import (
    AccountInfo,
    FinancialSummary,
    PerformanceMetrics,
    TradeStatistics,
    TradeData,
    LargestAverageTrades,
    ConsecutiveStatistics,
    CalculatedMetrics,
    RMultipleData,
    RMultipleStatistics,
    MT4StatementData
)

# Import from calculators module
try:
    from ..calculators.r_multiple_calculator import RMultipleCalculatorResult
except ImportError:
    try:
        from calculators.r_multiple_calculator import RMultipleCalculatorResult
    except ImportError:
        # Create a dummy class if import fails
        from dataclasses import dataclass
        from typing import List

        @dataclass
        class RMultipleCalculatorResult:
            r_multiple_data: List = None
            statistics: object = None

__all__ = [
    'AccountInfo',
    'FinancialSummary',
    'PerformanceMetrics',
    'TradeStatistics',
    'TradeData',
    'LargestAverageTrades',
    'ConsecutiveStatistics',
    'CalculatedMetrics',
    'RMultipleData',
    'RMultipleStatistics',
    'MT4StatementData',
    'RMultipleCalculatorResult'
]
