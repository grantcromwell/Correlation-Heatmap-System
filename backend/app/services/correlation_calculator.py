"""Correlation calculation service."""
import pandas as pd
from scipy.stats import pearsonr, spearmanr


class CorrelationCalculator:
    """Service for calculating correlations between price series."""

    MIN_DATA_POINTS = 30  # Minimum data points required for correlation

    def calculate_pearson(
        self, series_a: pd.Series, series_b: pd.Series
    ) -> tuple[float, float]:
        """
        Calculate Pearson correlation coefficient.

        Args:
            series_a: First price series
            series_b: Second price series

        Returns:
            Tuple of (correlation, p_value)

        Raises:
            ValueError: If insufficient data points
        """
        # Align and remove NaN values
        aligned = pd.DataFrame({"a": series_a, "b": series_b}).dropna()

        if len(aligned) < self.MIN_DATA_POINTS:
            raise ValueError(
                f"Insufficient data points: {len(aligned)} < {self.MIN_DATA_POINTS}"
            )

        corr, p_value = pearsonr(aligned["a"], aligned["b"])

        # Handle NaN results
        if pd.isna(corr) or pd.isna(p_value):
            raise ValueError("Correlation calculation resulted in NaN")

        return float(corr), float(p_value)

    def calculate_spearman(
        self, series_a: pd.Series, series_b: pd.Series
    ) -> tuple[float, float]:
        """
        Calculate Spearman rank correlation coefficient.

        Args:
            series_a: First price series
            series_b: Second price series

        Returns:
            Tuple of (correlation, p_value)

        Raises:
            ValueError: If insufficient data points
        """
        # Align and remove NaN values
        aligned = pd.DataFrame({"a": series_a, "b": series_b}).dropna()

        if len(aligned) < self.MIN_DATA_POINTS:
            raise ValueError(
                f"Insufficient data points: {len(aligned)} < {self.MIN_DATA_POINTS}"
            )

        corr, p_value = spearmanr(aligned["a"], aligned["b"])

        # Handle NaN results
        if pd.isna(corr) or pd.isna(p_value):
            raise ValueError("Correlation calculation resulted in NaN")

        return float(corr), float(p_value)

    def calculate_rolling_correlation(
        self,
        series_a: pd.Series,
        series_b: pd.Series,
        window: int = 252,
        method: str = "pearson",
    ) -> pd.Series:
        """
        Calculate rolling window correlation.

        Args:
            series_a: First price series
            series_b: Second price series
            window: Rolling window size (default: 252 trading days)
            method: Correlation method ('pearson' or 'spearman')

        Returns:
            Series of rolling correlations
        """
        # Align and remove NaN values
        aligned = pd.DataFrame({"a": series_a, "b": series_b}).dropna()

        if len(aligned) < window:
            raise ValueError(f"Insufficient data points: {len(aligned)} < {window}")

        if method == "pearson":
            rolling_corr = aligned["a"].rolling(window).corr(aligned["b"])
        elif method == "spearman":
            # Spearman rolling correlation requires rank transformation
            rolling_corr = (
                aligned["a"].rolling(window).apply(
                    lambda x: spearmanr(x, aligned["b"].loc[x.index])[0]
                    if len(x) == window
                    else pd.NA
                )
            )
        else:
            raise ValueError(f"Unknown correlation method: {method}")

        return rolling_corr

    def calculate_returns(self, price_series: pd.Series) -> pd.Series:
        """
        Calculate returns from price series.

        Args:
            price_series: Price series

        Returns:
            Returns series
        """
        return price_series.pct_change().dropna()

    def calculate_log_returns(self, price_series: pd.Series) -> pd.Series:
        """
        Calculate log returns from price series.

        Args:
            price_series: Price series

        Returns:
            Log returns series
        """
        import numpy as np
        return pd.Series(np.log(price_series / price_series.shift(1))).dropna()

