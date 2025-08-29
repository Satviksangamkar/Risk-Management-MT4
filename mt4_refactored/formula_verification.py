#!/usr/bin/env python3
"""
Formula Verification Tool for MT4 Calculator
Cross-reference all implemented formulas with industry standards
"""

import csv
import json
from pathlib import Path

def generate_formula_verification_csv():
    """Generate CSV file for formula verification"""

    formulas_data = [
        {
            "Category": "Financial Summary",
            "Formula Name": "Gross Profit",
            "Our Implementation": "Sum of all positive trade profits",
            "Standard Formula": "Σ(Profitable Trade P&L)",
            "Variables": "Profitable trades from closed_trades list",
            "Verification Status": "TO_CHECK",
            "Source": "MT4/MT5 Standard"
        },
        {
            "Category": "Financial Summary",
            "Formula Name": "Gross Loss",
            "Our Implementation": "Sum of all negative trade profits (absolute value)",
            "Standard Formula": "|Σ(Losing Trade P&L)|",
            "Variables": "Losing trades from closed_trades list",
            "Verification Status": "TO_CHECK",
            "Source": "MT4/MT5 Standard"
        },
        {
            "Category": "Financial Summary",
            "Formula Name": "Total Net Profit",
            "Our Implementation": "Gross Profit - Gross Loss",
            "Standard Formula": "Σ(All Trade P&L)",
            "Variables": "All closed trades P&L",
            "Verification Status": "TO_CHECK",
            "Source": "MT4/MT5 Standard"
        },
        {
            "Category": "Financial Summary",
            "Formula Name": "Profit Factor",
            "Our Implementation": "Gross Profit ÷ Gross Loss",
            "Standard Formula": "Gross Profit / Gross Loss",
            "Variables": "gross_profit, gross_loss from performance_metrics",
            "Verification Status": "TO_CHECK",
            "Source": "MT4/MT5 Standard"
        },
        {
            "Category": "Financial Summary",
            "Formula Name": "Expected Payoff",
            "Our Implementation": "Total Net Profit ÷ Number of trades",
            "Standard Formula": "Net Profit / Total Trades",
            "Variables": "total_net_profit / total_trades",
            "Verification Status": "TO_CHECK",
            "Source": "MT4/MT5 Standard"
        },
        {
            "Category": "Risk Metrics",
            "Formula Name": "Win Rate",
            "Our Implementation": "(Winning Trades ÷ Total Trades) × 100",
            "Standard Formula": "(Profitable Trades / Total Trades) × 100%",
            "Variables": "profit_trades_count / total_trades",
            "Verification Status": "TO_CHECK",
            "Source": "Industry Standard"
        },
        {
            "Category": "Risk Metrics",
            "Formula Name": "Sharpe Ratio",
            "Our Implementation": "(Mean Return - Risk-Free Rate) ÷ Standard Deviation",
            "Standard Formula": "E[R - Rf] / σ",
            "Variables": "mean_return, risk_free_rate, std_dev",
            "Verification Status": "TO_CHECK",
            "Source": "William Sharpe (1966)"
        },
        {
            "Category": "Risk Metrics",
            "Formula Name": "Sortino Ratio",
            "Our Implementation": "(Mean Return - Risk-Free Rate) ÷ Downside Deviation",
            "Standard Formula": "E[R - Rf] / σ_downside",
            "Variables": "mean_return, risk_free_rate, downside_deviation",
            "Verification Status": "TO_CHECK",
            "Source": "Frank Sortino (1980s)"
        },
        {
            "Category": "Risk Metrics",
            "Formula Name": "Calmar Ratio",
            "Our Implementation": "Annual Return ÷ Maximum Drawdown",
            "Standard Formula": "Annual Return / Max Drawdown",
            "Variables": "annualized_return / max_drawdown",
            "Verification Status": "TO_CHECK",
            "Source": "Terry Young (1991)"
        },
        {
            "Category": "Risk Metrics",
            "Formula Name": "Risk-Reward Ratio",
            "Our Implementation": "Average Win ÷ Average Loss",
            "Standard Formula": "Avg Profit / Avg Loss",
            "Variables": "average_win / average_loss",
            "Verification Status": "TO_CHECK",
            "Source": "Industry Standard"
        },
        {
            "Category": "Risk Metrics",
            "Formula Name": "Kelly Percentage",
            "Our Implementation": "Optimal position size based on win rate and R:R",
            "Standard Formula": "(Win Rate × (R:R + 1) - 1) ÷ R:R",
            "Variables": "win_rate, risk_reward_ratio",
            "Verification Status": "TO_CHECK",
            "Source": "John Kelly (1956)"
        },
        {
            "Category": "Risk Metrics",
            "Formula Name": "Z-Score",
            "Our Implementation": "(Sample Mean - Population Mean) ÷ Standard Error",
            "Standard Formula": "(x̄ - μ) / (σ / √n)",
            "Variables": "sample_mean, population_mean, standard_error",
            "Verification Status": "TO_CHECK",
            "Source": "Statistical Standard"
        },
        {
            "Category": "Statistical",
            "Formula Name": "Skewness",
            "Our Implementation": "Third standardized moment",
            "Standard Formula": "E[(X-μ)³/σ³]",
            "Variables": "standardized third moment",
            "Verification Status": "TO_CHECK",
            "Source": "Statistical Standard"
        },
        {
            "Category": "Statistical",
            "Formula Name": "Kurtosis",
            "Our Implementation": "Fourth standardized moment - 3",
            "Standard Formula": "E[(X-μ)⁴/σ⁴] - 3",
            "Variables": "standardized fourth moment minus 3",
            "Verification Status": "TO_CHECK",
            "Source": "Statistical Standard"
        },
        {
            "Category": "Drawdown",
            "Formula Name": "Maximum Drawdown",
            "Our Implementation": "(Max Peak - Min Trough) ÷ Max Peak × 100",
            "Standard Formula": "(Peak - Trough) / Peak × 100%",
            "Variables": "peak_equity, trough_equity",
            "Verification Status": "TO_CHECK",
            "Source": "Industry Standard"
        },
        {
            "Category": "Drawdown",
            "Formula Name": "Recovery Factor",
            "Our Implementation": "Net Profit ÷ Maximum Drawdown Amount",
            "Standard Formula": "Net Profit / Max Drawdown",
            "Variables": "net_profit / max_drawdown",
            "Verification Status": "TO_CHECK",
            "Source": "Industry Standard"
        },
        {
            "Category": "Volatility",
            "Formula Name": "Ulcer Index",
            "Our Implementation": "√(Mean of squared drawdowns)",
            "Standard Formula": "√[Σ(Drawdown²) / N]",
            "Variables": "squared drawdowns average",
            "Verification Status": "TO_CHECK",
            "Source": "Peter Martin (1987)"
        },
        {
            "Category": "Performance",
            "Formula Name": "Expectancy",
            "Our Implementation": "(Win Rate × Average Win) - (Loss Rate × Average Loss)",
            "Standard Formula": "E[P&L] = P(Win) × Avg Win - P(Loss) × Avg Loss",
            "Variables": "win_rate, avg_win, avg_loss",
            "Verification Status": "TO_CHECK",
            "Source": "Trading Standard"
        },
        {
            "Category": "Performance",
            "Formula Name": "Payoff Ratio",
            "Our Implementation": "Average Win ÷ Average Loss",
            "Standard Formula": "Avg Win / Avg Loss",
            "Variables": "average_win / average_loss",
            "Verification Status": "TO_CHECK",
            "Source": "Trading Standard"
        }
    ]

    # Save to CSV
    csv_path = Path("formula_verification.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Category", "Formula Name", "Our Implementation", "Standard Formula",
                     "Variables", "Verification Status", "Source"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(formulas_data)

    # Save to JSON as well
    json_path = Path("formula_verification.json")
    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(formulas_data, jsonfile, indent=2, ensure_ascii=False)

    print(f"✅ Formula verification files created:")
    print(f"   CSV: {csv_path.absolute()}")
    print(f"   JSON: {json_path.absolute()}")

    return formulas_data

def print_verification_summary():
    """Print summary of formulas to verify"""

    print("\n" + "="*80)
    print("📋 FORMULA VERIFICATION SUMMARY")
    print("="*80)

    categories = {
        "Financial Summary": 5,
        "Risk Metrics": 7,
        "Statistical": 2,
        "Drawdown": 2,
        "Volatility": 1,
        "Performance": 2
    }

    print("\n📊 FORMULA CATEGORIES:")
    for category, count in categories.items():
        print(f"   {category:<20}: {count} formulas")

    print(f"\n   TOTAL FORMULAS TO VERIFY: {sum(categories.values())}")

    print("\n🔍 VERIFICATION PRIORITY:")
    print("   1. Financial Summary (Core MT4 metrics)")
    print("   2. Risk Metrics (Sharpe, Sortino, Calmar)")
    print("   3. Statistical Analysis (Skewness, Kurtosis)")
    print("   4. Drawdown Metrics (Recovery Factor, Ulcer Index)")
    print("   5. Performance Ratios (Expectancy, Payoff)")

    print("\n💡 WHEN CHECKING TRADEZELLA:")
    print("   • Compare exact formula definitions")
    print("   • Note any variations or alternatives")
    print("   • Check for additional metrics we might be missing")
    print("   • Verify industry standard definitions")
    print("   • Look for academic references or sources")

if __name__ == "__main__":
    formulas = generate_formula_verification_csv()
    print_verification_summary()

    print("\n🎯 READY TO VERIFY!")
    print(f"📁 Files created in: {Path.cwd()}")
    print("📋 Open formula_verification.csv in Excel to systematically check each formula")

