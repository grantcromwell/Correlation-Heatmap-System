"""GraphQL type definitions."""
from datetime import datetime
from typing import List, Optional

import strawberry


@strawberry.enum
class AssetClass:
    """Asset class enum."""

    CRYPTO = "crypto"
    EQUITY = "equity"
    TECH = "tech"
    METALS = "metals"
    FOREX = "forex"


@strawberry.enum
class Timeframe:
    """Timeframe enum."""

    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1m"
    THREE_MONTHS = "3m"
    SIX_MONTHS = "6m"
    ONE_YEAR = "1y"


@strawberry.type
class CorrelationPair:
    """Correlation pair type."""

    instrument_a: str
    instrument_b: str
    correlation: float
    p_value: float
    h3_index: Optional[str]
    asset_class_a: AssetClass
    asset_class_b: AssetClass
    last_updated: datetime


@strawberry.type
class HeatmapMetadata:
    """Heatmap metadata type."""

    total_pairs: int
    strong_correlations: int
    generated_at: datetime


@strawberry.type
class HeatmapData:
    """Heatmap data type."""

    correlations: List[CorrelationPair]
    metadata: HeatmapMetadata


@strawberry.type
class DiscoveredCorrelation:
    """Discovered correlation type."""

    id: str
    instrument_pair: List[str]
    correlation: float
    discovered_at: datetime
    h3_index: str
    status: str

