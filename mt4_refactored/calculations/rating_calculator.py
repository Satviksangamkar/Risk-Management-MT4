"""
Rating Calculator for MT4 Parser
Handles performance rating calculations.
"""

from typing import Dict, Any, Optional

from ..core.interfaces import ICalculator
from ..core.exceptions import MT4CalculationError
from ..config import MT4Config
from ..models import CalculatedMetrics, RMultipleStatistics
from ..utils import LoggerMixin


class RatingCalculator(LoggerMixin, ICalculator):
    """
    Calculator for performance ratings.

    Provides comprehensive rating calculations including:
    - Overall performance rating
    - Risk-adjusted performance rating
    - R-Multiple performance rating
    - Comprehensive rating combining all metrics
    """

    def __init__(self, config: Optional[MT4Config] = None):
        """
        Initialize the rating calculator.

        Args:
            config: Configuration object
        """
        self.config = config or MT4Config()
        self.log_info("Rating Calculator initialized")

    def calculate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive performance ratings.

        Args:
            data: Dictionary containing basic_metrics and r_multiple_statistics

        Returns:
            Dict: Performance rating results

        Raises:
            MT4CalculationError: If calculation fails
        """
        try:
            basic_metrics = data.get('basic_metrics')
            r_multiple_statistics = data.get('r_multiple_statistics')

            self.log_info("Calculating comprehensive performance ratings")

            results = {}

            # Calculate individual ratings
            results['overall_performance_rating'] = self._calculate_overall_performance_rating(basic_metrics)
            results['risk_adjusted_rating'] = self._calculate_risk_adjusted_rating(basic_metrics)
            results['r_multiple_rating'] = self._calculate_r_multiple_rating(r_multiple_statistics)
            results['comprehensive_rating'] = self._calculate_comprehensive_rating(basic_metrics, r_multiple_statistics)

            # Calculate rating scores (0-100)
            results['performance_score'] = self._calculate_performance_score(basic_metrics)
            results['risk_adjusted_score'] = self._calculate_risk_adjusted_score(basic_metrics)
            results['r_multiple_score'] = self._calculate_r_multiple_score(r_multiple_statistics)

            self.log_info("Performance ratings calculation completed")
            return results

        except Exception as e:
            self.log_error(f"Performance rating calculation failed: {e}")
            raise MT4CalculationError(f"Failed to calculate performance ratings: {str(e)}", details=e) from e

    def _calculate_overall_performance_rating(self, metrics: Optional[CalculatedMetrics]) -> str:
        """Calculate overall performance rating."""
        if not metrics:
            return "INSUFFICIENT_DATA"

        score = self._calculate_performance_score(metrics)
        return self._score_to_rating(score)

    def _calculate_risk_adjusted_rating(self, metrics: Optional[CalculatedMetrics]) -> str:
        """Calculate risk-adjusted performance rating."""
        if not metrics:
            return "INSUFFICIENT_DATA"

        score = self._calculate_risk_adjusted_score(metrics)
        return self._score_to_rating(score)

    def _calculate_r_multiple_rating(self, r_stats: Optional[RMultipleStatistics]) -> str:
        """Calculate R-Multiple performance rating."""
        if not r_stats:
            return "NO_R_MULTIPLE_DATA"

        score = self._calculate_r_multiple_score(r_stats)
        return self._score_to_rating(score)

    def _calculate_comprehensive_rating(
        self,
        metrics: Optional[CalculatedMetrics],
        r_stats: Optional[RMultipleStatistics]
    ) -> str:
        """Calculate comprehensive rating combining all metrics."""
        if not metrics:
            return "INSUFFICIENT_DATA"

        # Calculate weighted score
        performance_score = self._calculate_performance_score(metrics)
        risk_score = self._calculate_risk_adjusted_score(metrics)
        r_multiple_score = self._calculate_r_multiple_score(r_stats) if r_stats else 50

        # Weight the scores (40% performance, 30% risk, 30% R-multiple)
        comprehensive_score = (performance_score * 0.4) + (risk_score * 0.3) + (r_multiple_score * 0.3)

        return self._score_to_rating(comprehensive_score)

    def _calculate_performance_score(self, metrics: Optional[CalculatedMetrics]) -> float:
        """Calculate performance score (0-100)."""
        if not metrics:
            return 0.0

        score = 0.0

        # Win rate contribution (max 50 points)
        score += min(metrics.win_rate, 50)

        # Profit factor contribution (max 20 points)
        score += min(metrics.profit_factor * 10, 20) if metrics.profit_factor > 0 else 0

        # Expectancy contribution (max 30 points)
        score += min(metrics.expectancy * 5, 30) if metrics.expectancy > 0 else 0

        return score

    def _calculate_risk_adjusted_score(self, metrics: Optional[CalculatedMetrics]) -> float:
        """Calculate risk-adjusted performance score."""
        if not metrics or metrics.recovery_factor <= 0:
            return 0.0

        return min(metrics.recovery_factor * 10, 100)

    def _calculate_r_multiple_score(self, r_stats: Optional[RMultipleStatistics]) -> float:
        """Calculate R-Multiple performance score."""
        if not r_stats or r_stats.total_valid_r_trades == 0:
            return 50.0  # Neutral score

        score = 0.0

        # R Expectancy (40% weight)
        if r_stats.r_expectancy > 0.5:
            score += 40
        elif r_stats.r_expectancy > 0.2:
            score += 25
        elif r_stats.r_expectancy > 0:
            score += 10

        # R Win Rate (30% weight)
        if r_stats.r_win_rate >= 60:
            score += 30
        elif r_stats.r_win_rate >= 50:
            score += 20
        elif r_stats.r_win_rate >= 40:
            score += 10

        # Risk Management (20% weight)
        if r_stats.average_losing_r > -1.0:
            score += 20
        elif r_stats.average_losing_r > -2.0:
            score += 10

        # Consistency (10% weight)
        if r_stats.r_volatility < 2.0:
            score += 10

        return score

    def _score_to_rating(self, score: float) -> str:
        """Convert numerical score to rating string."""
        if score >= 80:
            return "EXCELLENT"
        elif score >= 70:
            return "VERY_GOOD"
        elif score >= 60:
            return "GOOD"
        elif score >= 50:
            return "SATISFACTORY"
        elif score >= 40:
            return "FAIR"
        elif score >= 30:
            return "NEEDS_IMPROVEMENT"
        else:
            return "POOR"

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data for rating calculations."""
        if not isinstance(data, dict):
            return False

        # At least basic_metrics should be present
        if 'basic_metrics' not in data:
            return False

        return True

