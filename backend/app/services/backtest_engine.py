"""Backtest engine for correlation-based strategies."""
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd


class BacktestEngine:
    """Backtest engine for correlation-based trading strategies."""

    def __init__(self):
        """Initialize backtest engine."""
        pass

    def run_pairs_trading_backtest(
        self,
        price_data_a: pd.DataFrame,
        price_data_b: pd.DataFrame,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5,
    ) -> dict[str, Any]:
        """
        Run pairs trading backtest.

        Args:
            price_data_a: Price data for first instrument
            price_data_b: Price data for second instrument
            entry_threshold: Z-score threshold for entry
            exit_threshold: Z-score threshold for exit

        Returns:
            Backtest results dictionary
        """
        # Align price series
        aligned = pd.DataFrame(
            {
                "price_a": price_data_a["close"],
                "price_b": price_data_b["close"],
            }
        ).dropna()

        # Calculate spread
        spread = aligned["price_a"] - aligned["price_b"]

        # Calculate z-score
        spread_mean = spread.mean()
        spread_std = spread.std()
        z_score = (spread - spread_mean) / spread_std

        # Generate signals
        positions = []
        current_position = 0  # 0 = no position, 1 = long spread, -1 = short spread

        for i, z in enumerate(z_score):
            if current_position == 0:
                if z > entry_threshold:
                    current_position = -1  # Short spread (sell A, buy B)
                elif z < -entry_threshold:
                    current_position = 1  # Long spread (buy A, sell B)
            elif current_position == 1:
                if z > -exit_threshold:
                    current_position = 0  # Exit long
            elif current_position == -1:
                if z < exit_threshold:
                    current_position = 0  # Exit short

            positions.append(current_position)

        # Calculate returns
        returns_a = aligned["price_a"].pct_change()
        returns_b = aligned["price_b"].pct_change()
        strategy_returns = pd.Series(positions[:-1]) * (returns_a[1:] - returns_b[1:])

        # Calculate metrics
        total_return = (1 + strategy_returns).prod() - 1
        sharpe_ratio = (
            strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
            if strategy_returns.std() > 0
            else 0.0
        )
        max_drawdown = self._calculate_max_drawdown(strategy_returns)
        win_rate = (strategy_returns > 0).sum() / len(strategy_returns) if len(strategy_returns) > 0 else 0.0
        total_trades = len([i for i in range(1, len(positions)) if positions[i] != positions[i - 1]])

        return {
            "total_return": float(total_return),
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "win_rate": float(win_rate),
            "total_trades": total_trades,
            "strategy_returns": strategy_returns.tolist(),
        }

    def run_momentum_backtest(
        self,
        price_data_a: pd.DataFrame,
        price_data_b: pd.DataFrame,
        lookback_period: int = 20,
    ) -> dict[str, Any]:
        """
        Run momentum strategy backtest.

        Args:
            price_data_a: Price data for first instrument
            price_data_b: Price data for second instrument
            lookback_period: Lookback period for momentum

        Returns:
            Backtest results dictionary
        """
        # Align price series
        aligned = pd.DataFrame(
            {
                "price_a": price_data_a["close"],
                "price_b": price_data_b["close"],
            }
        ).dropna()

        # Calculate momentum
        momentum_a = aligned["price_a"].pct_change(lookback_period)
        momentum_b = aligned["price_b"].pct_change(lookback_period)

        # Generate signals (long when both have positive momentum)
        signals = ((momentum_a > 0) & (momentum_b > 0)).astype(int)

        # Calculate returns
        returns_a = aligned["price_a"].pct_change()
        returns_b = aligned["price_b"].pct_change()
        strategy_returns = signals.shift(1) * (returns_a + returns_b) / 2

        # Calculate metrics
        total_return = (1 + strategy_returns).prod() - 1
        sharpe_ratio = (
            strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
            if strategy_returns.std() > 0
            else 0.0
        )
        max_drawdown = self._calculate_max_drawdown(strategy_returns)
        win_rate = (strategy_returns > 0).sum() / len(strategy_returns) if len(strategy_returns) > 0 else 0.0
        total_trades = signals.diff().abs().sum()

        return {
            "total_return": float(total_return),
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "win_rate": float(win_rate),
            "total_trades": int(total_trades),
            "strategy_returns": strategy_returns.tolist(),
        }

    def run_mean_reversion_backtest(
        self,
        price_data_a: pd.DataFrame,
        price_data_b: pd.DataFrame,
        lookback_period: int = 20,
        entry_threshold: float = 1.5,
    ) -> dict[str, Any]:
        """
        Run mean reversion strategy backtest.

        Args:
            price_data_a: Price data for first instrument
            price_data_b: Price data for second instrument
            lookback_period: Lookback period for mean calculation
            entry_threshold: Z-score threshold for entry

        Returns:
            Backtest results dictionary
        """
        # Align price series
        aligned = pd.DataFrame(
            {
                "price_a": price_data_a["close"],
                "price_b": price_data_b["close"],
            }
        ).dropna()

        # Calculate spread
        spread = aligned["price_a"] - aligned["price_b"]

        # Calculate rolling mean and std
        spread_mean = spread.rolling(lookback_period).mean()
        spread_std = spread.rolling(lookback_period).std()
        z_score = (spread - spread_mean) / spread_std

        # Generate signals (mean revert when z-score is extreme)
        signals = pd.Series(0, index=z_score.index)
        signals[z_score > entry_threshold] = -1  # Short spread
        signals[z_score < -entry_threshold] = 1  # Long spread

        # Calculate returns
        returns_a = aligned["price_a"].pct_change()
        returns_b = aligned["price_b"].pct_change()
        strategy_returns = signals.shift(1) * (returns_a - returns_b)

        # Calculate metrics
        total_return = (1 + strategy_returns).prod() - 1
        sharpe_ratio = (
            strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
            if strategy_returns.std() > 0
            else 0.0
        )
        max_drawdown = self._calculate_max_drawdown(strategy_returns)
        win_rate = (strategy_returns > 0).sum() / len(strategy_returns) if len(strategy_returns) > 0 else 0.0
        total_trades = signals.diff().abs().sum()

        return {
            "total_return": float(total_return),
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "win_rate": float(win_rate),
            "total_trades": int(total_trades),
            "strategy_returns": strategy_returns.tolist(),
        }

    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown."""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return float(drawdown.min())

