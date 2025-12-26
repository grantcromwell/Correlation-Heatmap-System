#!/usr/bin/env python3
"""Backtest script for major financial instruments."""
import asyncio
import json
import sys
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from typing import Dict, List

import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.backtest_engine import BacktestEngine
from app.services.correlation_calculator import CorrelationCalculator
from app.services.data_fetcher import DataFetcher


MAJOR_INSTRUMENTS = {
    "equity": [
        "AAPL",  # Apple
        "MSFT",  # Microsoft
        "GOOGL",  # Google
        "AMZN",  # Amazon
        "TSLA",  # Tesla
        "META",  # Meta
        "NVDA",  # NVIDIA
        "JPM",  # JPMorgan
        "V",  # Visa
        "JNJ",  # Johnson & Johnson
    ],
    "crypto": [
        "BTC-USD",  # Bitcoin
        "ETH-USD",  # Ethereum
        "BNB-USD",  # Binance Coin
        "SOL-USD",  # Solana
        "ADA-USD",  # Cardano
    ],
    "forex": [
        "EURUSD=X",  # Euro/USD (yfinance format)
        "GBPUSD=X",  # GBP/USD
        "USDJPY=X",  # USD/JPY
        "AUDUSD=X",  # AUD/USD
        "USDCAD=X",  # USD/CAD
    ],
}


async def fetch_all_data(data_fetcher: DataFetcher, start_date: datetime, end_date: datetime) -> Dict[str, pd.DataFrame]:
    """Fetch historical data for all major instruments."""
    import asyncio
    all_data = {}
    
    print(f"Fetching data from {start_date.date()} to {end_date.date()}...")
    
    for asset_class, symbols in MAJOR_INSTRUMENTS.items():
        print(f"  Fetching {asset_class} data for {len(symbols)} instruments...")
        data = await data_fetcher.fetch_historical_prices(symbols, start_date, end_date, asset_class)
        all_data.update(data)
        print(f"    Retrieved {len(data)}/{len(symbols)} instruments")
        
        # Small delay between asset classes to avoid rate limiting
        if asset_class != list(MAJOR_INSTRUMENTS.keys())[-1]:  # Don't delay after last class
            await asyncio.sleep(0.5)  # 500ms delay between asset classes
    
    return all_data


def calculate_correlations(price_data: Dict[str, pd.DataFrame]) -> List[Dict]:
    """Calculate correlations between all pairs."""
    calculator = CorrelationCalculator()
    correlations = []
    
    symbols = list(price_data.keys())
    print(f"\nCalculating correlations for {len(symbols)} instruments ({len(list(combinations(symbols, 2)))} pairs)...")
    
    for symbol_a, symbol_b in combinations(symbols, 2):
        try:
            df_a = price_data[symbol_a]
            df_b = price_data[symbol_b]
            
            if "close" not in df_a.columns or "close" not in df_b.columns:
                continue
            
            series_a = df_a["close"]
            series_b = df_b["close"]
            
            returns_a = calculator.calculate_returns(series_a)
            returns_b = calculator.calculate_returns(series_b)
            
            corr_value, p_value = calculator.calculate_pearson(returns_a, returns_b)
            
            correlations.append({
                "symbol_a": symbol_a,
                "symbol_b": symbol_b,
                "correlation": corr_value,
                "p_value": p_value,
                "abs_correlation": abs(corr_value),
            })
        except Exception as e:
            print(f"    Error calculating correlation for {symbol_a}-{symbol_b}: {e}")
            continue
    
    correlations.sort(key=lambda x: x["abs_correlation"], reverse=True)
    return correlations


