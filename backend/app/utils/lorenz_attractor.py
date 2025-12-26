"""Lorenz attractor implementation for decoupling detection."""
import numpy as np
import pandas as pd
from scipy.integrate import odeint


class LorenzAttractor:
    """Lorenz attractor for financial decoupling detection."""

    def __init__(self, sigma: float = 10.0, rho: float = 28.0, beta: float = 8.0 / 3.0):
        """
        Initialize Lorenz attractor with parameters.

        Args:
            sigma: Prandtl number (default: 10.0)
            rho: Rayleigh number (default: 28.0)
            beta: Geometric factor (default: 8/3)
        """
        self.sigma = sigma
        self.rho = rho
        self.beta = beta

    def lorenz_equations(self, state: np.ndarray, t: float) -> np.ndarray:
        """
        Lorenz system differential equations.

        Args:
            state: Current state [x, y, z]
            t: Time

        Returns:
            Derivatives [dx/dt, dy/dt, dz/dt]
        """
        x, y, z = state
        dx_dt = self.sigma * (y - x)
        dy_dt = x * (self.rho - z) - y
        dz_dt = x * y - self.beta * z
        return np.array([dx_dt, dy_dt, dz_dt])

    def map_prices_to_phase_space(
        self, price_series_a: pd.Series, price_series_b: pd.Series
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        """
        Map two price series to Lorenz phase space coordinates.

        Args:
            price_series_a: First instrument price series
            price_series_b: Second instrument price series

        Returns:
            Tuple of (x, y, z) phase space coordinates
        """
        # Normalize price series
        norm_a = (price_series_a - price_series_a.mean()) / price_series_a.std()
        norm_b = (price_series_b - price_series_b.mean()) / price_series_b.std()

        # Calculate returns
        returns_a = price_series_a.pct_change().dropna()
        returns_b = price_series_b.pct_change().dropna()

        # Align series
        aligned = pd.DataFrame({"a": returns_a, "b": returns_b}).dropna()

        # Map to phase space
        # x: normalized price difference
        x = norm_a - norm_b

        # y: return difference
        y = aligned["a"] - aligned["b"]

        # z: volatility measure (rolling std of returns)
        z = aligned["a"].rolling(window=20).std() - aligned["b"].rolling(window=20).std()

        # Align all series
        aligned_xyz = pd.DataFrame({"x": x, "y": y, "z": z}).dropna()

        return aligned_xyz["x"], aligned_xyz["y"], aligned_xyz["z"]

    def calculate_trajectory(
        self, x: pd.Series, y: pd.Series, z: pd.Series, t_span: np.ndarray | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Calculate Lorenz attractor trajectory.

        Args:
            x: X phase space coordinates
            y: Y phase space coordinates
            z: Z phase space coordinates
            t_span: Time span for integration

        Returns:
            Tuple of (time_points, trajectory_states)
        """
        if t_span is None:
            t_span = np.linspace(0, 100, len(x))

        # Initial state from first data point
        initial_state = np.array([x.iloc[0], y.iloc[0], z.iloc[0]])

        # Integrate Lorenz equations
        trajectory = odeint(self.lorenz_equations, initial_state, t_span)

        return t_span, trajectory

    def detect_decoupling(
        self,
        price_series_a: pd.Series,
        price_series_b: pd.Series,
        threshold: float = 0.3,
    ) -> dict:
        """
        Detect decoupling between two price series using Lorenz attractor.

        Args:
            price_series_a: First instrument price series
            price_series_b: Second instrument price series
            threshold: Decoupling threshold (default: 0.3)

        Returns:
            Dictionary with decoupling metrics
        """
        # Map to phase space
        x, y, z = self.map_prices_to_phase_space(price_series_a, price_series_b)

        # Calculate trajectory
        t_span, trajectory = self.calculate_trajectory(x, y, z)

        # Calculate attractor distance (how far from expected trajectory)
        # Use Euclidean distance from initial state
        initial_state = trajectory[0]
        distances = np.linalg.norm(trajectory - initial_state, axis=1)

        # Detect divergence
        max_distance = np.max(distances)
        avg_distance = np.mean(distances)

        # Stability index (lower = more stable)
        stability_index = np.std(distances) / (avg_distance + 1e-10)

        # Regime change probability based on distance and stability
        regime_change_probability = min(1.0, max_distance / threshold)

        decoupling_detected = regime_change_probability > threshold

        return {
            "decoupling_detected": decoupling_detected,
            "attractor_distance": float(max_distance),
            "stability_index": float(stability_index),
            "regime_change_probability": float(regime_change_probability),
            "trajectory": trajectory.tolist(),
            "distances": distances.tolist(),
        }

