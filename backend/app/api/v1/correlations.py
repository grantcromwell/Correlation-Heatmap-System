"""Correlation API endpoints."""
import logging
from datetime import datetime, timedelta
from itertools import combinations
from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from temporalio.client import Client
from temporalio.exceptions import WorkflowNotFoundError

from app.config import settings
from app.dependencies import get_db, get_redis
from app.database.models import DiscoveredCorrelation, Instrument
from app.models.correlation import (
    BacktestJobResponse,
    BacktestRequest,
    BacktestResultResponse,
    CorrelationPair,
    DiscoveredCorrelationResponse,
    DiscoveredCorrelationsResponse,
    HeatmapMetadata,
    HeatmapResponse,
)
from app.repositories.correlation_repo import CorrelationRepository
from app.services.correlation_calculator import CorrelationCalculator
from app.services.data_fetcher import DataFetcher
from app.utils.h3_utils import H3Manager
from app.workflows.backtest_workflow import BacktestWorkflow
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

# Temporal client singleton
_temporal_client: Client | None = None


async def get_temporal_client() -> Client:
    """Get or create Temporal client."""
    global _temporal_client
    if _temporal_client is None:
        _temporal_client = await Client.connect(
            settings.temporal_address,
            namespace=settings.temporal_namespace,
        )
    return _temporal_client

router = APIRouter(prefix="/correlations", tags=["correlations"])