def run_backtests(price_data: Dict[str, pd.DataFrame], correlations: List[Dict], min_correlation: float = 0.7) -> List[Dict]:
    """Run backtests on highly correlated pairs."""
    engine = BacktestEngine()
    backtest_results = []
    
    strong_correlations = [c for c in correlations if abs(c["correlation"]) >= min_correlation]
    print(f"\nRunning backtests on {len(strong_correlations)} pairs with |correlation| >= {min_correlation}...")
    
    for corr in strong_correlations:
        symbol_a = corr["symbol_a"]
        symbol_b = corr["symbol_b"]
        
        if symbol_a not in price_data or symbol_b not in price_data:
            continue
        
        df_a = price_data[symbol_a]
        df_b = price_data[symbol_b]
        
        results = {}
        
        for strategy_name, strategy_func in [
            ("pairs_trading", engine.run_pairs_trading_backtest),
            ("momentum", engine.run_momentum_backtest),
            ("mean_reversion", engine.run_mean_reversion_backtest),
        ]:
            try:
                result = strategy_func(df_a, df_b)
                results[strategy_name] = {
                    "total_return": result["total_return"],
                    "sharpe_ratio": result["sharpe_ratio"],
                    "max_drawdown": result["max_drawdown"],
                    "win_rate": result["win_rate"],
                    "total_trades": result["total_trades"],
                }
            except Exception as e:
                print(f"    Error running {strategy_name} for {symbol_a}-{symbol_b}: {e}")
                results[strategy_name] = None
        
        backtest_results.append({
            "symbol_a": symbol_a,
            "symbol_b": symbol_b,
            "correlation": corr["correlation"],
            "p_value": corr["p_value"],
            "strategies": results,
        })
    
    return backtest_results


