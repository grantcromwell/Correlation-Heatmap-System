"""GraphQL schema definition."""
from datetime import datetime
from typing import List, Optional

import strawberry
from strawberry.fastapi import GraphQLRouter

from app.api.graphql.types import (
    AssetClass,
    CorrelationPair,
    DiscoveredCorrelation,
    HeatmapData,
    Timeframe,
)


@strawberry.type
class Query:
    """GraphQL query type."""

    @strawberry.field
    async def heatmap(
        self,
        asset_classes: List[AssetClass],
        timeframe: Optional[Timeframe] = None,
        min_correlation: Optional[float] = None,
        lookback_days: Optional[int] = None,
    ) -> HeatmapData:
        """Get correlation heatmap data."""
        # TODO: Implement resolver
        return HeatmapData(correlations=[], metadata={})

    @strawberry.field
    async def discovered_correlations(
        self,
        h3_resolution: Optional[int] = None,
        min_strength: Optional[float] = None,
        status: Optional[str] = None,
    ) -> List[DiscoveredCorrelation]:
        """Get discovered correlations."""
        # TODO: Implement resolver
        return []


def create_graphql_router() -> GraphQLRouter:
    """Create GraphQL router."""
    schema = strawberry.Schema(query=Query)
    return GraphQLRouter(schema)

