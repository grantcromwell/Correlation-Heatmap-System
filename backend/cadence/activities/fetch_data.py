"""Temporal activity for fetching market data."""
from datetime import datetime
from typing import Dict, List

from temporalio import activity

from app.services.data_fetcher import DataFetcher


@activity.defn
async def fetch_data_activity(asset_classes: List[str]) -> Dict:
    """Fetch price data for instruments in asset classes."""
    from redis.asyncio import Redis
    from app.config import settings

    redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    fetcher = DataFetcher(redis_client=redis_client)

    end_date = datetime.utcnow()
    start_date = datetime(end_date.year - 1, 1, 1)

    results = {}
    for asset_class in asset_classes:
        symbols = _get_symbols_for_asset_class(asset_class)
        data = await fetcher.fetch_historical_prices(
            symbols, start_date, end_date, asset_class
        )
        results[asset_class] = {symbol: df.to_dict() for symbol, df in data.items()}

    return results


def _get_symbols_for_asset_class(asset_class: str) -> List[str]:
    """Get instrument symbols for asset class."""
    symbols_map = {
        "crypto": ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "ADA-USD", "XRP-USD"],
        "equity": ["SPY", "QQQ", "IWM", "EFA", "EEM"],
        "tech": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"],
        "metals": ["GLD", "SLV", "GDX", "SIL"],
        "forex": ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"],
    }
    return symbols_map.get(asset_class, [])

