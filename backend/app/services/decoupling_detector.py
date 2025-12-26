"""Decoupling detection service."""
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.correlation_repo import CorrelationRepository
from app.services.data_fetcher import DataFetcher
from app.utils.lorenz_attractor import LorenzAttractor


class DecouplingDetector:
    """Service for detecting correlation decoupling events."""

    def __init__(self, session: AsyncSession):
        """
        Initialize decoupling detector.

        Args:
            session: Database session
        """
        self.session = session
        self.lorenz = LorenzAttractor()
        self.data_fetcher = DataFetcher()
        self.correlation_repo = CorrelationRepository(session)

    async def detect_decoupling(
        self,
        instrument_a_id: int,
        instrument_b_id: int,
        lookback_days: int = 60,
        threshold: float = 0.3,
    ) -> dict:
        """
        Detect decoupling for an instrument pair.

        Args:
            instrument_a_id: First instrument ID
            instrument_b_id: Second instrument ID
            lookback_days: Number of days to look back
            threshold: Decoupling threshold

        Returns:
            Decoupling detection results
        """
        # Get historical correlations
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=lookback_days)

        correlations = await self.correlation_repo.get_correlations(
            instrument_a_id, instrument_b_id, start_date, end_date
        )

        if len(correlations) < 30:
            return {
                "decoupling_detected": False,
                "reason": "insufficient_data",
            }

        # Extract correlation values over time
        correlation_series = pd.Series(
            {corr.timestamp: corr.correlation_value for corr in correlations}
        )
        correlation_series.sort_index(inplace=True)

        # Detect significant correlation drop
        recent_corr = correlation_series.tail(10).mean()
        historical_corr = correlation_series.head(len(correlation_series) - 10).mean()

        correlation_change = historical_corr - recent_corr

        if correlation_change < threshold:
            return {
                "decoupling_detected": False,
                "correlation_before": float(historical_corr),
                "correlation_after": float(recent_corr),
                "correlation_change": float(correlation_change),
            }

        # Use Lorenz attractor for detailed analysis
        # TODO: Fetch price data and run Lorenz analysis
        lorenz_metrics = {
            "attractor_distance": 0.0,
            "stability_index": 0.0,
            "regime_change_probability": correlation_change,
        }

        return {
            "decoupling_detected": True,
            "correlation_before": float(historical_corr),
            "correlation_after": float(recent_corr),
            "correlation_change": float(correlation_change),
            "decoupling_date": correlation_series.index[-1],
            "lorenz_metrics": lorenz_metrics,
        }

