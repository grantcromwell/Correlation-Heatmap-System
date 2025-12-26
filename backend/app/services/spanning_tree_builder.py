"""Spanning tree builder for correlation network."""
from typing import List

import networkx as nx

from app.database.models import Correlation


class SpanningTreeBuilder:
    """Builder for minimum spanning tree from correlation data."""

    def build_tree(
        self, correlations: List[Correlation], min_correlation: float = 0.7
    ) -> nx.Graph:
        """
        Build minimum spanning tree from correlations.

        Args:
            correlations: List of correlation objects
            min_correlation: Minimum correlation to include

        Returns:
            Minimum spanning tree graph
        """
        # Create graph
        G = nx.Graph()

        # Add edges for correlations above threshold
        for corr in correlations:
            if corr.correlation_value >= min_correlation:
                # Weight = 1 - correlation (lower weight = stronger correlation)
                weight = 1.0 - corr.correlation_value
                G.add_edge(
                    corr.instrument_a_id,
                    corr.instrument_b_id,
                    weight=weight,
                    correlation=corr.correlation_value,
                )

        # Find minimum spanning tree
        if G.number_of_nodes() > 0:
            mst = nx.minimum_spanning_tree(G, weight="weight")
            return mst
        else:
            return G

    def get_tree_structure(self, mst: nx.Graph) -> dict:
        """
        Get tree structure representation.

        Args:
            mst: Minimum spanning tree graph

        Returns:
            Dictionary with tree structure
        """
        if mst.number_of_nodes() == 0:
            return {"root": None, "branches": []}

        # Find root (node with highest degree or first node)
        root = max(mst.nodes(), key=lambda n: mst.degree(n))

        # Build tree paths
        branches = []
        for node in mst.nodes():
            if node != root:
                try:
                    path = nx.shortest_path(mst, root, node)
                    branches.append({"node": node, "path": path})
                except nx.NetworkXNoPath:
                    pass

        return {"root": root, "branches": branches}

