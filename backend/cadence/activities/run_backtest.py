"""Temporal activity for running backtests."""
from datetime import datetime
from typing import Dict, List

from temporalio import activity

from app.services.backtest_engine import BacktestEngine


@activity.defn
async def run_backtest_activity(
    instrument_pair: List[str],
    start_date: datetime,
    end_date: datetime,
    strategy: str,
) -> Dict:
    """Run backtest for instrument pair."""
    from app.services.data_fetcher import DataFetcher
    import pandas as pd

    fetcher = DataFetcher()
    engine = BacktestEngine()

    price_data = await fetcher.fetch_historical_prices(
        instrument_pair, start_date, end_date
    )

    if len(price_data) < 2:
        raise ValueError("Insufficient price data")

    df_a = price_data[instrument_pair[0]]
    df_b = price_data[instrument_pair[1]]

    if strategy == "pairs_trading":
        results = engine.run_pairs_trading_backtest(df_a, df_b)
    elif strategy == "momentum":
        results = engine.run_momentum_backtest(df_a, df_b)
    elif strategy == "mean_reversion":
        results = engine.run_mean_reversion_backtest(df_a, df_b)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    return results

