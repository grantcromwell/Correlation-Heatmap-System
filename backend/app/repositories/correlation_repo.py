"""Correlation repository."""
from datetime import datetime
from typing import List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Correlation, Instrument
from app.repositories.base import BaseRepository


class CorrelationRepository(BaseRepository[Correlation]):
    """Repository for correlation operations."""

    def __init__(self, session: AsyncSession):
        """Initialize correlation repository."""
        super().__init__(Correlation, session)

    async def get_correlations(
        self,
        instrument_a_id: int,
        instrument_b_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 1000,
    ) -> List[Correlation]:
        """
        Get correlations for an instrument pair.

        Args:
            instrument_a_id: First instrument ID
            instrument_b_id: Second instrument ID
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum number of results

        Returns:
            List of correlations
        """
        conditions = [
            Correlation.instrument_a_id == instrument_a_id,
            Correlation.instrument_b_id == instrument_b_id,
        ]

        if start_date:
            conditions.append(Correlation.timestamp >= start_date)
        if end_date:
            conditions.append(Correlation.timestamp <= end_date)

        stmt = (
            select(Correlation)
            .where(and_(*conditions))
            .order_by(Correlation.timestamp.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_correlation(
        self, instrument_a_id: int, instrument_b_id: int
    ) -> Correlation | None:
        """Get the latest correlation for an instrument pair."""
        stmt = (
            select(Correlation)
            .where(
                and_(
                    Correlation.instrument_a_id == instrument_a_id,
                    Correlation.instrument_b_id == instrument_b_id,
                )
            )
            .order_by(Correlation.timestamp.desc())
            .limit(1)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_correlations_by_asset_class(
        self,
        asset_class: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        min_correlation: float | None = None,
    ) -> List[Correlation]:
        """
        Get correlations for instruments in an asset class.

        Args:
            asset_class: Asset class name
            start_date: Start date filter
            end_date: End date filter
            min_correlation: Minimum correlation value

        Returns:
            List of correlations
        """
        conditions = [
            Instrument.asset_class == asset_class,
        ]

        if start_date:
            conditions.append(Correlation.timestamp >= start_date)
        if end_date:
            conditions.append(Correlation.timestamp <= end_date)
        if min_correlation is not None:
            conditions.append(Correlation.correlation_value >= min_correlation)

        stmt = (
            select(Correlation)
            .join(Instrument, Correlation.instrument_a_id == Instrument.id)
            .where(and_(*conditions))
            .order_by(Correlation.timestamp.desc())
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_correlation(
        self,
        instrument_a_id: int,
        instrument_b_id: int,
        correlation_value: float,
        p_value: float,
        timestamp: datetime,
        lookback_days: int = 252,
        method: str = "pearson",
    ) -> Correlation:
        """Create a new correlation record."""
        correlation = Correlation(
            instrument_a_id=instrument_a_id,
            instrument_b_id=instrument_b_id,
            correlation_value=correlation_value,
            p_value=p_value,
            timestamp=timestamp,
            lookback_days=lookback_days,
            method=method,
        )
        self.session.add(correlation)
        await self.session.flush()
        return correlation

    async def bulk_create_correlations(self, correlations: List[dict]) -> None:
        """Bulk create correlation records."""
        correlation_objects = [Correlation(**corr) for corr in correlations]
        self.session.add_all(correlation_objects)
        await self.session.flush()

    async def get_instruments_by_asset_class(self, asset_classes: List[str]) -> List[Instrument]:
        """
        Get instruments filtered by asset classes.

        Args:
            asset_classes: List of asset class names

        Returns:
            List of instruments
        """
        stmt = select(Instrument).where(Instrument.asset_class.in_(asset_classes))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

