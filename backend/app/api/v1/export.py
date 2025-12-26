"""Export API endpoints."""
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
import io

from app.dependencies import get_db

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/correlations")
async def export_correlations(
    format: str = Query("json", regex="^(csv|json|parquet)$"),
    asset_classes: list[str] = Query(None),
    timeframe: str = Query(None),
    min_correlation: float = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Export correlations data."""
    # TODO: Fetch correlations from database
    df = pd.DataFrame()

    if format == "csv":
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        return Response(
            content=stream.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=correlations.csv"},
        )
    elif format == "json":
        return Response(
            content=df.to_json(orient="records"),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=correlations.json"},
        )
    elif format == "parquet":
        stream = io.BytesIO()
        df.to_parquet(stream, index=False)
        return Response(
            content=stream.getvalue(),
            media_type="application/octet-stream",
            headers={"Content-Disposition": "attachment; filename=correlations.parquet"},
        )


@router.get("/discovered")
async def export_discovered(
    format: str = Query("json", regex="^(csv|json|parquet)$"),
    status: str = Query(None),
    min_strength: float = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Export discovered correlations."""
    # TODO: Fetch discovered correlations from database
    df = pd.DataFrame()

    if format == "csv":
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        return Response(
            content=stream.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=discovered.csv"},
        )
    elif format == "json":
        return Response(
            content=df.to_json(orient="records"),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=discovered.json"},
        )
    elif format == "parquet":
        stream = io.BytesIO()
        df.to_parquet(stream, index=False)
        return Response(
            content=stream.getvalue(),
            media_type="application/octet-stream",
            headers={"Content-Disposition": "attachment; filename=discovered.parquet"},
        )

