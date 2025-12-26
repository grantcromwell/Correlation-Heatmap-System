"""Temporal activity for calculating correlations."""
from typing import Dict, List

from temporalio import activity

from app.services.correlation_calculator import CorrelationCalculator


@activity.defn
async def calculate_correlations_activity(
    price_data: Dict, min_correlation: float
) -> List[Dict]:
    """Calculate correlations for all instrument pairs."""
    import pandas as pd

    calculator = CorrelationCalculator()
    correlations = []

    asset_classes = list(price_data.keys())
    for i, asset_class_a in enumerate(asset_classes):
        for asset_class_b in asset_classes[i:]:
            symbols_a = list(price_data[asset_class_a].keys())
            symbols_b = list(price_data[asset_class_b].keys())

            for symbol_a in symbols_a:
                for symbol_b in symbols_b:
                    if symbol_a == symbol_b:
                        continue

                    try:
                        df_a = pd.DataFrame(price_data[asset_class_a][symbol_a])
                        df_b = pd.DataFrame(price_data[asset_class_b][symbol_b])

                        series_a = pd.Series(df_a["close"])
                        series_b = pd.Series(df_b["close"])

                        corr, p_value = calculator.calculate_pearson(series_a, series_b)

                        if abs(corr) >= min_correlation:
                            correlations.append(
                                {
                                    "instrument_a": symbol_a,
                                    "instrument_b": symbol_b,
                                    "correlation": corr,
                                    "p_value": p_value,
                                }
                            )
                    except Exception:
                        continue

    return correlations

