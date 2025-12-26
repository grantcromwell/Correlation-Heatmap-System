"""H3 utility functions for correlation clustering."""
import hashlib
from typing import List

import h3


class H3Manager:
    """Manager for H3 hexagonal indexing of correlations."""

    DEFAULT_RESOLUTION = 7

    def correlation_to_h3_index(
        self,
        instrument_a: str,
        instrument_b: str,
        correlation: float,
        resolution: int | None = None,
    ) -> str:
        """
        Convert correlation pair to H3 index.

        Args:
            instrument_a: First instrument symbol
            instrument_b: Second instrument symbol
            correlation: Correlation value
            resolution: H3 resolution (default: adaptive based on correlation)

        Returns:
            H3 index string
        """
        if resolution is None:
            resolution = self._get_resolution_for_correlation(correlation)

        # Create virtual coordinates from instrument characteristics
        # Use hash of instrument pair to create consistent coordinates
        pair_hash = hashlib.md5(f"{instrument_a}:{instrument_b}".encode()).hexdigest()

        # Convert hash to lat/lng (0-180 range)
        lat = (int(pair_hash[:8], 16) % 180) - 90
        lng = (int(pair_hash[8:16], 16) % 360) - 180

        # Adjust based on correlation strength (stronger correlations cluster together)
        correlation_factor = correlation * 10  # Scale to 0-10
        lat += correlation_factor * 0.1
        lng += correlation_factor * 0.1

        # Convert to H3 index
        h3_index = h3.geo_to_h3(lat, lng, resolution)
        return h3_index

    def _get_resolution_for_correlation(self, correlation: float) -> int:
        """
        Get adaptive H3 resolution based on correlation strength.

        Args:
            correlation: Correlation value

        Returns:
            H3 resolution level
        """
        abs_corr = abs(correlation)
        if abs_corr >= 0.9:
            return 9  # Very strong correlation
        elif abs_corr >= 0.8:
            return 8  # Strong correlation
        elif abs_corr >= 0.7:
            return 7  # Moderate correlation (default)
        elif abs_corr >= 0.6:
            return 6  # Weak correlation
        else:
            return 5  # Very weak correlation

    def find_clusters(
        self, h3_indices: List[str], min_correlations: int = 5
    ) -> List[dict]:
        """
        Find clusters of correlations using H3 indices.

        Args:
            h3_indices: List of H3 indices
            min_correlations: Minimum correlations per cluster

        Returns:
            List of cluster dictionaries
        """
        # Count correlations per H3 index
        cluster_counts: dict[str, int] = {}
        for h3_index in h3_indices:
            cluster_counts[h3_index] = cluster_counts.get(h3_index, 0) + 1

        # Filter clusters by minimum count
        clusters = []
        for h3_index, count in cluster_counts.items():
            if count >= min_correlations:
                # Get neighbors
                neighbors = h3.k_ring(h3_index, k=1)
                clusters.append(
                    {
                        "h3_index": h3_index,
                        "correlation_count": count,
                        "neighbors": list(neighbors),
                    }
                )

        return clusters

    def get_h3_neighbors(self, h3_index: str, k: int = 1) -> List[str]:
        """
        Get H3 neighbors for spatial queries.

        Args:
            h3_index: H3 index
            k: Ring size

        Returns:
            List of neighbor H3 indices
        """
        return list(h3.k_ring(h3_index, k=k))

