"""Temporal worker for executing workflows and activities."""
import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from app.config import settings
from app.workflows.correlation_discovery import CorrelationDiscoveryWorkflow
from app.workflows.backtest_workflow import BacktestWorkflow
from cadence.activities.fetch_data import fetch_data_activity
from cadence.activities.calculate_correlations import calculate_correlations_activity
from cadence.activities.run_backtest import run_backtest_activity


async def main():
    """Start Temporal worker."""
    client = await Client.connect(
        settings.temporal_address, namespace=settings.temporal_namespace
    )

    worker = Worker(
        client,
        task_queue="correlation-tasks",
        workflows=[CorrelationDiscoveryWorkflow, BacktestWorkflow],
        activities=[
            fetch_data_activity,
            calculate_correlations_activity,
            run_backtest_activity,
        ],
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

