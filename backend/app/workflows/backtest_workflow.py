"""Backtest workflow."""
from datetime import datetime, timedelta
from typing import List

from temporalio import workflow

from app.cadence.activities.run_backtest import run_backtest_activity


@workflow.defn
class BacktestWorkflow:
    """Workflow for running backtests."""

    @workflow.run
    async def run(
        self,
        instrument_pair: List[str],
        start_date: datetime,
        end_date: datetime,
        strategy: str,
    ) -> dict:
        """Run backtest workflow."""
        results = await workflow.execute_activity(
            run_backtest_activity,
            instrument_pair,
            start_date,
            end_date,
            strategy,
            start_to_close_timeout=timedelta(minutes=10),
        )

        return {"status": "completed", "results": results}