@router.get("/heatmap", response_model=HeatmapResponse)
async def get_heatmap(
    asset_classes: List[str] = Query(..., description="Asset classes to include"),
    timeframe: str = Query("1m", description="Timeframe: 1d, 1w, 1m, 3m, 6m, 1y"),
    min_correlation: float = Query(0.5, ge=-1.0, le=1.0, description="Minimum correlation"),
    lookback_days: int = Query(252, ge=30, le=2520, description="Lookback period in days"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> HeatmapResponse:
    """
    Get correlation heatmap data.

    Args:
        asset_classes: List of asset classes to include
        timeframe: Timeframe for correlation calculation
        min_correlation: Minimum correlation value to include
        lookback_days: Number of days to look back
        db: Database session
        redis: Redis client

    Returns:
        Heatmap data with correlations
    """
    # Map timeframe to days if not using lookback_days directly
    timeframe_map = {"1d": 1, "1w": 7, "1m": 30, "3m": 90, "6m": 180, "1y": 365}
    if timeframe in timeframe_map:
        lookback_days = timeframe_map[timeframe]

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=lookback_days)

    # Initialize services
    repo = CorrelationRepository(db)
    data_fetcher = DataFetcher(redis)
    calculator = CorrelationCalculator()
    h3_manager = H3Manager()

    # Fetch instruments by asset class
    instruments = await repo.get_instruments_by_asset_class(asset_classes)
    if not instruments:
        logger.warning(f"No instruments found for asset classes: {asset_classes}")
        return HeatmapResponse(
            heatmap_data=[],
            metadata=HeatmapMetadata(
                total_pairs=0,
                strong_correlations=0,
                generated_at=datetime.utcnow(),
            ),
        )

    # Fetch historical prices for all instruments
    symbols = [inst.symbol for inst in instruments]
    symbol_to_instrument = {inst.symbol: inst for inst in instruments}
    
    # Group by asset class for data fetching
    price_data = {}
    for asset_class in asset_classes:
        class_symbols = [inst.symbol for inst in instruments if inst.asset_class == asset_class]
        if class_symbols:
            class_prices = await data_fetcher.fetch_historical_prices(
                class_symbols, start_date, end_date, asset_class
            )
            price_data.update(class_prices)

    # Calculate correlations for all pairs
    correlation_pairs = []
    strong_correlations_count = 0

    for inst_a, inst_b in combinations(instruments, 2):
        # Ensure consistent ordering (instrument_a_id < instrument_b_id)
        if inst_a.id > inst_b.id:
            inst_a, inst_b = inst_b, inst_a

        symbol_a = inst_a.symbol
        symbol_b = inst_b.symbol

        # Skip if we don't have price data for both instruments
        if symbol_a not in price_data or symbol_b not in price_data:
            logger.debug(f"Missing price data for pair: {symbol_a}-{symbol_b}")
            continue

        df_a = price_data[symbol_a]
        df_b = price_data[symbol_b]

        # Extract close prices
        if "close" not in df_a.columns or "close" not in df_b.columns:
            logger.debug(f"Missing 'close' column for pair: {symbol_a}-{symbol_b}")
            continue

        series_a = df_a["close"]
        series_b = df_b["close"]

        try:
            # Calculate returns
            returns_a = calculator.calculate_returns(series_a)
            returns_b = calculator.calculate_returns(series_b)

            # Calculate correlation
            corr_value, p_value = calculator.calculate_pearson(returns_a, returns_b)

            # Filter by min_correlation
            if abs(corr_value) < abs(min_correlation):
                continue

            # Generate H3 index
            h3_index = h3_manager.correlation_to_h3_index(symbol_a, symbol_b, corr_value)

            # Count strong correlations
            if abs(corr_value) >= 0.7:
                strong_correlations_count += 1

            # Create correlation pair
            correlation_pairs.append(
                CorrelationPair(
                    instrument_a=symbol_a,
                    instrument_b=symbol_b,
                    correlation=corr_value,
                    p_value=p_value,
                    h3_index=h3_index,
                    asset_class_a=inst_a.asset_class,
                    asset_class_b=inst_b.asset_class,
                    last_updated=datetime.utcnow(),
                )
            )
        except ValueError as e:
            # Insufficient data or calculation error
            logger.debug(f"Correlation calculation failed for {symbol_a}-{symbol_b}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error calculating correlation for {symbol_a}-{symbol_b}: {e}")
            continue

    # Create response
    return HeatmapResponse(
        heatmap_data=correlation_pairs,
        metadata=HeatmapMetadata(
            total_pairs=len(correlation_pairs),
            strong_correlations=strong_correlations_count,
            generated_at=datetime.utcnow(),
        ),
    )


@router.get("/discovered", response_model=DiscoveredCorrelationsResponse)
async def get_discovered_correlations(
    h3_resolution: int = Query(7, ge=0, le=15, description="H3 resolution"),
    min_strength: float = Query(0.7, ge=0.0, le=1.0, description="Minimum correlation strength"),
    status: str = Query(None, description="Filter by status: new, validated, decayed"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> DiscoveredCorrelationsResponse:
    """
    Get discovered correlations.

    Args:
        h3_resolution: H3 resolution level
        min_strength: Minimum correlation strength
        status: Filter by status
        page: Page number
        per_page: Items per page
        db: Database session

    Returns:
        List of discovered correlations
    """
    # Build query conditions
    conditions = [
        DiscoveredCorrelation.correlation_value >= min_strength,
    ]

    # Filter by status if provided
    if status:
        conditions.append(DiscoveredCorrelation.status == status)

    # Filter by H3 resolution if provided
    # Extract resolution from H3 index (first character after '8' prefix indicates resolution)
    # H3 indices are strings, we'll filter by checking if they match the resolution pattern
    # For simplicity, we'll filter by absolute correlation strength which correlates with resolution
    # More precise filtering would require parsing H3 index resolution

    # Build base query with joins
    base_query = (
        select(DiscoveredCorrelation)
        .join(Instrument, DiscoveredCorrelation.instrument_a_id == Instrument.id)
        .where(and_(*conditions))
        .order_by(DiscoveredCorrelation.discovered_at.desc())
    )

    # Count total matching records
    count_query = (
        select(func.count(DiscoveredCorrelation.id))
        .join(Instrument, DiscoveredCorrelation.instrument_a_id == Instrument.id)
        .where(and_(*conditions))
    )
    total_result = await db.execute(count_query)
    total_count = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * per_page
    paginated_query = base_query.offset(offset).limit(per_page)

    # Execute query
    result = await db.execute(paginated_query)
    discovered_correlations = list(result.scalars().all())

    # Load instrument relationships for symbol access
    discoveries_response = []
    for dc in discovered_correlations:
        # Load instruments separately
        inst_a = await db.get(Instrument, dc.instrument_a_id)
        inst_b = await db.get(Instrument, dc.instrument_b_id)
        
        if not inst_a or not inst_b:
            logger.warning(f"Missing instruments for discovered correlation {dc.id}")
            continue

        discoveries_response.append(
            DiscoveredCorrelationResponse(
                id=dc.id,
                instrument_pair=[inst_a.symbol, inst_b.symbol],
                correlation=dc.correlation_value,
                discovered_at=dc.discovered_at,
                h3_index=dc.h3_index,
                backtest_results=dc.backtest_results,
                spanning_tree_data=None,  # Not implemented yet
                status=dc.status,
            )
        )

    return DiscoveredCorrelationsResponse(
        discoveries=discoveries_response,
        pagination={"page": page, "per_page": per_page, "total": total_count},
    )


@router.post("/backtest", response_model=BacktestJobResponse)
async def start_backtest(
    request: BacktestRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> BacktestJobResponse:
    """
    Start a backtest for an instrument pair.

    Args:
        request: Backtest request
        db: Database session
        redis: Redis client

    Returns:
        Backtest job information
    """
    # Validate request
    if len(request.instrument_pair) != 2:
        raise HTTPException(status_code=400, detail="instrument_pair must contain exactly 2 instruments")

    if request.start_date >= request.end_date:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")

    valid_strategies = ["pairs_trading", "momentum", "mean_reversion"]
    if request.strategy not in valid_strategies:
        raise HTTPException(
            status_code=400,
            detail=f"strategy must be one of: {', '.join(valid_strategies)}",
        )

    # Get or create instruments
    instruments = []
    for symbol in request.instrument_pair:
        stmt = select(Instrument).where(Instrument.symbol == symbol)
        result = await db.execute(stmt)
        instrument = result.scalar_one_or_none()
        if not instrument:
            # Create instrument if it doesn't exist (default asset class)
            instrument = Instrument(
                symbol=symbol,
                asset_class="equity",  # Default, could be improved
                data_source="yfinance",
            )
            db.add(instrument)
            await db.flush()
            await db.refresh(instrument)
        instruments.append(instrument)

    instrument_a_id = instruments[0].id
    instrument_b_id = instruments[1].id

    # Start Temporal workflow
    try:
        client = await get_temporal_client()
        workflow_id = f"backtest-{uuid4()}"

        handle = await client.start_workflow(
            BacktestWorkflow.run,
            args=[
                request.instrument_pair,
                request.start_date,
                request.end_date,
                request.strategy,
            ],
            id=workflow_id,
            task_queue="backtest-queue",
        )

        # Store workflow_id in Redis with TTL (24 hours)
        await redis.setex(f"backtest:{workflow_id}", 86400, str(handle.id))

        return BacktestJobResponse(
            backtest_id=UUID(workflow_id.split("-")[-1]),
            status="queued",
            estimated_completion=datetime.utcnow() + timedelta(minutes=10),
        )
    except Exception as e:
        logger.error(f"Failed to start backtest workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start backtest: {str(e)}")


@router.get("/backtest/{backtest_id}", response_model=BacktestResultResponse)
async def get_backtest_result(
    backtest_id: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> BacktestResultResponse:
    """
    Get backtest result.

    Args:
        backtest_id: Backtest job ID
        db: Database session
        redis: Redis client

    Returns:
        Backtest result
    """
    try:
        backtest_uuid = UUID(backtest_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid backtest_id format")

    # Get workflow_id from Redis
    workflow_id_key = f"backtest:backtest-{backtest_id}"
    stored_workflow_id = await redis.get(workflow_id_key)
    
    if not stored_workflow_id:
        # Try to construct workflow_id from backtest_id
        workflow_id = f"backtest-{backtest_id}"
    else:
        workflow_id = stored_workflow_id

    try:
        client = await get_temporal_client()
        handle = client.get_workflow_handle(workflow_id)

        # Get workflow status
        description = await handle.describe()

        # Check workflow status
        if description.status.name == "COMPLETED":
            result = await handle.result()
            return BacktestResultResponse(
                backtest_id=backtest_uuid,
                status="completed",
                results=result.get("results") if isinstance(result, dict) else result,
                lorenz_analysis=None,  # Could be extracted from results if available
            )
        elif description.status.name == "RUNNING":
            return BacktestResultResponse(
                backtest_id=backtest_uuid,
                status="running",
                results=None,
                lorenz_analysis=None,
            )
        elif description.status.name == "FAILED":
            return BacktestResultResponse(
                backtest_id=backtest_uuid,
                status="failed",
                results={"error": "Workflow failed"},
                lorenz_analysis=None,
            )
        else:
            return BacktestResultResponse(
                backtest_id=backtest_uuid,
                status="unknown",
                results=None,
                lorenz_analysis=None,
            )
    except WorkflowNotFoundError:
        raise HTTPException(status_code=404, detail=f"Backtest {backtest_id} not found")
    except Exception as e:
        logger.error(f"Failed to get backtest result: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get backtest result: {str(e)}")