def generate_report(correlations: List[Dict], backtest_results: List[Dict], start_date: datetime, end_date: datetime) -> str:
    """Generate markdown report."""
    report_lines = [
        "# Correlation Analysis & Backtesting Report",
        "",
        f"**Analysis Period**: {start_date.date()} to {end_date.date()}",
        f"**Total Instruments Analyzed**: {len(set(c['symbol_a'] for c in correlations) | set(c['symbol_b'] for c in correlations))}",
        f"**Total Pairs Analyzed**: {len(correlations)}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
    ]
    
    strong_pos = [c for c in correlations if c["correlation"] >= 0.7]
    strong_neg = [c for c in correlations if c["correlation"] <= -0.7]
    moderate = [c for c in correlations if 0.5 <= abs(c["correlation"]) < 0.7]
    
    report_lines.extend([
        f"- **Strong Positive Correlations (≥0.7)**: {len(strong_pos)} pairs",
        f"- **Strong Negative Correlations (≤-0.7)**: {len(strong_neg)} pairs",
        f"- **Moderate Correlations (0.5-0.7)**: {len(moderate)} pairs",
        f"- **Weak Correlations (<0.5)**: {len(correlations) - len(strong_pos) - len(strong_neg) - len(moderate)} pairs",
        "",
        "---",
        "",
        "## Top Correlations",
        "",
        "### Strongest Positive Correlations",
        "",
        "| Pair | Correlation | P-Value |",
        "|------|-------------|---------|",
    ])
    
    for corr in strong_pos[:10]:
        report_lines.append(
            f"| {corr['symbol_a']} - {corr['symbol_b']} | {corr['correlation']:.4f} | {corr['p_value']:.4f} |"
        )
    
    report_lines.extend([
        "",
        "### Strongest Negative Correlations",
        "",
        "| Pair | Correlation | P-Value |",
        "|------|-------------|---------|",
    ])
    
    for corr in sorted(strong_neg, key=lambda x: x["correlation"])[:10]:
        report_lines.append(
            f"| {corr['symbol_a']} - {corr['symbol_b']} | {corr['correlation']:.4f} | {corr['p_value']:.4f} |"
        )
    
    report_lines.extend([
        "",
        "---",
        "",
        "## Backtest Results",
        "",
        f"Backtests were run on {len(backtest_results)} pairs with |correlation| ≥ 0.7 using three strategies:",
        "",
        "1. **Pairs Trading**: Mean reversion strategy based on spread z-scores",
        "2. **Momentum**: Trend-following strategy based on momentum signals",
        "3. **Mean Reversion**: Mean reversion strategy with rolling statistics",
        "",
    ])
    
    if backtest_results:
        report_lines.extend([
            "### Best Performing Strategies",
            "",
            "| Pair | Strategy | Total Return | Sharpe Ratio | Max Drawdown | Win Rate | Trades |",
            "|------|----------|--------------|--------------|--------------|----------|--------|",
        ])
        
        all_strategy_results = []
        for result in backtest_results:
            for strategy_name, strategy_data in result["strategies"].items():
                if strategy_data:
                    all_strategy_results.append({
                        "pair": f"{result['symbol_a']}-{result['symbol_b']}",
                        "correlation": result["correlation"],
                        "strategy": strategy_name,
                        **strategy_data,
                    })
        
        all_strategy_results.sort(key=lambda x: x["sharpe_ratio"], reverse=True)
        
        for result in all_strategy_results[:15]:
            report_lines.append(
                f"| {result['pair']} | {result['strategy']} | "
                f"{result['total_return']:.2%} | {result['sharpe_ratio']:.2f} | "
                f"{result['max_drawdown']:.2%} | {result['win_rate']:.2%} | {result['total_trades']} |"
            )
        
        report_lines.extend([
            "",
            "### Strategy Performance Summary",
            "",
        ])
        
        for strategy_name in ["pairs_trading", "momentum", "mean_reversion"]:
            strategy_results = [r for r in all_strategy_results if r["strategy"] == strategy_name]
            if strategy_results:
                avg_sharpe = sum(r["sharpe_ratio"] for r in strategy_results) / len(strategy_results)
                avg_return = sum(r["total_return"] for r in strategy_results) / len(strategy_results)
                positive_returns = sum(1 for r in strategy_results if r["total_return"] > 0)
                
                report_lines.extend([
                    f"#### {strategy_name.replace('_', ' ').title()}",
                    "",
                    f"- **Average Sharpe Ratio**: {avg_sharpe:.2f}",
                    f"- **Average Total Return**: {avg_return:.2%}",
                    f"- **Profitable Pairs**: {positive_returns}/{len(strategy_results)} ({positive_returns/len(strategy_results):.1%})",
                    "",
                ])
    
    report_lines.extend([
        "",
        "---",
        "",
        "## Key Findings",
        "",
        "### Correlation Insights",
        "",
    ])
    
    asset_class_corrs = {}
    for corr in correlations:
        a_class = "equity" if corr["symbol_a"] in MAJOR_INSTRUMENTS["equity"] else \
                 "crypto" if corr["symbol_a"] in MAJOR_INSTRUMENTS["crypto"] else "forex"
        b_class = "equity" if corr["symbol_b"] in MAJOR_INSTRUMENTS["equity"] else \
                 "crypto" if corr["symbol_b"] in MAJOR_INSTRUMENTS["crypto"] else "forex"
        
        if a_class == b_class:
            key = f"{a_class}_intra"
        else:
            key = f"{a_class}_{b_class}"
        
        if key not in asset_class_corrs:
            asset_class_corrs[key] = []
        asset_class_corrs[key].append(corr["correlation"])
    
    for key, corrs in asset_class_corrs.items():
        avg_corr = sum(corrs) / len(corrs)
        report_lines.append(f"- **{key.replace('_', ' ').title()}**: Average correlation = {avg_corr:.4f} ({len(corrs)} pairs)")
    
    report_lines.extend([
        "",
        "### Trading Strategy Insights",
        "",
    ])
    
    if backtest_results:
        best_strategy = max(
            ["pairs_trading", "momentum", "mean_reversion"],
            key=lambda s: sum(
                r["strategies"][s]["sharpe_ratio"]
                for r in backtest_results
                if r["strategies"].get(s) and r["strategies"][s]
            ) / max(1, sum(1 for r in backtest_results if r["strategies"].get(s) and r["strategies"][s]))
        )
        
        report_lines.extend([
            f"- Best performing strategy overall: **{best_strategy.replace('_', ' ').title()}**",
            "- Strong correlations (|r| ≥ 0.7) show potential for pairs trading strategies",
            "- Mean reversion strategies work best on highly correlated pairs",
            "- Momentum strategies benefit from trending markets",
            "",
        ])
    
    report_lines.extend([
        "",
        "---",
        "",
        f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
    ])
    
    return "\n".join(report_lines)


async def main():
    """Main execution function."""
    print("=" * 60)
    print("Major Instruments Backtesting Script")
    print("=" * 60)
    
    from datetime import timezone
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=365)
    
    data_fetcher = DataFetcher(redis_client=None)
    
    price_data = await fetch_all_data(data_fetcher, start_date, end_date)
    
    if not price_data:
        print("Error: No price data retrieved")
        return
    
    print(f"\nSuccessfully retrieved data for {len(price_data)} instruments")
    
    correlations = calculate_correlations(price_data)
    print(f"Calculated {len(correlations)} correlations")
    
    backtest_results = run_backtests(price_data, correlations, min_correlation=0.7)
    print(f"Completed {len(backtest_results)} backtests")
    
    report = generate_report(correlations, backtest_results, start_date, end_date)
    
    report_path = "REPORT.md"
    with open(report_path, "w") as f:
        f.write(report)
    
    print(f"\nReport saved to {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

