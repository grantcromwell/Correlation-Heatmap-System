"""yfinance wrapper client."""
import asyncio
from datetime import datetime
from typing import Any

import pandas as pd
import yfinance as yf


class YFinanceClient:
    """Client wrapper for yfinance library."""

    def __init__(self):
        """Initialize yfinance client."""
        self._last_request_time: float = 0.0
        self._min_interval = 0.1  # 100ms minimum between requests

    async def _throttle(self) -> None:
        """Basic throttling to avoid overwhelming yfinance."""
        import time
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_interval:
            await asyncio.sleep(self._min_interval - time_since_last)
        self._last_request_time = time.time()

    async def get_historical_data(
        self,
        symbol: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Get historical price data using yfinance."""
        await self._throttle()
        
        ticker = yf.Ticker(symbol)

        # Convert datetime to string format expected by yfinance
        start_str = start_date.strftime("%Y-%m-%d") if start_date else None
        end_str = end_date.strftime("%Y-%m-%d") if end_date else None

        # Download historical data
        try:
            df = ticker.history(start=start_str, end=end_str, interval=interval)
        except Exception as e:
            error_msg = str(e).lower()
            if "rate limit" in error_msg or "429" in error_msg or "too many" in error_msg:
                raise ValueError(f"yfinance rate limit exceeded for {symbol}")
            raise ValueError(f"Error fetching data for {symbol}: {e}")

        if df.empty:
            raise ValueError(f"No data available for symbol {symbol}")

        return df

    async def get_info(self, symbol: str) -> dict[str, Any]:
        """Get ticker info."""
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info

