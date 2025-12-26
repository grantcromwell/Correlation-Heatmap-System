"""initial_schema

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create instruments table
    op.create_table(
        "instruments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("asset_class", sa.String(length=50), nullable=False),
        sa.Column("data_source", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_instruments_asset_class"), "instruments", ["asset_class"], unique=False)
    op.create_index(op.f("ix_instruments_symbol"), "instruments", ["symbol"], unique=True)

    # Create correlations table (will be converted to hypertable)
    op.create_table(
        "correlations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("instrument_a_id", sa.Integer(), nullable=False),
        sa.Column("instrument_b_id", sa.Integer(), nullable=False),
        sa.Column("correlation_value", sa.Float(), nullable=False),
        sa.Column("p_value", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("lookback_days", sa.Integer(), nullable=False),
        sa.Column("method", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(["instrument_a_id"], ["instruments.id"],),
        sa.ForeignKeyConstraint(["instrument_b_id"], ["instruments.id"],),
        sa.PrimaryKeyConstraint("id", "timestamp"),
        sa.UniqueConstraint("instrument_a_id", "instrument_b_id", "timestamp", name="uq_correlation_pair_time"),
    )
    op.create_index(op.f("ix_correlations_instrument_a_id"), "correlations", ["instrument_a_id"], unique=False)
    op.create_index(op.f("ix_correlations_instrument_b_id"), "correlations", ["instrument_b_id"], unique=False)
    op.create_index(op.f("ix_correlations_timestamp"), "correlations", ["timestamp"], unique=False)

    # Create discovered_correlations table
    op.create_table(
        "discovered_correlations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("instrument_a_id", sa.Integer(), nullable=False),
        sa.Column("instrument_b_id", sa.Integer(), nullable=False),
        sa.Column("correlation_value", sa.Float(), nullable=False),
        sa.Column("p_value", sa.Float(), nullable=False),
        sa.Column("h3_index", sa.String(length=20), nullable=False),
        sa.Column("discovered_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("backtest_results", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("spanning_tree_node_id", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["instrument_a_id"], ["instruments.id"],),
        sa.ForeignKeyConstraint(["instrument_b_id"], ["instruments.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_discovered_correlations_discovered_at"), "discovered_correlations", ["discovered_at"], unique=False)
    op.create_index(op.f("ix_discovered_correlations_h3_index"), "discovered_correlations", ["h3_index"], unique=False)
    op.create_index(op.f("ix_discovered_correlations_instrument_a_id"), "discovered_correlations", ["instrument_a_id"], unique=False)
    op.create_index(op.f("ix_discovered_correlations_instrument_b_id"), "discovered_correlations", ["instrument_b_id"], unique=False)
    op.create_index(op.f("ix_discovered_correlations_spanning_tree_node_id"), "discovered_correlations", ["spanning_tree_node_id"], unique=False)
    op.create_index(op.f("ix_discovered_correlations_status"), "discovered_correlations", ["status"], unique=False)

    # Create backtest_results table
    op.create_table(
        "backtest_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("discovered_correlation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("instrument_a_id", sa.Integer(), nullable=False),
        sa.Column("instrument_b_id", sa.Integer(), nullable=False),
        sa.Column("strategy", sa.String(length=50), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=False),
        sa.Column("total_return", sa.Float(), nullable=False),
        sa.Column("sharpe_ratio", sa.Float(), nullable=False),
        sa.Column("max_drawdown", sa.Float(), nullable=False),
        sa.Column("win_rate", sa.Float(), nullable=False),
        sa.Column("total_trades", sa.Integer(), nullable=False),
        sa.Column("lorenz_analysis", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["discovered_correlation_id"], ["discovered_correlations.id"],),
        sa.ForeignKeyConstraint(["instrument_a_id"], ["instruments.id"],),
        sa.ForeignKeyConstraint(["instrument_b_id"], ["instruments.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_backtest_results_discovered_correlation_id"), "backtest_results", ["discovered_correlation_id"], unique=False)
    op.create_index(op.f("ix_backtest_results_instrument_a_id"), "backtest_results", ["instrument_a_id"], unique=False)
    op.create_index(op.f("ix_backtest_results_instrument_b_id"), "backtest_results", ["instrument_b_id"], unique=False)

    # Create decoupling_events table
    op.create_table(
        "decoupling_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("instrument_a_id", sa.Integer(), nullable=False),
        sa.Column("instrument_b_id", sa.Integer(), nullable=False),
        sa.Column("correlation_before", sa.Float(), nullable=False),
        sa.Column("correlation_after", sa.Float(), nullable=False),
        sa.Column("decoupling_date", sa.DateTime(), nullable=False),
        sa.Column("lorenz_metrics", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("h3_index", sa.String(length=20), nullable=False),
        sa.Column("detected_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["instrument_a_id"], ["instruments.id"],),
        sa.ForeignKeyConstraint(["instrument_b_id"], ["instruments.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_decoupling_events_decoupling_date"), "decoupling_events", ["decoupling_date"], unique=False)
    op.create_index(op.f("ix_decoupling_events_h3_index"), "decoupling_events", ["h3_index"], unique=False)
    op.create_index(op.f("ix_decoupling_events_instrument_a_id"), "decoupling_events", ["instrument_a_id"], unique=False)
    op.create_index(op.f("ix_decoupling_events_instrument_b_id"), "decoupling_events", ["instrument_b_id"], unique=False)

    # Create h3_clusters table
    op.create_table(
        "h3_clusters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("h3_index", sa.String(length=20), nullable=False),
        sa.Column("resolution", sa.Integer(), nullable=False),
        sa.Column("correlation_count", sa.Integer(), nullable=False),
        sa.Column("avg_correlation", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_h3_clusters_h3_index"), "h3_clusters", ["h3_index"], unique=True)

    # Create spanning_tree_nodes table
    op.create_table(
        "spanning_tree_nodes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("node_id", sa.String(length=100), nullable=False),
        sa.Column("instrument_id", sa.Integer(), nullable=False),
        sa.Column("fiass_score", sa.Float(), nullable=False),
        sa.Column("parent_node_id", sa.String(length=100), nullable=True),
        sa.Column("tree_path", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["instrument_id"], ["instruments.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_spanning_tree_nodes_instrument_id"), "spanning_tree_nodes", ["instrument_id"], unique=False)
    op.create_index(op.f("ix_spanning_tree_nodes_node_id"), "spanning_tree_nodes", ["node_id"], unique=True)
    op.create_index(op.f("ix_spanning_tree_nodes_parent_node_id"), "spanning_tree_nodes", ["parent_node_id"], unique=False)

    # Create TimescaleDB hypertable for correlations
    # Note: This requires TimescaleDB extension to be installed
    op.execute("SELECT create_hypertable('correlations', 'timestamp', if_not_exists => TRUE);")


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("spanning_tree_nodes")
    op.drop_table("h3_clusters")
    op.drop_table("decoupling_events")
    op.drop_table("backtest_results")
    op.drop_table("discovered_correlations")
    op.drop_table("correlations")
    op.drop_table("instruments")

