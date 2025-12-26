"""Correlation discovery workflow."""
from datetime import timedelta
from typing import List

from temporalio import workflow

from cadence.activities.calculate_correlations import (
    calculate_correlations_activity,
)
from cadence.activities.fetch_data import fetch_data_activity


@workflow.defn
class CorrelationDiscoveryWorkflow:
    """Workflow for discovering correlations across asset classes."""

    @workflow.run
    async def run(
        self, asset_classes: List[str], min_correlation: float = 0.7
    ) -> dict:
        """Run correlation discovery workflow."""
        price_data = await workflow.execute_activity(
            fetch_data_activity,
            asset_classes,
            start_to_close_timeout=timedelta(minutes=10),
        )

        correlations = await workflow.execute_activity(
            calculate_correlations_activity,
            price_data,
            min_correlation,
            start_to_close_timeout=timedelta(minutes=30),
        )

        return {"discovered": len(correlations), "correlations": correlations}

