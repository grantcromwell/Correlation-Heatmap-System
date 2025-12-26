"""Finnhub API client."""
import asyncio
from datetime import datetime
from typing import Any

import httpx

from app.config import settings


class FinnhubClient:
    """Client for Finnhub API."""

    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self, api_key: str | None = None):
        """Initialize Finnhub client."""
        self.api_key = api_key or settings.finnhub_api_key
        self.rate_limit = settings.finnhub_rate_limit
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

    async def get_stock_candles(
        self,
        symbol: str,
        resolution: str = "D",
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
    ) -> dict[str, Any]:
        """Get stock candle data."""
        await self._rate_limit_delay()

        params: dict[str, Any] = {
            "symbol": symbol,
            "resolution": resolution,
            "token": self.api_key,
        }

        if from_timestamp:
            params["from"] = from_timestamp
        if to_timestamp:
            params["to"] = to_timestamp

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/stock/candle",
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("s") == "no_data":
                raise ValueError(f"No data available for symbol {symbol}")

            return data

    async def get_forex_candles(
        self,
        symbol: str,
        resolution: str = "D",
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
    ) -> dict[str, Any]:
        """Get forex candle data."""
        await self._rate_limit_delay()

        params: dict[str, Any] = {
            "symbol": symbol,
            "resolution": resolution,
            "token": self.api_key,
        }

        if from_timestamp:
            params["from"] = from_timestamp
        if to_timestamp:
            params["to"] = to_timestamp

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/forex/candle",
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("s") == "no_data":
                raise ValueError(f"No data available for symbol {symbol}")

            return data

    async def get_crypto_candles(
        self,
        symbol: str,
        resolution: str = "D",
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
    ) -> dict[str, Any]:
        """Get crypto candle data."""
        await self._rate_limit_delay()

        params: dict[str, Any] = {
            "symbol": symbol,
            "resolution": resolution,
            "token": self.api_key,
        }

        if from_timestamp:
            params["from"] = from_timestamp
        if to_timestamp:
            params["to"] = to_timestamp

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/crypto/candle",
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("s") == "no_data":
                raise ValueError(f"No data available for symbol {symbol}")

            return data

