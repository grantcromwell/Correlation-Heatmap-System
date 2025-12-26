"""Multi-source data fetcher service."""
import json
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
from redis.asyncio import Redis

from app.config import settings
from app.services.clients.alpha_vantage import AlphaVantageClient
from app.services.clients.finnhub import FinnhubClient
from app.services.clients.yfinance import YFinanceClient


class DataFetcher:
    """Service for fetching historical price data from multiple sources."""

    # Asset class to data source mapping
    # Using yfinance for everything to avoid rate limits
    # yfinance supports: stocks, crypto, forex, ETFs, indices, commodities
    ASSET_CLASS_SOURCES = {
        "crypto": "yfinance",
        "equity": "yfinance",
        "tech": "yfinance",
        "metals": "yfinance",
        "forex": "yfinance",
    }

    def __init__(self, redis_client: Redis | None = None):
        """Initialize data fetcher with clients."""
        self.redis = redis_client
        self.alpha_vantage = AlphaVantageClient()
        self.finnhub = FinnhubClient()
        self.yfinance = YFinanceClient()

    def _get_cache_key(self, symbol: str, start_date: datetime, end_date: datetime) -> str:
        """Generate cache key for price data."""
        return f"price_data:{symbol}:{start_date.date()}:{end_date.date()}"

    async def _get_from_cache(self, cache_key: str) -> pd.DataFrame | None:
        """Get data from Redis cache."""
        if not self.redis:
            return None

        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                # Deserialize JSON to DataFrame
                data_dict = json.loads(cached_data)
                df = pd.DataFrame(data_dict)
                df.index = pd.to_datetime(df.index)
                return df
        except Exception:
            # If cache fails, continue without cache
            pass
        return None

    async def _set_cache(self, cache_key: str, df: pd.DataFrame, ttl: int = 3600) -> None:
        """Store data in Redis cache."""
        if not self.redis:
            return

        try:
            # Serialize DataFrame to JSON
            data_dict = df.to_dict(orient="index")
            # Convert index to string for JSON serialization
            data_dict_str = json.dumps({str(k): v for k, v in data_dict.items()})
            await self.redis.setex(cache_key, ttl, data_dict_str)
        except Exception:
            # If cache fails, continue without caching
            pass

    async def fetch_historical_prices(
        self,
        symbols: list[str],
        start_date: datetime,
        end_date: datetime,
        asset_class: str | None = None,
    ) -> dict[str, pd.DataFrame]:
        """Fetch historical prices for multiple symbols."""
        import asyncio
        results: dict[str, pd.DataFrame] = {}

        # Determine data source
        if asset_class:
            source = self.ASSET_CLASS_SOURCES.get(asset_class, "yfinance")
        else:
            source = "yfinance"  # Default fallback

        # Minimal delay for yfinance to avoid rate limiting
        yfinance_delay = 0.05  # 50ms delay between yfinance requests

        for i, symbol in enumerate(symbols):
            try:
                # Check cache first
                cache_key = self._get_cache_key(symbol, start_date, end_date)
                cached_data = await self._get_from_cache(cache_key)
                if cached_data is not None:
                    results[symbol] = cached_data
                    continue

                # Fetch from appropriate source
                if source == "yfinance":
                    # Add small delay for yfinance to avoid rate limiting
                    if i > 0:
                        await asyncio.sleep(yfinance_delay)
                    df = await self.yfinance.get_historical_data(
                        symbol, start_date, end_date, interval="1d"
                    )
                elif source == "alpha_vantage":
                    # Fallback to yfinance to avoid rate limits
                    try:
                        data = await self.alpha_vantage.get_time_series_daily(symbol)
                        df = self._parse_alpha_vantage_data(data)
                    except Exception as e:
                        print(f"Alpha Vantage failed for {symbol}, using yfinance: {e}")
                        df = await self.yfinance.get_historical_data(
                            symbol, start_date, end_date, interval="1d"
                        )
                elif source == "finnhub":
                    # Fallback to yfinance to avoid rate limits
                    try:
                        from_ts = int(start_date.timestamp())
                        to_ts = int(end_date.timestamp())
                        data = await self.finnhub.get_stock_candles(
                            symbol, resolution="D", from_timestamp=from_ts, to_timestamp=to_ts
                        )
                        df = self._parse_finnhub_data(data)
                    except Exception as e:
                        print(f"Finnhub failed for {symbol}, using yfinance: {e}")
                        df = await self.yfinance.get_historical_data(
                            symbol, start_date, end_date, interval="1d"
                        )
                else:
                    raise ValueError(f"Unknown data source: {source}")

                # Normalize DataFrame format
                df = self._normalize_dataframe(df)

                # Cache the result
                await self._set_cache(cache_key, df)

                results[symbol] = df
            except ValueError as e:
                # Handle rate limit errors specifically
                error_msg = str(e).lower()
                if "rate limit" in error_msg or "too many requests" in error_msg:
                    print(f"Rate limit hit for {symbol}, waiting before retry...")
                    await asyncio.sleep(60)  # Wait 1 minute before continuing
                    # Retry once
                    try:
                        if source == "yfinance":
                            df = await self.yfinance.get_historical_data(
                                symbol, start_date, end_date, interval="1d"
                            )
                        elif source == "alpha_vantage":
                            try:
                                data = await self.alpha_vantage.get_time_series_daily(symbol)
                                df = self._parse_alpha_vantage_data(data)
                            except Exception:
                                df = await self.yfinance.get_historical_data(
                                    symbol, start_date, end_date, interval="1d"
                                )
                        elif source == "finnhub":
                            try:
                                from_ts = int(start_date.timestamp())
                                to_ts = int(end_date.timestamp())
                                data = await self.finnhub.get_stock_candles(
                                    symbol, resolution="D", from_timestamp=from_ts, to_timestamp=to_ts
                                )
                                df = self._parse_finnhub_data(data)
                            except Exception:
                                df = await self.yfinance.get_historical_data(
                                    symbol, start_date, end_date, interval="1d"
                                )
                        df = self._normalize_dataframe(df)
                        await self._set_cache(cache_key, df)
                        results[symbol] = df
                    except Exception as retry_e:
                        print(f"Error fetching data for {symbol} after retry: {retry_e}")
                        continue
                else:
                    # Log error but continue with other symbols
                    print(f"Error fetching data for {symbol}: {e}")
                    continue
            except Exception as e:
                # Log error but continue with other symbols
                print(f"Error fetching data for {symbol}: {e}")
                continue

        return results

    def _parse_alpha_vantage_data(self, data: dict[str, Any]) -> pd.DataFrame:
        """Parse Alpha Vantage API response to DataFrame."""
        time_series_key = "Time Series (Daily)"
        if time_series_key not in data:
            raise ValueError("Invalid Alpha Vantage response format")

        records = []
        for date_str, values in data[time_series_key].items():
            records.append(
                {
                    "date": pd.to_datetime(date_str),
                    "open": float(values["1. open"]),
                    "high": float(values["2. high"]),
                    "low": float(values["3. low"]),
                    "close": float(values["4. close"]),
                    "adjusted_close": float(values["5. adjusted close"]),
                    "volume": int(values["6. volume"]),
                }
            )

        df = pd.DataFrame(records)
        df.set_index("date", inplace=True)
        df.sort_index(inplace=True)
        return df

    def _parse_finnhub_data(self, data: dict[str, Any]) -> pd.DataFrame:
        """Parse Finnhub API response to DataFrame."""
        if data.get("s") != "ok":
            raise ValueError(f"Finnhub API error: {data.get('s')}")

        timestamps = data.get("t", [])
        opens = data.get("o", [])
        highs = data.get("h", [])
        lows = data.get("l", [])
        closes = data.get("c", [])
        volumes = data.get("v", [])

        records = []
        for i, ts in enumerate(timestamps):
            records.append(
                {
                    "date": pd.to_datetime(ts, unit="s"),
                    "open": opens[i],
                    "high": highs[i],
                    "low": lows[i],
                    "close": closes[i],
                    "volume": volumes[i],
                }
            )

        df = pd.DataFrame(records)
        df.set_index("date", inplace=True)
        df.sort_index(inplace=True)
        return df

    def _normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize DataFrame to standard format."""
        # Normalize column names to lowercase (yfinance uses capital letters)
        df.columns = df.columns.str.lower()
        
        # Map common column name variations
        column_mapping = {
            "adj close": "adjusted_close",
            "adj_close": "adjusted_close",
        }
        df.rename(columns=column_mapping, inplace=True)
        
        # Ensure we have required columns
        required_columns = ["open", "high", "low", "close", "volume"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}. Available columns: {list(df.columns)}")

        # Use adjusted_close if available, otherwise use close
        if "adjusted_close" in df.columns:
            df["close"] = df["adjusted_close"]

        # Select only required columns
        df = df[required_columns].copy()

        # Ensure index is datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        # Sort by date
        df.sort_index(inplace=True)

        return df

