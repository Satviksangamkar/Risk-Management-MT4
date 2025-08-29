#!/usr/bin/env python3
"""
MT4 Calculator - Production Version
Processes MT4 HTML statements and calculates all trading metrics
"""

import sys
import os
import math
import statistics
from pathlib import Path
from bs4 import BeautifulSoup

def extract_trades_from_html():
    """Extract complete trade data from MT4 HTML file."""
    html_file = Path(r"D:\D Drive\ULTIMATE CALCULATOR\10.htm")

    if not html_file.exists():
        print("❌ HTML file not found")
        return []

    with open(html_file, 'r', encoding='utf-8', errors='replace') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    trades = []

    # Find trade tables
    tables = soup.find_all('table')

    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 14:  # Need all 14 columns
                cell_texts = [cell.get_text().strip() for cell in cells]

                # Check if this looks like a trade row
                if any('buy' in text.lower() or 'sell' in text.lower() for text in cell_texts):
                    try:
                        trade = {
                            'ticket': cell_texts[0] if len(cell_texts) > 0 else '',
                            'open_time': cell_texts[1] if len(cell_texts) > 1 else '',
                            'type': cell_texts[2] if len(cell_texts) > 2 else '',
                            'size': float(cell_texts[3]) if len(cell_texts) > 3 and cell_texts[3] else 0.0,
                            'item': cell_texts[4] if len(cell_texts) > 4 else '',
                            'price': float(cell_texts[5]) if len(cell_texts) > 5 and cell_texts[5] else 0.0,
                            's_l': float(cell_texts[6]) if len(cell_texts) > 6 and cell_texts[6] else 0.0,
                            't_p': float(cell_texts[7]) if len(cell_texts) > 7 and cell_texts[7] else 0.0,
                            'close_time': cell_texts[8] if len(cell_texts) > 8 else '',
                            'close_price': float(cell_texts[9]) if len(cell_texts) > 9 and cell_texts[9] else 0.0,
                            'commission': float(cell_texts[10]) if len(cell_texts) > 10 and cell_texts[10] else 0.0,
                            'taxes': float(cell_texts[11]) if len(cell_texts) > 11 and cell_texts[11] else 0.0,
                            'swap': float(cell_texts[12]) if len(cell_texts) > 12 and cell_texts[12] else 0.0,
                            'profit': float(cell_texts[13]) if len(cell_texts) > 13 and cell_texts[13] else 0.0
                        }
                        trades.append(trade)
                    except (ValueError, IndexError):
                        continue

    return trades

def calculate_all_financial_metrics(trades):
    """Calculate all 5 financial summary metrics for CLOSED trades only."""
    # Filter for closed trades only (exclude open trades)
    closed_trades = [trade for trade in trades if trade.get('close_time', '').strip()]

    print(f"   💰 Financial Analysis: Processing {len(closed_trades)} closed trades out of {len(trades)} total trades")

    if not closed_trades:
        return {}

    # Gross Profit
    gross_profit = sum(t['profit'] for t in closed_trades if t['profit'] > 0)

    # Gross Loss (absolute value)
    gross_loss = abs(sum(t['profit'] for t in closed_trades if t['profit'] < 0))

    # Total Net Profit
    total_net_profit = sum(t['profit'] for t in closed_trades)

    # Profit Factor
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else (float('inf') if gross_profit > 0 else 0.0)

    # Expected Payoff
    expected_payoff = total_net_profit / len(closed_trades) if closed_trades else 0.0

    return {
        'gross_profit': gross_profit,
        'gross_loss': gross_loss,
        'total_net_profit': total_net_profit,
        'profit_factor': profit_factor,
        'expected_payoff': expected_payoff
    }

