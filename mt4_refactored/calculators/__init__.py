"""
Calculators module for MT4 statement analysis.
Provides specialized calculation engines for various trading metrics.
"""

from .r_multiple_calculator import RMultipleCalculator, RMultipleCalculatorResult

__all__ = [
    'RMultipleCalculator',
    'RMultipleCalculatorResult'
]

