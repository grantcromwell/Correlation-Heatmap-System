"""SQLAlchemy database models."""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class Instrument(Base):
    """Financial instrument model."""

    __tablename__ = "instruments"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    asset_class: Mapped[str] = mapped_column(String(50), index=True)
    data_source: Mapped[str] = mapped_column(String(50))
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    correlations_a: Mapped[list["Correlation"]] = relationship(
        "Correlation",
        foreign_keys="Correlation.instrument_a_id",
        back_populates="instrument_a",
    )
    correlations_b: Mapped[list["Correlation"]] = relationship(
        "Correlation",
        foreign_keys="Correlation.instrument_b_id",
        back_populates="instrument_b",
    )

    def __repr__(self) -> str:
        return f"<Instrument(id={self.id}, symbol={self.symbol}, asset_class={self.asset_class})>"


class Correlation(Base):
    """Correlation time-series model (TimescaleDB hypertable)."""

    __tablename__ = "correlations"

    id: Mapped[int] = mapped_column(primary_key=True)
    instrument_a_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    instrument_b_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    correlation_value: Mapped[float] = mapped_column(Float)
    p_value: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime, primary_key=True, index=True)
    lookback_days: Mapped[int] = mapped_column(Integer, default=252)
    method: Mapped[str] = mapped_column(String(20), default="pearson")  # pearson or spearman

    # Relationships
    instrument_a: Mapped["Instrument"] = relationship(
        "Instrument", foreign_keys=[instrument_a_id], back_populates="correlations_a"
    )
    instrument_b: Mapped["Instrument"] = relationship(
        "Instrument", foreign_keys=[instrument_b_id], back_populates="correlations_b"
    )

    __table_args__ = (
        UniqueConstraint("instrument_a_id", "instrument_b_id", "timestamp", name="uq_correlation_pair_time"),
    )

    def __repr__(self) -> str:
        return (
            f"<Correlation(instrument_a_id={self.instrument_a_id}, "
            f"instrument_b_id={self.instrument_b_id}, "
            f"correlation={self.correlation_value:.3f}, "
            f"timestamp={self.timestamp})>"
        )


class DiscoveredCorrelation(Base):
    """Discovered correlation model with backtest results and H3 indexing."""

    __tablename__ = "discovered_correlations"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    instrument_a_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    instrument_b_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    correlation_value: Mapped[float] = mapped_column(Float)
    p_value: Mapped[float] = mapped_column(Float)
    h3_index: Mapped[str] = mapped_column(String(20), index=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    status: Mapped[str] = mapped_column(String(20), default="new", index=True)  # new, validated, decayed
    backtest_results: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    spanning_tree_node_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # Relationships
    instrument_a: Mapped["Instrument"] = relationship("Instrument", foreign_keys=[instrument_a_id])
    instrument_b: Mapped["Instrument"] = relationship("Instrument", foreign_keys=[instrument_b_id])

    def __repr__(self) -> str:
        return (
            f"<DiscoveredCorrelation(id={self.id}, "
            f"instrument_a_id={self.instrument_a_id}, "
            f"instrument_b_id={self.instrument_b_id}, "
            f"correlation={self.correlation_value:.3f}, "
            f"status={self.status})>"
        )


class BacktestResult(Base):
    """Backtest result model."""

    __tablename__ = "backtest_results"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    discovered_correlation_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("discovered_correlations.id"), nullable=True, index=True
    )
    instrument_a_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    instrument_b_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    strategy: Mapped[str] = mapped_column(String(50))  # pairs_trading, momentum, mean_reversion
    start_date: Mapped[datetime] = mapped_column(DateTime)
    end_date: Mapped[datetime] = mapped_column(DateTime)
    total_return: Mapped[float] = mapped_column(Float)
    sharpe_ratio: Mapped[float] = mapped_column(Float)
    max_drawdown: Mapped[float] = mapped_column(Float)
    win_rate: Mapped[float] = mapped_column(Float)
    total_trades: Mapped[int] = mapped_column(Integer)
    lorenz_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    discovered_correlation: Mapped["DiscoveredCorrelation | None"] = relationship(
        "DiscoveredCorrelation", backref="backtest_results"
    )

    def __repr__(self) -> str:
        return (
            f"<BacktestResult(id={self.id}, "
            f"strategy={self.strategy}, "
            f"total_return={self.total_return:.3f}, "
            f"sharpe_ratio={self.sharpe_ratio:.3f})>"
        )


class DecouplingEvent(Base):
    """Decoupling event detected using Lorenz attractor."""

    __tablename__ = "decoupling_events"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    instrument_a_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    instrument_b_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    correlation_before: Mapped[float] = mapped_column(Float)
    correlation_after: Mapped[float] = mapped_column(Float)
    decoupling_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    lorenz_metrics: Mapped[dict] = mapped_column(JSON)
    h3_index: Mapped[str] = mapped_column(String(20), index=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    instrument_a: Mapped["Instrument"] = relationship("Instrument", foreign_keys=[instrument_a_id])
    instrument_b: Mapped["Instrument"] = relationship("Instrument", foreign_keys=[instrument_b_id])

    def __repr__(self) -> str:
        return (
            f"<DecouplingEvent(id={self.id}, "
            f"correlation_before={self.correlation_before:.3f}, "
            f"correlation_after={self.correlation_after:.3f}, "
            f"decoupling_date={self.decoupling_date})>"
        )


class H3Cluster(Base):
    """H3 cluster model for grouping correlations."""

    __tablename__ = "h3_clusters"

    id: Mapped[int] = mapped_column(primary_key=True)
    h3_index: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    resolution: Mapped[int] = mapped_column(Integer)
    correlation_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_correlation: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return (
            f"<H3Cluster(id={self.id}, "
            f"h3_index={self.h3_index}, "
            f"correlation_count={self.correlation_count}, "
            f"avg_correlation={self.avg_correlation:.3f})>"
        )


class SpanningTreeNode(Base):
    """Spanning tree node model with FIASS scores."""

    __tablename__ = "spanning_tree_nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    node_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    fiass_score: Mapped[float] = mapped_column(Float)
    parent_node_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    tree_path: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    instrument: Mapped["Instrument"] = relationship("Instrument")

    def __repr__(self) -> str:
        return (
            f"<SpanningTreeNode(id={self.id}, "
            f"node_id={self.node_id}, "
            f"instrument_id={self.instrument_id}, "
            f"fiass_score={self.fiass_score:.3f})>"
        )