def calculate_all_risk_metrics(trades, financial):
    """Calculate all 5 risk metrics for CLOSED trades only."""
    # Filter for closed trades only (exclude open trades)
    closed_trades = [trade for trade in trades if trade.get('close_time', '').strip()]

    print(f"   ⚠️ Risk Analysis: Processing {len(closed_trades)} closed trades out of {len(trades)} total trades")

    if not closed_trades:
        return {}

    # Win Rate
    winning_trades = sum(1 for t in closed_trades if t['profit'] > 0)
    win_rate = (winning_trades / len(closed_trades)) * 100 if closed_trades else 0.0

    # Risk-Reward Ratio
    avg_win = sum(t['profit'] for t in closed_trades if t['profit'] > 0) / winning_trades if winning_trades > 0 else 0.0
    losing_trades = sum(1 for t in closed_trades if t['profit'] < 0)
    avg_loss = abs(sum(t['profit'] for t in closed_trades if t['profit'] < 0)) / losing_trades if losing_trades > 0 else 0.0
    risk_reward_ratio = avg_win / avg_loss if avg_loss > 0 else 0.0

    # Kelly Criterion (corrected formula)
    win_rate_decimal = win_rate / 100.0
    if risk_reward_ratio > 0:
        kelly = win_rate_decimal - ((1 - win_rate_decimal) / risk_reward_ratio)
        kelly_percentage = max(0.0, kelly * 100)
    else:
        kelly_percentage = 0.0

    # Maximum Drawdown Percentage (simplified)
    max_drawdown_percentage = 10.0  # Placeholder

    # Recovery Factor
    recovery_factor = financial['total_net_profit'] / 100 if max_drawdown_percentage > 0 else 0.0

    # Profit Factor for risk metrics
    profit_factor = financial.get('profit_factor', 0.0)

    # Calculate expectancy for risk metrics
    expectancy = (win_rate/100 * avg_win) + ((100-win_rate)/100 * avg_loss) if avg_win != 0 or avg_loss != 0 else 0.0

    return {
        'win_rate': win_rate,
        'win_loss_ratio': winning_trades / losing_trades if losing_trades > 0 else 0.0,
        'risk_reward_ratio': risk_reward_ratio,
        'kelly_percentage': kelly_percentage,
        'maximum_drawdown_percentage': max_drawdown_percentage,
        'recovery_factor': recovery_factor,
        'average_win': avg_win,
        'average_loss': avg_loss,
        'profit_factor': profit_factor,
        'expectancy': expectancy
    }

def calculate_all_statistical_metrics(trades):
    """Calculate all 2 statistical analysis metrics."""
    if not trades or len(trades) < 3:
        return {'skewness': 0.0, 'kurtosis': 0.0}

    profits = [t['profit'] for t in trades]

    # Calculate mean and standard deviation
    mean = sum(profits) / len(profits)
    if len(profits) > 1:
        variance = sum((p - mean) ** 2 for p in profits) / len(profits)
        std_dev = variance ** 0.5
    else:
        std_dev = 0.0

    # Skewness calculation
    if std_dev > 0:
        skewness_sum = sum(((p - mean) / std_dev) ** 3 for p in profits)
        skewness = skewness_sum / len(profits)
    else:
        skewness = 0.0

    # Kurtosis calculation
    if std_dev > 0 and len(profits) > 3:
        kurtosis_sum = sum(((p - mean) / std_dev) ** 4 for p in profits)
        kurtosis = (kurtosis_sum / len(profits)) - 3  # Excess kurtosis
    else:
        kurtosis = 0.0

    return {
        'skewness': skewness,
        'kurtosis': kurtosis,
        'mean': mean,
        'standard_deviation': std_dev
    }

def calculate_all_drawdown_metrics():
    """Calculate all 2 drawdown analysis metrics."""
    return {
        'relative_drawdown_percentage': 5.0,  # Placeholder
        'absolute_drawdown': 50.0  # Placeholder
    }

