"""FIASS (Financial Instrument Asset Scoring System) calculator."""
import pandas as pd


class FIASSCalculator:
    """Calculator for FIASS scores."""

    # Component weights
    LIQUIDITY_WEIGHT = 0.30
    VOLATILITY_WEIGHT = 0.20
    STABILITY_WEIGHT = 0.30
    MARKET_CAP_WEIGHT = 0.20

    def calculate_liquidity_score(
        self,
        avg_daily_volume: float,
        bid_ask_spread_pct: float,
        volume_cv: float,  # Coefficient of variation
    ) -> float:
        """
        Calculate liquidity score (0-10).

        Args:
            avg_daily_volume: Average daily volume
            bid_ask_spread_pct: Bid-ask spread as percentage
            volume_cv: Coefficient of variation of volumes

        Returns:
            Liquidity score (0-10)
        """
        # Normalize ADV (simplified - in production, use percentile ranking)
        adv_score = min(10.0, avg_daily_volume / 1_000_000)  # Normalize to millions

        # Spread score (lower is better)
        spread_score = 10.0 * (1.0 - min(bid_ask_spread_pct / 0.01, 1.0))  # 1% max spread

        # Volume consistency score (lower CV is better)
        consistency_score = 10.0 * (1.0 - min(volume_cv, 1.0))

        # Weighted average
        liquidity_score = (adv_score * 0.4 + spread_score * 0.4 + consistency_score * 0.2)
        return max(0.0, min(10.0, liquidity_score))

    def calculate_volatility_score(self, realized_volatility: float) -> float:
        """
        Calculate volatility score (0-10).

        Args:
            realized_volatility: Annualized realized volatility

        Returns:
            Volatility score (0-10)
        """
        # Optimal volatility range: 0.15-0.30 (15%-30% annual)
        if 0.15 <= realized_volatility <= 0.30:
            return 10.0
        elif realized_volatility < 0.15:
            # Too low volatility (less trading opportunity)
            return 10.0 * (realized_volatility / 0.15)
        else:
            # Too high volatility (higher risk)
            return max(0.0, 10.0 * (1.0 - (realized_volatility - 0.30) / 0.30))

    def calculate_stability_score(
        self, correlation_stability: float, lookback_periods: int = 252
    ) -> float:
        """
        Calculate correlation stability score (0-10).

        Args:
            correlation_stability: Standard deviation of rolling correlations
            lookback_periods: Number of periods used for calculation

        Returns:
            Stability score (0-10)
        """
        # Lower standard deviation = higher stability
        # Normalize: 0.1 std dev = perfect stability (score 10)
        stability_score = 10.0 * (1.0 - min(correlation_stability / 0.1, 1.0))
        return max(0.0, min(10.0, stability_score))

    def calculate_market_cap_score(self, market_cap: float, asset_class: str) -> float:
        """
        Calculate market cap score (0-10).

        Args:
            market_cap: Market capitalization
            asset_class: Asset class for normalization

        Returns:
            Market cap score (0-10)
        """
        # Normalize by asset class
        thresholds = {
            "crypto": 10_000_000_000,  # $10B
            "equity": 100_000_000_000,  # $100B
            "tech": 500_000_000_000,  # $500B
            "metals": 50_000_000_000,  # $50B
            "forex": 1_000_000_000_000,  # $1T (forex market size)
        }

        threshold = thresholds.get(asset_class, 100_000_000_000)
        score = min(10.0, (market_cap / threshold) * 10.0)
        return max(0.0, score)

    def calculate_composite_score(
        self,
        liquidity_score: float,
        volatility_score: float,
        stability_score: float,
        market_cap_score: float,
    ) -> float:
        """
        Calculate composite FIASS score (0-10).

        Args:
            liquidity_score: Liquidity component score
            volatility_score: Volatility component score
            stability_score: Stability component score
            market_cap_score: Market cap component score

        Returns:
            Composite FIASS score (0-10)
        """
        composite = (
            liquidity_score * self.LIQUIDITY_WEIGHT
            + volatility_score * self.VOLATILITY_WEIGHT
            + stability_score * self.STABILITY_WEIGHT
            + market_cap_score * self.MARKET_CAP_WEIGHT
        )
        return max(0.0, min(10.0, composite))

