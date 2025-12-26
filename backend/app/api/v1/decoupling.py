"""Decoupling detection API endpoints."""
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services.decoupling_detector import DecouplingDetector

router = APIRouter(prefix="/decoupling", tags=["decoupling"])


@router.get("/detections")
async def get_decoupling_detections(
    instrument_pair: List[str] = Query(None, description="Instrument pair to filter"),
    threshold: float = Query(0.3, ge=0.0, le=1.0, description="Decoupling threshold"),
    lookback_days: int = Query(60, ge=30, le=365, description="Lookback period in days"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get decoupling detections.

    Args:
        instrument_pair: Optional instrument pair filter
        threshold: Decoupling threshold
        lookback_days: Lookback period
        db: Database session

    Returns:
        List of decoupling detections
    """
    # TODO: Implement decoupling detections retrieval
    return {"detections": []}


@router.post("/analyze")
async def analyze_decoupling(
    instrument_pair: List[str],
    timeframe: str = "1m",
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze decoupling for an instrument pair.

    Args:
        instrument_pair: Instrument pair to analyze
        timeframe: Timeframe for analysis
        db: Database session

    Returns:
        Analysis job information
    """
    # TODO: Implement decoupling analysis
    from uuid import uuid4

    return {
        "analysis_id": str(uuid4()),
        "status": "processing",
    }