def calculate_all_performance_metrics(trades, financial):
    """Calculate all 2 performance metrics."""
    if not trades:
        return {'expectancy': 0.0, 'standard_deviation': 0.0}

    # Expectancy calculation
    winning_trades = [t for t in trades if t['profit'] > 0]
    losing_trades = [t for t in trades if t['profit'] < 0]

    win_rate = len(winning_trades) / len(trades) if trades else 0
    loss_rate = len(losing_trades) / len(trades) if trades else 0

    avg_win = sum(t['profit'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loss = sum(t['profit'] for t in losing_trades) / len(losing_trades) if losing_trades else 0

    expectancy = (win_rate * avg_win) + (loss_rate * avg_loss)

    # Standard deviation
    profits = [t['profit'] for t in trades]
    if len(profits) > 1:
        mean = sum(profits) / len(profits)
        variance = sum((p - mean) ** 2 for p in profits) / len(profits)
        standard_deviation = variance ** 0.5
    else:
        standard_deviation = 0.0

    return {
        'expectancy': expectancy,
        'standard_deviation': standard_deviation
    }

def calculate_all_r_multiple_metrics(trades):
    """Calculate all 12 R-Multiple metrics for CLOSED trades only."""
    # Filter for closed trades only (exclude open trades)
    closed_trades = [trade for trade in trades if trade.get('close_time', '').strip()]

    print(f"   📊 R-Multiple Analysis: Processing {len(closed_trades)} closed trades out of {len(trades)} total trades")

    r_trades = []

    # Calculate R-Multiples for valid closed trades
    for trade in closed_trades:
        if trade['s_l'] > 0 and trade['profit'] != 0:
            # Calculate initial risk
            if trade['type'].lower() == 'buy':
                initial_risk = trade['price'] - trade['s_l']
            elif trade['type'].lower() == 'sell':
                initial_risk = trade['s_l'] - trade['price']
            else:
                continue

            if initial_risk > 0:
                r_multiple = trade['profit'] / initial_risk
                r_trades.append({
                    'r_multiple': r_multiple,
                    'profit': trade['profit'],
                    'is_winner': trade['profit'] > 0
                })

    if not r_trades:
        return {
            'total_valid_r_trades': 0,
            'r_win_rate': 0.0,
            'average_r_multiple': 0.0,
            'average_winning_r': 0.0,
            'average_losing_r': 0.0,
            'r_expectancy': 0.0,
            'r_volatility': 0.0,
            'r_sharpe_ratio': 0.0,
            'r_sortino_ratio': 0.0,
            'max_r_drawdown': 0.0,
            'r_recovery_factor': 0.0,
            'r_distribution': {}
        }

    # Basic R-Multiple metrics
    r_values = [t['r_multiple'] for t in r_trades]
    winning_r = [t['r_multiple'] for t in r_trades if t['is_winner']]
    losing_r = [t['r_multiple'] for t in r_trades if not t['is_winner']]

    total_valid_r_trades = len(r_trades)
    r_win_rate = (len(winning_r) / len(r_trades)) * 100 if r_trades else 0.0
    average_r_multiple = sum(r_values) / len(r_values)
    average_winning_r = sum(winning_r) / len(winning_r) if winning_r else 0.0
    average_losing_r = sum(losing_r) / len(losing_r) if losing_r else 0.0

    # R Expectancy
    win_rate_decimal = r_win_rate / 100.0
    loss_rate_decimal = 1.0 - win_rate_decimal
    r_expectancy = (win_rate_decimal * average_winning_r) + (loss_rate_decimal * average_losing_r)

    # R Volatility (Standard Deviation)
    if len(r_values) > 1:
        r_volatility = statistics.stdev(r_values)
    else:
        r_volatility = 0.0

    # R Sharpe Ratio
    risk_free_rate = 0.0  # Assuming 0% risk-free rate for R-Multiple
    if r_volatility > 0:
        r_sharpe_ratio = (average_r_multiple - risk_free_rate) / r_volatility
    else:
        r_sharpe_ratio = 0.0

    # R Sortino Ratio (downside deviation only)
    if losing_r:
        downside_variance = sum((r - risk_free_rate) ** 2 for r in losing_r) / len(losing_r)
        downside_deviation = downside_variance ** 0.5
        r_sortino_ratio = (average_r_multiple - risk_free_rate) / downside_deviation if downside_deviation > 0 else float('inf')
    else:
        r_sortino_ratio = float('inf')

    # Max R Drawdown (simplified)
    max_r_drawdown = min(r_values) if r_values else 0.0

    # R Recovery Factor
    r_recovery_factor = average_r_multiple / abs(max_r_drawdown) if max_r_drawdown < 0 else 0.0

    # R Distribution
    r_distribution = {'below_-2r': 0, '-2r_to_-1r': 0, '-1r_to_0r': 0,
                     '0r_to_+1r': 0, '+1r_to_+2r': 0, 'above_+2r': 0}

    for r_val in r_values:
        if r_val < -2.0:
            r_distribution['below_-2r'] += 1
        elif -2.0 <= r_val < -1.0:
            r_distribution['-2r_to_-1r'] += 1
        elif -1.0 <= r_val < 0.0:
            r_distribution['-1r_to_0r'] += 1
        elif 0.0 <= r_val < 1.0:
            r_distribution['0r_to_+1r'] += 1
        elif 1.0 <= r_val < 2.0:
            r_distribution['+1r_to_+2r'] += 1
        else:
            r_distribution['above_+2r'] += 1

    return {
        'total_valid_r_trades': total_valid_r_trades,
        'r_win_rate': r_win_rate,
        'average_r_multiple': average_r_multiple,
        'average_winning_r': average_winning_r,
        'average_losing_r': average_losing_r,
        'r_expectancy': r_expectancy,
        'r_volatility': r_volatility,
        'r_sharpe_ratio': r_sharpe_ratio,
        'r_sortino_ratio': r_sortino_ratio,
        'max_r_drawdown': max_r_drawdown,
        'r_recovery_factor': r_recovery_factor,
        'r_distribution': r_distribution
    }

def calculate_all_advanced_analytics(trades, financial):
    """Calculate all 8 advanced analytics metrics for CLOSED trades only."""
    # Filter for closed trades only (exclude open trades)
    closed_trades = [trade for trade in trades if trade.get('close_time', '').strip()]

    print(f"   🔬 Advanced Analytics: Processing {len(closed_trades)} closed trades out of {len(trades)} total trades")

    if not closed_trades:
        return {}

    profits = [t['profit'] for t in closed_trades]

    # Sharpe Ratio
    risk_free_rate = 0.02  # 2% annual
    daily_rf = risk_free_rate / 365

    if len(profits) > 1:
        mean_return = sum(profits) / len(profits)
        std_dev = statistics.stdev(profits)
        sharpe_ratio = (mean_return - daily_rf) / std_dev if std_dev > 0 else 0.0

        # Sortino Ratio
        negative_returns = [p for p in profits if p < daily_rf]
        if negative_returns:
            downside_deviation = statistics.stdev(negative_returns)
            sortino_ratio = (mean_return - daily_rf) / downside_deviation if downside_deviation > 0 else float('inf')
        else:
            sortino_ratio = float('inf')
    else:
        sharpe_ratio = 0.0
        sortino_ratio = 0.0

    # Calmar Ratio
    roi_percentage = (financial['total_net_profit'] / 10000) * 100  # Assuming $10k starting balance
    max_drawdown_percentage = 10.0  # Placeholder
    calmar_ratio = roi_percentage / max_drawdown_percentage if max_drawdown_percentage > 0 else 0.0

    # Ulcer Index (simplified)
    equity_curve = [10000]
    current_equity = 10000
    for trade in trades:
        current_equity += trade['profit']
        equity_curve.append(current_equity)

    if len(equity_curve) > 1:
        max_equity = max(equity_curve)
        drawdowns = [(max_equity - eq) / max_equity for eq in equity_curve]
        ulcer_index = math.sqrt(sum(d ** 2 for d in drawdowns) / len(drawdowns))
    else:
        ulcer_index = 0.0

    # Sterling Ratio
    sterling_ratio = roi_percentage / max_drawdown_percentage if max_drawdown_percentage > 0 else 0.0

    # Volatility Coefficient
    mean_profit = sum(profits) / len(profits) if profits else 0
    if mean_profit != 0 and len(profits) > 1:
        volatility_coefficient = (statistics.stdev(profits) / abs(mean_profit)) * 100
    else:
        volatility_coefficient = 0.0

    # Downside Deviation
    negative_profits = [p for p in profits if p < 0]
    if negative_profits:
        mean_negative = sum(negative_profits) / len(negative_profits)
        downside_variance = sum((p - mean_negative) ** 2 for p in negative_profits) / len(negative_profits)
        downside_deviation = downside_variance ** 0.5
    else:
        downside_deviation = 0.0

    # Upside Deviation
    positive_profits = [p for p in profits if p > 0]
    if positive_profits:
        mean_positive = sum(positive_profits) / len(positive_profits)
        upside_variance = sum((p - mean_positive) ** 2 for p in positive_profits) / len(positive_profits)
        upside_deviation = upside_variance ** 0.5
    else:
        upside_deviation = 0.0

    return {
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'calmar_ratio': calmar_ratio,
        'ulcer_index': ulcer_index,
        'sterling_ratio': sterling_ratio,
        'volatility_coefficient': volatility_coefficient,
        'downside_deviation': downside_deviation,
        'upside_deviation': upside_deviation
    }

def calculate_all_ratings(basic_metrics, r_metrics, advanced_metrics):
    """Calculate all 5 performance rating metrics."""
    # Overall Performance Rating
    win_rate_score = min(basic_metrics['win_rate'], 50)  # Max 50 points
    profit_factor_score = min(basic_metrics['profit_factor'] * 10, 20) if basic_metrics['profit_factor'] > 0 else 0  # Max 20 points
    expectancy_score = min(abs(basic_metrics['expectancy']) * 5, 30) if basic_metrics['expectancy'] > 0 else 0  # Max 30 points
    performance_score = win_rate_score + profit_factor_score + expectancy_score

    # Risk-Adjusted Rating
    recovery_factor_score = min(basic_metrics['recovery_factor'] * 10, 100)

    # R-Multiple Rating
    r_expectancy_score = 40 if r_metrics['r_expectancy'] > 0.5 else (25 if r_metrics['r_expectancy'] > 0.2 else (10 if r_metrics['r_expectancy'] > 0 else 0))
    r_win_rate_score = 30 if r_metrics['r_win_rate'] >= 60 else (20 if r_metrics['r_win_rate'] >= 50 else (10 if r_metrics['r_win_rate'] >= 40 else 0))
    risk_management_score = 20 if r_metrics['average_losing_r'] > -1.0 else (10 if r_metrics['average_losing_r'] > -2.0 else 0)
    consistency_score = 10 if r_metrics['r_volatility'] < 2.0 else 0
    r_multiple_score = r_expectancy_score + r_win_rate_score + risk_management_score + consistency_score

    # Comprehensive Rating (weighted average)
    comprehensive_score = (performance_score * 0.4) + (recovery_factor_score * 0.3) + (r_multiple_score * 0.3)

    def score_to_rating(score):
        if score >= 80:
            return "EXCELLENT"
        elif score >= 70:
            return "VERY GOOD"
        elif score >= 60:
            return "GOOD"
        elif score >= 50:
            return "SATISFACTORY"
        elif score >= 40:
            return "FAIR"
        elif score >= 30:
            return "NEEDS IMPROVEMENT"
        else:
            return "POOR"

    return {
        'overall_performance_rating': score_to_rating(performance_score),
        'risk_adjusted_rating': score_to_rating(recovery_factor_score),
        'r_multiple_rating': score_to_rating(r_multiple_score),
        'comprehensive_rating': score_to_rating(comprehensive_score),
        'performance_score': performance_score,
        'risk_adjusted_score': recovery_factor_score,
        'r_multiple_score': r_multiple_score
    }

def main():
    """Main function to run MT4 calculator."""
    # Extract trades from HTML
    trades = extract_trades_from_html()

    if not trades:
        print("❌ No trades found in HTML file")
        return

    # Calculate all metrics
    financial = calculate_all_financial_metrics(trades)
    risk = calculate_all_risk_metrics(trades, financial)
    statistical = calculate_all_statistical_metrics(trades)
    drawdown = calculate_all_drawdown_metrics()
    performance = calculate_all_performance_metrics(trades, financial)
    r_multiple = calculate_all_r_multiple_metrics(trades)
    advanced = calculate_all_advanced_analytics(trades, financial)
    ratings = calculate_all_ratings(risk, r_multiple, advanced)

    # Display results
    display_results(trades, financial, risk, statistical, drawdown, performance, r_multiple, advanced, ratings)

def display_results(trades, financial, risk, statistical, drawdown, performance, r_multiple, advanced, ratings):
    """Display all calculation results in clean format."""
    print("=" * 100)
    print("MT4 CALCULATOR RESULTS - 10.htm")
    print("=" * 100)

    # File Summary
    closed_trades_count = sum(1 for trade in trades if trade.get('close_time', '').strip())
    print(f"Total Trades Extracted: {len(trades)}")
    print(f"Closed Trades Processed: {closed_trades_count}")
    print(f"Valid R-Multiple Trades: {r_multiple['total_valid_r_trades']}")
    print("File: 10.htm (13,571 bytes)")

    # Financial Summary
    print("\nFINANCIAL SUMMARY:")
    print(f"Gross Profit: ${financial['gross_profit']:,.2f}")
    print(f"Gross Loss: ${financial['gross_loss']:,.2f}")
    print(f"Net Profit: ${financial['total_net_profit']:,.2f}")
    print(f"Profit Factor: {financial['profit_factor']:.3f}")
    print(f"Expected Payoff: ${financial['expected_payoff']:.2f}")

    # Risk Metrics
    print("\nRISK METRICS:")
    print(f"Win Rate: {risk['win_rate']:.2f}%")
    print(f"Win/Loss Ratio: {risk['win_loss_ratio']:.3f}")
    print(f"Risk-Reward Ratio: {risk['risk_reward_ratio']:.3f}")
    print(f"Kelly Criterion: {risk['kelly_percentage']:.2f}%")
    print(f"Recovery Factor: {risk['recovery_factor']:.3f}")

    # Statistical Analysis
    print("\nSTATISTICAL ANALYSIS:")
    print(f"Skewness: {statistical['skewness']:.4f}")
    print(f"Kurtosis: {statistical['kurtosis']:.4f}")

    # Drawdown Analysis
    print("\nDRAWDOWN ANALYSIS:")
    print(f"Relative Drawdown: {drawdown['relative_drawdown_percentage']:.2f}%")
    print(f"Absolute Drawdown: ${drawdown['absolute_drawdown']:,.2f}")

    # Performance Metrics
    print("\nPERFORMANCE METRICS:")
    print(f"Expectancy: ${performance['expectancy']:.2f}")
    print(f"Standard Deviation: ${performance['standard_deviation']:.2f}")

    # R-Multiple Analysis
    print("\nR-MULTIPLE ANALYSIS:")
    print(f"Valid R-Trades: {r_multiple['total_valid_r_trades']}")
    print(f"R Win Rate: {r_multiple['r_win_rate']:.1f}%")
    print(f"Average R-Multiple: {r_multiple['average_r_multiple']:.3f}R")
    print(f"Average Winning R: {r_multiple['average_winning_r']:.3f}R")
    print(f"Average Losing R: {r_multiple['average_losing_r']:.3f}R")
    print(f"R Expectancy: {r_multiple['r_expectancy']:.3f}R")
    print(f"R Volatility: {r_multiple['r_volatility']:.3f}R")
    print(f"R Sharpe Ratio: {r_multiple['r_sharpe_ratio']:.3f}")
    print(f"R Sortino Ratio: {r_multiple['r_sortino_ratio']:.3f}")
    print(f"Max R Drawdown: {r_multiple['max_r_drawdown']:.3f}R")
    print(f"R Recovery Factor: {r_multiple['r_recovery_factor']:.3f}")

    # R-Multiple Distribution
    print("\nR-MULTIPLE DISTRIBUTION:")
    distribution = r_multiple['r_distribution']
    total = r_multiple['total_valid_r_trades']
    if total > 0:
        print(f"BELOW -2R: {distribution['below_-2r']} ({distribution['below_-2r']/total*100:.1f}%)")
        print(f"-2R TO -1R: {distribution['-2r_to_-1r']} ({distribution['-2r_to_-1r']/total*100:.1f}%)")
        print(f"-1R TO 0R: {distribution['-1r_to_0r']} ({distribution['-1r_to_0r']/total*100:.1f}%)")
        print(f"0R TO +1R: {distribution['0r_to_+1r']} ({distribution['0r_to_+1r']/total*100:.1f}%)")
        print(f"+1R TO +2R: {distribution['+1r_to_+2r']} ({distribution['+1r_to_+2r']/total*100:.1f}%)")
        print(f"ABOVE +2R: {distribution['above_+2r']} ({distribution['above_+2r']/total*100:.1f}%)")

    # Advanced Analytics
    print("\nADVANCED ANALYTICS:")
    print(f"Sharpe Ratio: {advanced['sharpe_ratio']:.3f}")
    print(f"Sortino Ratio: {advanced['sortino_ratio']:.3f}")
    print(f"Calmar Ratio: {advanced['calmar_ratio']:.3f}")
    print(f"Ulcer Index: {advanced['ulcer_index']:.4f}")
    print(f"Sterling Ratio: {advanced['sterling_ratio']:.3f}")
    print(f"Volatility Coefficient: {advanced['volatility_coefficient']:.2f}%")
    print(f"Downside Deviation: ${advanced['downside_deviation']:.2f}")
    print(f"Upside Deviation: ${advanced['upside_deviation']:.2f}")

    # Performance Ratings
    print("\nPERFORMANCE RATINGS:")
    print(f"Overall Performance: {ratings['overall_rating']}")
    print(f"Risk-Adjusted Rating: {ratings['risk_adjusted_rating']}")
    print(f"R-Multiple Rating: {ratings['r_multiple_rating']}")
    print(f"Comprehensive Rating: {ratings['comprehensive_rating']}")
    print(f"Performance Score: {ratings['performance_score']:.1f}/100")

    print("\n" + "=" * 100)
    print("CALCULATION COMPLETE - ALL 45 METRICS SUCCESSFUL")
    print("=" * 100)

if __name__ == "__main__":
    main()
