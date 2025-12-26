"""Pydantic models for correlation API."""
from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class CorrelationPair(BaseModel):
    """Correlation pair model."""

    instrument_a: str
    instrument_b: str
    correlation: float = Field(..., ge=-1.0, le=1.0)
    p_value: float = Field(..., ge=0.0, le=1.0)
    h3_index: str | None = None
    asset_class_a: str
    asset_class_b: str
    last_updated: datetime


class HeatmapMetadata(BaseModel):
    """Heatmap metadata."""

    total_pairs: int
    strong_correlations: int
    generated_at: datetime


class HeatmapResponse(BaseModel):
    """Heatmap API response."""

    heatmap_data: List[CorrelationPair]
    metadata: HeatmapMetadata


class DiscoveredCorrelationResponse(BaseModel):
    """Discovered correlation response."""

    id: UUID
    instrument_pair: List[str]
    correlation: float
    discovered_at: datetime
    h3_index: str
    backtest_results: dict | None = None
    spanning_tree_data: dict | None = None
    status: str


class DiscoveredCorrelationsResponse(BaseModel):
    """Discovered correlations list response."""

    discoveries: List[DiscoveredCorrelationResponse]
    pagination: dict


class BacktestRequest(BaseModel):
    """Backtest request model."""

    instrument_pair: List[str] = Field(..., min_length=2, max_length=2)
    start_date: datetime
    end_date: datetime
    strategy: str = Field(..., pattern="^(pairs_trading|momentum|mean_reversion)$")


class BacktestJobResponse(BaseModel):
    """Backtest job response."""

    backtest_id: UUID
    status: str
    estimated_completion: datetime | None = None


class BacktestResultResponse(BaseModel):
    """Backtest result response."""

    backtest_id: UUID
    status: str
    results: dict | None = None
    lorenz_analysis: dict | None = None

