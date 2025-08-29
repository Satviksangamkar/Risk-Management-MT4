"""
Main processor for MT4 HTML statement parsing.
Orchestrates all parsing operations and provides the main API.
"""

from pathlib import Path
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup

try:
    # Try relative imports for package usage
    from .config import MT4Config
    from .models import MT4StatementData, CalculatedMetrics
    from .parsers import (
        AccountParser,
        FinancialParser,
        PerformanceParser,
        TradeParser
    )
    from .calculators import RMultipleCalculator
    from .utils import (
        LoggerMixin,
        ProgressLogger,
        setup_logging,
        parse_numeric_value
    )
except ImportError:
    # Fallback to absolute imports for direct execution
    from config.settings import MT4Config
    from models.data_models import MT4StatementData, CalculatedMetrics
    from parsers.account_parser import AccountParser
    from parsers.financial_parser import FinancialParser
    from parsers.performance_parser import PerformanceParser
    from parsers.trade_parser import TradeParser
    from calculators.r_multiple_calculator import RMultipleCalculator
    from utils.logging_utils import (
        LoggerMixin,
        ProgressLogger,
        setup_logging
    )
    from utils.parsing_utils import parse_numeric_value


class MT4Processor(LoggerMixin):
    """
    Main processor for MT4 HTML statements.

    Provides a clean API for parsing MT4 trading statements and extracting
    all relevant data in a structured format.
    """

    def __init__(self, config: Optional[MT4Config] = None):
        """
        Initialize the MT4 processor.

        Args:
            config: Configuration object (uses default if None)
        """
        self.config = config or MT4Config()
        setup_logging(level=self.config.LOG_LEVEL, log_format=self.config.LOG_FORMAT)

        # Initialize parser instances (lazy loading)
        self._parsers = {}

    def _get_parser(self, parser_class, soup):
        """
        Get or create a parser instance for reuse.

        Args:
            parser_class: Parser class to instantiate
            soup: BeautifulSoup object

        Returns:
            Parser instance
        """
        parser_key = parser_class.__name__
        if parser_key not in self._parsers:
            self._parsers[parser_key] = parser_class(soup, self.config)
        return self._parsers[parser_key]

    def process_file(self, file_path: Path) -> MT4StatementData:
        """
        Process an MT4 HTML file and extract all data.

        Args:
            file_path: Path to the HTML file

        Returns:
            MT4StatementData: Complete structured data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        self.log_info(f"Processing MT4 file: {file_path}")

        # Validate file
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.config.validate_file_extension(file_path):
            raise ValueError(f"Invalid file extension. Expected: {self.config.SUPPORTED_EXTENSIONS}")

        # Read and parse HTML
        soup = self._load_html_file(file_path)

        # Create progress logger
        progress = ProgressLogger("MT4 statement processing")

        # Parse all sections
        data = MT4StatementData()

        try:
            progress.start()

            # Parse account information
            progress.log_section("Account Information")
            account_parser = self._get_parser(AccountParser, soup)
            data.account_info = account_parser.parse()
            account_parser.print_summary(data.account_info)
            progress.update()

            # Parse financial summary
            progress.log_section("Financial Summary")
            financial_parser = self._get_parser(FinancialParser, soup)
            data.financial_summary = financial_parser.parse()
            financial_parser.print_summary(data.financial_summary)
            progress.update()

            # Parse performance metrics
            progress.log_section("Performance Metrics")
            performance_parser = self._get_parser(PerformanceParser, soup)
            data.performance_metrics = performance_parser.parse()
            performance_parser.print_summary(data.performance_metrics)
            progress.update()

            # Parse trade data
            progress.log_section("Trade Data")
            trade_parser = self._get_parser(TradeParser, soup)

            # Parse trade statistics
            data.trade_statistics = trade_parser.parse_trade_statistics()

            # Parse closed trades
            data.closed_trades = trade_parser.parse_closed_trades()
            trade_parser.print_trades_summary(data.closed_trades, "7. CLOSED TRADES")

            # Parse open trades
            data.open_trades = trade_parser.parse_open_trades()
            trade_parser.print_trades_summary(data.open_trades, "8. OPEN TRADES")
            progress.update()

            # Calculate additional metrics
            progress.log_section("Calculated Metrics")
            data.calculated_metrics = self._calculate_additional_metrics(data)
            self._print_calculated_metrics(data.calculated_metrics)
            progress.update()

            # Perform R-Multiple analysis
            progress.log_section("R-Multiple Analysis")
            r_calculator = RMultipleCalculator()
            r_result = r_calculator.calculate_comprehensive_r_analysis(data.closed_trades)
            data.r_multiple_data = r_result.r_multiple_data
            data.r_multiple_statistics = r_result.statistics
            r_calculator.print_comprehensive_r_analysis(r_result)
            progress.update()

            progress.complete()
            self.log_info("Successfully processed MT4 statement with R-Multiple analysis")

        except Exception as e:
            self.log_error(f"Error processing MT4 statement: {e}")
            raise

        return data

    def _load_html_file(self, file_path: Path) -> BeautifulSoup:
        """
        Load and parse HTML file.

        Args:
            file_path: Path to HTML file

        Returns:
            BeautifulSoup: Parsed HTML object
        """
        try:
            with open(file_path, 'r', encoding=self.config.DEFAULT_ENCODING,
                     errors=self.config.FALLBACK_ENCODING) as file:
                html_content = file.read()

            self.log_info(f"Successfully loaded HTML file: {file_path}")
            self.log_debug(f"File size: {len(html_content)} characters")

            soup = BeautifulSoup(html_content, 'html.parser')
            return soup

        except Exception as e:
            self.log_error(f"Error loading HTML file {file_path}: {e}")
            raise

    def _calculate_additional_metrics(self, data: MT4StatementData) -> CalculatedMetrics:
        """
        Calculate comprehensive additional performance metrics using industry-standard formulas.
        OPTIMIZED: Single-pass calculation with cached trade statistics.

        Args:
            data: Complete MT4 statement data

        Returns:
            CalculatedMetrics: Comprehensive calculated metrics
        """
        calculated = CalculatedMetrics()

        # Extract relevant data
        financial = data.financial_summary
        performance = data.performance_metrics
        trade_stats = data.trade_statistics
        closed_trades = data.closed_trades

        try:
            # OPTIMIZATION: Calculate all trade statistics in a single pass
            trade_stats_result = self._calculate_optimized_trade_statistics(closed_trades)

            # Financial Summary (5 formulas) - Using optimized results
            calculated.gross_profit = trade_stats_result['gross_profit']
            calculated.gross_loss = trade_stats_result['gross_loss']
            calculated.total_net_profit = trade_stats_result['total_net_profit']
            calculated.profit_factor = trade_stats_result['profit_factor']
            calculated.expected_payoff = trade_stats_result['expected_payoff']

            # Risk Metrics (5 formulas) - Using optimized results
            calculated.win_rate = trade_stats_result['win_rate']
            calculated.risk_reward_ratio = trade_stats_result['risk_reward_ratio']
            calculated.kelly_percentage = self._calculate_kelly_percentage_optimized(
                calculated.win_rate, calculated.risk_reward_ratio
            )
            calculated.maximum_drawdown_percentage = performance.maximal_drawdown_percentage
            calculated.recovery_factor = self._calculate_recovery_factor_optimized(
                performance, calculated.total_net_profit
            )

            # Statistical Analysis (2 formulas) - Using optimized results
            if closed_trades:
                calculated.skewness = trade_stats_result['skewness']
                calculated.kurtosis = trade_stats_result['kurtosis']

            # Drawdown Analysis (2 formulas)
            calculated.relative_drawdown_percentage = performance.relative_drawdown_percentage
            calculated.absolute_drawdown = performance.relative_drawdown_amount

            # Performance Metrics (2 formulas) - Using optimized results
            calculated.expectancy = trade_stats_result['expectancy']
            calculated.standard_deviation = trade_stats_result['standard_deviation']

            # Additional metrics for compatibility
            calculated.roi_percentage = self._calculate_roi(financial)
            calculated.account_growth_percentage = self._calculate_account_growth(financial)
            calculated.average_trade_profit = trade_stats_result['average_win']
            calculated.average_trade_loss = trade_stats_result['average_loss']
            calculated.win_loss_ratio = trade_stats_result['win_loss_ratio']

        except Exception as e:
            self.log_error(f"Error in optimized metrics calculation: {e}")
            # Fallback to basic calculations
            try:
                calculated.win_rate = self._calculate_win_rate_new(trade_stats)
                basic_stats = self._calculate_basic_trade_stats(closed_trades)
                calculated.profit_factor = basic_stats['profit_factor']
            except Exception as basic_error:
                self.log_error(f"Basic calculations also failed: {basic_error}")

        return calculated

    def _calculate_roi(self, financial) -> float:
        """Calculate Return on Investment."""
        initial_deposit = financial.deposit_withdrawal
        closed_pnl = financial.closed_trade_pnl
        return (closed_pnl / initial_deposit) * 100 if initial_deposit > 0 else 0



    def _calculate_win_rate(self, trade_stats) -> float:
        """Calculate Win Rate."""
        profit_trades = trade_stats.profit_trades_count
        total_trades = trade_stats.total_trades
        return (profit_trades / total_trades) * 100 if total_trades > 0 else 0

    def _calculate_profit_factor(self, performance) -> float:
        """Calculate Profit Factor if not already available."""
        if performance.profit_factor == 0.0:
            gross_profit = performance.gross_profit
            gross_loss = abs(performance.gross_loss)
            return gross_profit / gross_loss if gross_loss > 0 else 0
        return performance.profit_factor

    def _calculate_account_growth(self, financial) -> float:
        """Calculate Account Growth."""
        initial_deposit = financial.deposit_withdrawal
        balance = financial.balance
        return ((balance - initial_deposit) / initial_deposit) * 100 if initial_deposit > 0 else 0

    def _calculate_drawdown_percentage(self, financial, performance) -> float:
        """Calculate Drawdown as percentage of balance."""
        max_drawdown = performance.maximal_drawdown_amount
        balance = financial.balance
        return (max_drawdown / balance) * 100 if balance > 0 else 0

    def _calculate_max_drawdown_percentage(self, financial, performance) -> float:
        """Calculate Maximum Drawdown as percentage."""
        return performance.maximal_drawdown_percentage

    def _calculate_win_loss_ratio(self, trade_stats) -> float:
        """Calculate Win/Loss Ratio."""
        if trade_stats.loss_trades_count > 0:
            return trade_stats.profit_trades_count / trade_stats.loss_trades_count
        return 0.0

    def _calculate_payoff_ratio(self, performance) -> float:
        """Calculate Payoff Ratio (Average Win / Average Loss)."""
        # Use gross_profit and gross_loss to calculate average win/loss
        # We need to estimate the number of winning/losing trades from the data
        if performance.gross_loss != 0:
            # Estimate number of losing trades from gross loss and expected payoff
            avg_loss_estimate = abs(performance.expected_payoff) * 2  # Rough estimate
            if avg_loss_estimate > 0:
                avg_win = performance.gross_profit
                avg_loss = abs(performance.gross_loss)
                return avg_win / avg_loss if avg_loss > 0 else 0.0
        return 0.0

    def _calculate_risk_reward_ratio(self, closed_trades) -> float:
        """Calculate Risk-Reward Ratio."""
        if not closed_trades:
            return 0.0

        total_risk = 0.0
        total_reward = 0.0

        for trade in closed_trades:
            if trade.profit > 0:
                # For winning trades, risk is the stop loss distance
                risk = abs(trade.price - trade.s_l) if trade.s_l > 0 else abs(trade.profit)
                reward = trade.profit
            else:
                # For losing trades, risk is the loss amount
                risk = abs(trade.profit)
                reward = 0.0

            total_risk += risk
            total_reward += reward

        return total_reward / total_risk if total_risk > 0 else 0.0

    def _calculate_average_risk_reward_ratio(self, closed_trades) -> float:
        """Calculate Average Risk-Reward Ratio per trade."""
        if not closed_trades:
            return 0.0

        rr_ratios = []
        for trade in closed_trades:
            if trade.s_l > 0:  # Has stop loss
                risk = abs(trade.price - trade.s_l)
                if trade.profit > 0:
                    reward = trade.profit
                    rr_ratios.append(reward / risk if risk > 0 else 0.0)
                else:
                    rr_ratios.append(0.0)  # No reward on losing trades

        return sum(rr_ratios) / len(rr_ratios) if rr_ratios else 0.0

    def _calculate_sharpe_ratio(self, closed_trades, financial) -> float:
        """Calculate Sharpe Ratio using daily returns."""
        if not closed_trades:
            return 0.0

        # Calculate daily returns from trade profits
        profits = [trade.profit for trade in closed_trades]
        if not profits:
            return 0.0

        # Use risk-free rate of 0.02 (2%) annualized, convert to daily
        risk_free_daily = 0.02 / 365

        # Calculate mean return and standard deviation
        mean_return = sum(profits) / len(profits)
        variance = sum((p - mean_return) ** 2 for p in profits) / len(profits)
        std_dev = variance ** 0.5

        # Sharpe ratio = (Mean return - Risk-free rate) / Standard deviation
        return (mean_return - risk_free_daily) / std_dev if std_dev > 0 else 0.0

    def _calculate_sortino_ratio(self, closed_trades, financial) -> float:
        """Calculate Sortino Ratio (downside deviation only)."""
        if not closed_trades:
            return 0.0

        profits = [trade.profit for trade in closed_trades]
        if not profits:
            return 0.0

        # Calculate downside deviation (only negative returns)
        negative_returns = [p for p in profits if p < 0]
        if not negative_returns:
            return float('inf')  # No downside risk

        mean_return = sum(profits) / len(profits)
        risk_free_daily = 0.02 / 365

        # Downside deviation
        downside_variance = sum((min(0, p - risk_free_daily)) ** 2 for p in profits) / len(profits)
        downside_deviation = downside_variance ** 0.5

        return (mean_return - risk_free_daily) / downside_deviation if downside_deviation > 0 else float('inf')

    def _calculate_calmar_ratio(self, roi_percentage, max_drawdown_percentage) -> float:
        """Calculate Calmar Ratio (Annual return / Max drawdown)."""
        if max_drawdown_percentage <= 0:
            return 0.0
        return roi_percentage / max_drawdown_percentage

    def _calculate_recovery_factor(self, performance) -> float:
        """Calculate Recovery Factor (Net profit / Max drawdown)."""
        if performance.maximal_drawdown_amount <= 0:
            return 0.0
        return performance.total_net_profit / performance.maximal_drawdown_amount

    def _calculate_average_trade_profit(self, closed_trades) -> float:
        """Calculate Average Profitable Trade."""
        profitable_trades = [trade.profit for trade in closed_trades if trade.profit > 0]
        return sum(profitable_trades) / len(profitable_trades) if profitable_trades else 0.0

    def _calculate_average_trade_loss(self, closed_trades) -> float:
        """Calculate Average Losing Trade."""
        losing_trades = [trade.profit for trade in closed_trades if trade.profit < 0]
        return sum(losing_trades) / len(losing_trades) if losing_trades else 0.0

    def _calculate_consecutive_statistics(self, closed_trades) -> dict:
        """Calculate consecutive wins and losses statistics."""
        if not closed_trades:
            return {
                'max_win_streak_amount': 0.0,
                'max_loss_streak_amount': 0.0,
                'avg_win_streak': 0.0,
                'avg_loss_streak': 0.0
            }

        win_streaks = []
        loss_streaks = []
        current_win_streak = 0
        current_loss_streak = 0
        current_win_amount = 0.0
        current_loss_amount = 0.0

        for trade in closed_trades:
            if trade.profit > 0:
                if current_loss_streak > 0:
                    loss_streaks.append((current_loss_streak, current_loss_amount))
                    current_loss_streak = 0
                    current_loss_amount = 0.0

                current_win_streak += 1
                current_win_amount += trade.profit
            elif trade.profit < 0:
                if current_win_streak > 0:
                    win_streaks.append((current_win_streak, current_win_amount))
                    current_win_streak = 0
                    current_win_amount = 0.0

                current_loss_streak += 1
                current_loss_amount += trade.profit

        # Handle final streaks
        if current_win_streak > 0:
            win_streaks.append((current_win_streak, current_win_amount))
        if current_loss_streak > 0:
            loss_streaks.append((current_loss_streak, current_loss_amount))

        max_win_streak_amount = max([amount for _, amount in win_streaks], default=0.0)
        max_loss_streak_amount = min([amount for _, amount in loss_streaks], default=0.0)

        avg_win_streak = sum(count for count, _ in win_streaks) / len(win_streaks) if win_streaks else 0.0
        avg_loss_streak = sum(count for count, _ in loss_streaks) / len(loss_streaks) if loss_streaks else 0.0

        return {
            'max_win_streak_amount': max_win_streak_amount,
            'max_loss_streak_amount': max_loss_streak_amount,
            'avg_win_streak': avg_win_streak,
            'avg_loss_streak': avg_loss_streak
        }

    # ===== OPTIMIZED CALCULATION METHODS =====

    def _calculate_optimized_trade_statistics(self, closed_trades) -> dict:
        """
        OPTIMIZED: Calculate all trade statistics in a single pass through the data.

        This method eliminates redundant iterations and provides all trade-related
        metrics in one efficient calculation.

        Returns:
            dict: All calculated trade statistics
        """
        if not closed_trades:
            return self._get_empty_trade_stats()

        # Single pass through all trades - collect all data at once
        profits = []
        winning_trades = []
        losing_trades = []
        total_profit_sum = 0.0
        gross_profit_sum = 0.0
        gross_loss_sum = 0.0

        for trade in closed_trades:
            profit = trade.profit
            profits.append(profit)
            total_profit_sum += profit

            if profit > 0:
                winning_trades.append(profit)
                gross_profit_sum += profit
            elif profit < 0:
                losing_trades.append(abs(profit))  # Store absolute value for avg loss
                gross_loss_sum += abs(profit)

        # Calculate basic metrics
        total_trades = len(closed_trades)
        win_count = len(winning_trades)
        loss_count = len(losing_trades)

        # Financial Summary
        gross_profit = gross_profit_sum
        gross_loss = gross_loss_sum
        total_net_profit = total_profit_sum
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else (float('inf') if gross_profit > 0 else 0.0)
        expected_payoff = total_net_profit / total_trades if total_trades > 0 else 0.0

        # Risk Metrics
        win_rate = (win_count / total_trades) * 100 if total_trades > 0 else 0.0
        win_loss_ratio = win_count / loss_count if loss_count > 0 else 0.0

        # Risk-Reward Ratio
        avg_win = sum(winning_trades) / len(winning_trades) if winning_trades else 0.0
        avg_loss = sum(losing_trades) / len(losing_trades) if losing_trades else 0.0
        risk_reward_ratio = avg_win / avg_loss if avg_loss > 0 else 0.0

        # Statistical calculations (using collected profits)
        mean = total_net_profit / total_trades if total_trades > 0 else 0.0

        # Calculate variance and standard deviation
        if total_trades > 1:
            variance = sum((p - mean) ** 2 for p in profits) / total_trades
            std_dev = variance ** 0.5
        else:
            variance = 0.0
            std_dev = 0.0



        # Skewness calculation
        skewness = 0.0
        if std_dev > 0 and total_trades >= 3:
            third_moment = sum(((p - mean) / std_dev) ** 3 for p in profits) / total_trades
            skewness = third_moment

        # Kurtosis calculation
        kurtosis = 0.0
        if std_dev > 0 and total_trades >= 4:
            fourth_moment = sum(((p - mean) / std_dev) ** 4 for p in profits) / total_trades
            kurtosis = fourth_moment - 3  # Excess kurtosis

        # Expectancy calculation
        expectancy = 0.0
        if total_trades > 0:
            win_rate_decimal = win_rate / 100.0
            loss_rate_decimal = (loss_count / total_trades) if total_trades > 0 else 0.0
            expectancy = (win_rate_decimal * avg_win) - (loss_rate_decimal * avg_loss)

        return {
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'total_net_profit': total_net_profit,
            'profit_factor': profit_factor,
            'expected_payoff': expected_payoff,
            'win_rate': win_rate,
            'win_loss_ratio': win_loss_ratio,
            'risk_reward_ratio': risk_reward_ratio,
            'average_win': avg_win,
            'average_loss': avg_loss,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'expectancy': expectancy,
            'standard_deviation': std_dev,
            'total_trades': total_trades,
            'win_count': win_count,
            'loss_count': loss_count
        }

    def _get_empty_trade_stats(self) -> dict:
        """Return empty trade statistics dictionary."""
        return {
            'gross_profit': 0.0,
            'gross_loss': 0.0,
            'total_net_profit': 0.0,
            'profit_factor': 0.0,
            'expected_payoff': 0.0,
            'win_rate': 0.0,
            'win_loss_ratio': 0.0,
            'risk_reward_ratio': 0.0,
            'average_win': 0.0,
            'average_loss': 0.0,
            'skewness': 0.0,
            'kurtosis': 0.0,
            'expectancy': 0.0,
            'standard_deviation': 0.0,
            'total_trades': 0,
            'win_count': 0,
            'loss_count': 0
        }

    def _calculate_basic_trade_stats(self, closed_trades) -> dict:
        """Basic trade statistics for fallback calculations."""
        if not closed_trades:
            return {'profit_factor': 0.0}

        profits = [trade.profit for trade in closed_trades]
        gross_profit = sum(p for p in profits if p > 0)
        gross_loss = abs(sum(p for p in profits if p < 0))

        return {
            'profit_factor': gross_profit / gross_loss if gross_loss > 0 else 0.0
        }

    def _calculate_kelly_percentage_optimized(self, win_rate: float, risk_reward_ratio: float) -> float:
        """Calculate Kelly Criterion: W - ((1-W) / R) - OPTIMIZED"""
        if risk_reward_ratio <= 0 or win_rate <= 0 or win_rate >= 100:
            return 0.0

        win_rate_decimal = win_rate / 100.0
        kelly = win_rate_decimal - ((1 - win_rate_decimal) / risk_reward_ratio)
        return max(0.0, kelly * 100)  # Convert to percentage

    def _calculate_recovery_factor_optimized(self, performance, total_net_profit: float) -> float:
        """Calculate Recovery Factor: Net Profit / Max Drawdown - OPTIMIZED"""
        if performance.maximal_drawdown_amount <= 0:
            return 0.0
        return total_net_profit / performance.maximal_drawdown_amount

    # LEGACY METHODS (kept for backward compatibility but optimized)

    def _calculate_gross_profit(self, closed_trades) -> float:
        """Calculate Gross Profit: Σ(Pi where Pi > 0) - LEGACY (use optimized version)"""
        if not closed_trades:
            return 0.0
        return sum(trade.profit for trade in closed_trades if trade.profit > 0)

    # Removed redundant methods - all calculations now handled by _calculate_optimized_trade_statistics()

    def _calculate_expectancy_value(self, closed_trades) -> float:
        """Calculate Expectancy Value per trade."""
        if not closed_trades:
            return 0.0

        total_profit = sum(trade.profit for trade in closed_trades)
        return total_profit / len(closed_trades)



    def _calculate_volatility_percentage(self, closed_trades) -> float:
        """Calculate Volatility as coefficient of variation."""
        if not closed_trades:
            return 0.0

        profits = [trade.profit for trade in closed_trades]
        if not profits:
            return 0.0

        mean = sum(profits) / len(profits)
        if mean == 0:
            return 0.0

        variance = sum((p - mean) ** 2 for p in profits) / len(profits)
        std_dev = variance ** 0.5

        return (std_dev / abs(mean)) * 100  # Coefficient of variation as percentage

    def _calculate_downside_deviation(self, closed_trades) -> float:
        """Calculate Downside Deviation (only negative returns)."""
        if not closed_trades:
            return 0.0

        profits = [trade.profit for trade in closed_trades]
        negative_profits = [p for p in profits if p < 0]

        if not negative_profits:
            return 0.0

        mean_negative = sum(negative_profits) / len(negative_profits)
        variance = sum((p - mean_negative) ** 2 for p in negative_profits) / len(negative_profits)
        return variance ** 0.5

    def _calculate_upside_deviation(self, closed_trades) -> float:
        """Calculate Upside Deviation (only positive returns)."""
        if not closed_trades:
            return 0.0

        profits = [trade.profit for trade in closed_trades]
        positive_profits = [p for p in profits if p > 0]

        if not positive_profits:
            return 0.0

        mean_positive = sum(positive_profits) / len(positive_profits)
        variance = sum((p - mean_positive) ** 2 for p in positive_profits) / len(positive_profits)
        return variance ** 0.5

    def _calculate_skewness(self, closed_trades) -> float:
        """Calculate Skewness of return distribution."""
        if not closed_trades:
            return 0.0

        profits = [trade.profit for trade in closed_trades]
        if len(profits) < 3:
            return 0.0

        mean = sum(profits) / len(profits)
        variance = sum((p - mean) ** 2 for p in profits) / len(profits)
        std_dev = variance ** 0.5

        if std_dev == 0:
            return 0.0

        # Third moment
        third_moment = sum(((p - mean) / std_dev) ** 3 for p in profits) / len(profits)
        return third_moment

    def _calculate_kurtosis(self, closed_trades) -> float:
        """Calculate Kurtosis of return distribution."""
        if not closed_trades:
            return 0.0

        profits = [trade.profit for trade in closed_trades]
        if len(profits) < 4:
            return 0.0

        mean = sum(profits) / len(profits)
        variance = sum((p - mean) ** 2 for p in profits) / len(profits)
        std_dev = variance ** 0.5

        if std_dev == 0:
            return 0.0

        # Fourth moment
        fourth_moment = sum(((p - mean) / std_dev) ** 4 for p in profits) / len(profits)
        return fourth_moment - 3  # Excess kurtosis

    def _calculate_ulcer_index(self, closed_trades) -> float:
        """Calculate Ulcer Index for drawdown measurement."""
        if not closed_trades:
            return 0.0

        # Simulate equity curve
        equity_curve = []
        current_equity = 10000  # Starting equity

        for trade in closed_trades:
            current_equity += trade.profit
            equity_curve.append(current_equity)

        if len(equity_curve) < 2:
            return 0.0

        # Calculate drawdowns
        max_equity = equity_curve[0]
        drawdowns = []

        for equity in equity_curve:
            max_equity = max(max_equity, equity)
            drawdown = (max_equity - equity) / max_equity
            drawdowns.append(drawdown)

        # Ulcer Index = sqrt(mean of squared drawdowns)
        mean_squared_drawdown = sum(d ** 2 for d in drawdowns) / len(drawdowns)
        return mean_squared_drawdown ** 0.5

    def _calculate_sterling_ratio(self, roi_percentage, max_drawdown_percentage) -> float:
        """Calculate Sterling Ratio (Average annual return / Average drawdown)."""
        if max_drawdown_percentage <= 0:
            return 0.0
        return roi_percentage / max_drawdown_percentage

    def _print_calculated_metrics(self, metrics: CalculatedMetrics) -> None:
        """
        Print comprehensive calculated metrics summary with industry-standard formatting.

        Args:
            metrics: CalculatedMetrics object to display
        """
        print("\n" + "="*80)
        print("COMPREHENSIVE CALCULATED METRICS - UPDATED FORMULAS")
        print("="*80)

        # Define field formatters and groupings for better organization
        metric_groups = {
            "FINANCIAL SUMMARY (5 formulas)": {
                'gross_profit': ('currency', 'Gross Profit'),
                'gross_loss': ('currency', 'Gross Loss'),
                'total_net_profit': ('currency', 'Total Net Profit'),
                'profit_factor': ('ratio', 'Profit Factor'),
                'expected_payoff': ('currency', 'Expected Payoff')
            },
            "RISK METRICS (5 formulas)": {
                'win_rate': ('percentage', 'Win Rate'),
                'risk_reward_ratio': ('ratio', 'Risk-Reward Ratio'),
                'kelly_percentage': ('percentage', 'Kelly Criterion'),
                'maximum_drawdown_percentage': ('percentage', 'Maximum Drawdown'),
                'recovery_factor': ('decimal', 'Recovery Factor')
            },
            "STATISTICAL ANALYSIS (2 formulas)": {
                'skewness': ('decimal', 'Skewness'),
                'kurtosis': ('decimal', 'Kurtosis')
            },
            "DRAWDOWN ANALYSIS (2 formulas)": {
                'relative_drawdown_percentage': ('percentage', 'Relative Drawdown'),
                'absolute_drawdown': ('currency', 'Absolute Drawdown')
            },
            "PERFORMANCE METRICS (2 formulas)": {
                'expectancy': ('currency', 'Expectancy'),
                'standard_deviation': ('currency', 'Standard Deviation')
            },
            "ADDITIONAL METRICS": {
                'roi_percentage': ('percentage', 'Return on Investment'),
                'account_growth_percentage': ('percentage', 'Account Growth'),
                'average_trade_profit': ('currency', 'Average Winning Trade'),
                'average_trade_loss': ('currency', 'Average Losing Trade'),
                'win_loss_ratio': ('ratio', 'Win/Loss Ratio')
            }
        }

        for group_name, group_metrics in metric_groups.items():
            print(f"\n{group_name}:")
            print("-" * 50)

            has_values = False
            for attr_name, (formatter, display_name) in group_metrics.items():
                if hasattr(metrics, attr_name):
                    value = getattr(metrics, attr_name)

                    # Skip None, zero, or invalid values
                    if value is None or value == "" or (isinstance(value, (int, float)) and value == 0):
                        continue

                    # Skip infinite values for ratios
                    if isinstance(value, float) and (value == float('inf') or value == float('-inf')):
                        continue

                    has_values = True

                    # Format value based on type
                    if formatter == 'percentage':
                        print(f"  {display_name}: {value:.2f}%")
                    elif formatter == 'ratio':
                        if value >= 1:
                            print(f"  {display_name}: {value:.2f}:1")
                        else:
                            print(f"  {display_name}: 1:{1/value:.2f}")
                    elif formatter == 'currency':
                        print(f"  {display_name}: {value:,.2f}")
                    elif formatter == 'decimal':
                        if abs(value) >= 100:
                            print(f"  {display_name}: {value:,.2f}")
                        elif abs(value) >= 1:
                            print(f"  {display_name}: {value:.2f}")
                        else:
                            print(f"  {display_name}: {value:.4f}")
                    else:
                        print(f"  {display_name}: {value}")

            if not has_values:
                print("  No data available for this section")

        # Performance Rating
        print(f"\nOVERALL PERFORMANCE RATING:")
        print("-" * 50)
        rating = metrics.get_comprehensive_rating()
        print(f"  Rating: {rating}")

        if rating != "NEEDS IMPROVEMENT":
            print("  System is performing well with corrected formulas")
        else:
            print("  Consider reviewing trading strategy")

        print("\n" + "="*80)

    def get_summary_report(self, data: MT4StatementData) -> Dict[str, Any]:
        """
        Generate a comprehensive summary report including R-Multiple analysis.

        Args:
            data: Complete MT4 statement data

        Returns:
            Dict containing summary information
        """
        report = {
            'file_info': {
                'total_trades': data.get_total_trades(),
                'closed_trades': len(data.closed_trades),
                'open_trades': len(data.open_trades),
                'total_profit': data.get_total_profit()
            },
            'performance': {
                'win_rate': data.calculated_metrics.win_rate,
                'profit_factor': data.performance_metrics.profit_factor,
                'roi': data.calculated_metrics.roi_percentage,
                'max_drawdown': data.performance_metrics.maximal_drawdown_percentage
            },
            'account': {
                'balance': data.financial_summary.balance,
                'equity': data.financial_summary.equity,
                'free_margin': data.financial_summary.free_margin
            }
        }

        # Add R-Multiple analysis if available
        if data.r_multiple_statistics.total_valid_r_trades > 0:
            report['r_multiple'] = {
                'valid_r_trades': data.r_multiple_statistics.total_valid_r_trades,
                'r_win_rate': data.r_multiple_statistics.r_win_rate,
                'average_r_multiple': data.r_multiple_statistics.average_r_multiple,
                'r_expectancy': data.r_multiple_statistics.r_expectancy,
                'r_sharpe_ratio': data.r_multiple_statistics.r_sharpe_ratio,
                'r_sortino_ratio': data.r_multiple_statistics.r_sortino_ratio,
                'max_r_drawdown': data.r_multiple_statistics.max_r_drawdown,
                'r_performance_rating': data.r_multiple_statistics.get_r_performance_rating()
            }

        return report
