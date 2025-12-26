"""Alpha Vantage API client."""
import asyncio
from datetime import datetime
from typing import Any

import httpx

from app.config import settings


class AlphaVantageClient:
    """Client for Alpha Vantage API."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str | None = None):
        """Initialize Alpha Vantage client."""
        self.api_key = api_key or settings.alpha_vantage_api_key
        self.rate_limit = settings.alpha_vantage_rate_limit
        self._last_request_time: float = 0.0
        self._min_interval = 60.0 / self.rate_limit  # seconds between requests

    async def _rate_limit_delay(self) -> None:
        """Enforce rate limiting."""
        import time
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_interval:
            sleep_time = self._min_interval - time_since_last
            await asyncio.sleep(sleep_time)
        self._last_request_time = time.time()

    async def get_time_series_daily(
        self, symbol: str, outputsize: str = "full"
    ) -> dict[str, Any]:
        """Get daily time series data for a symbol."""
        await self._rate_limit_delay()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                self.BASE_URL,
                params={
                    "function": "TIME_SERIES_DAILY_ADJUSTED",
                    "symbol": symbol,
                    "outputsize": outputsize,
                    "apikey": self.api_key,
                    "datatype": "json",
                },
            )
            response.raise_for_status()
            data = response.json()

            # Check for API errors
            if "Error Message" in data:
                raise ValueError(f"Alpha Vantage API error: {data['Error Message']}")
            if "Note" in data:
                raise ValueError(f"Alpha Vantage API rate limit: {data['Note']}")

            return data

    async def get_time_series_intraday(
        self, symbol: str, interval: str = "60min", outputsize: str = "full"
    ) -> dict[str, Any]:
        """Get intraday time series data for a symbol."""
        await self._rate_limit_delay()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                self.BASE_URL,
                params={
                    "function": "TIME_SERIES_INTRADAY",
                    "symbol": symbol,
                    "interval": interval,
                    "outputsize": outputsize,
                    "apikey": self.api_key,
                    "datatype": "json",
                },
            )
            response.raise_for_status()
            data = response.json()

            if "Error Message" in data:
                raise ValueError(f"Alpha Vantage API error: {data['Error Message']}")
            if "Note" in data:
                raise ValueError(f"Alpha Vantage API rate limit: {data['Note']}")

            return data

