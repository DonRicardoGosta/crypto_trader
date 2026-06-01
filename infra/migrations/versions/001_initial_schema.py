"""Initial schema with indexes.

Revision ID: 001
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "app_config",
        sa.Column("key", sa.String(128), primary_key=True),
        sa.Column("value", postgresql.JSONB(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "api_credentials",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("exchange", sa.String(32), nullable=False),
        sa.Column("label", sa.String(128), nullable=False),
        sa.Column("api_key_encrypted", sa.Text(), nullable=False),
        sa.Column("api_secret_encrypted", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_api_credentials_exchange", "api_credentials", ["exchange"])
    op.create_index("ix_api_credentials_is_active", "api_credentials", ["is_active"])

    op.create_table(
        "strategies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("strategy_type", sa.String(64), nullable=False),
        sa.Column("mode", sa.String(16), nullable=False),
        sa.Column("enabled", sa.Boolean(), default=False),
        sa.Column("parameters", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_strategies_name", "strategies", ["name"])
    op.create_index("ix_strategies_strategy_type", "strategies", ["strategy_type"])
    op.create_index("ix_strategies_enabled_mode", "strategies", ["enabled", "mode"])

    op.create_table(
        "strategy_risk",
        sa.Column("strategy_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("max_capital_usd", sa.Numeric(20, 8), nullable=False),
        sa.Column("min_investment_usd", sa.Numeric(20, 8), nullable=False),
        sa.Column("leverage_multiplier", sa.Integer(), nullable=False),
        sa.Column("max_leverage_multiplier", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("strategy_id", postgresql.UUID(as_uuid=True)),
        sa.Column("client_order_id", sa.String(64), unique=True),
        sa.Column("exchange_order_id", sa.String(64)),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("side", sa.String(8), nullable=False),
        sa.Column("order_type", sa.String(16), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("quantity", sa.Numeric(20, 8), nullable=False),
        sa.Column("filled_qty", sa.Numeric(20, 8), default=0),
        sa.Column("price", sa.Numeric(20, 8)),
        sa.Column("avg_price", sa.Numeric(20, 8)),
        sa.Column("raw_response", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_orders_strategy_created", "orders", ["strategy_id", "created_at"])
    op.create_index("ix_orders_symbol", "orders", ["symbol"])
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_client_order_id", "orders", ["client_order_id"])
    op.create_index("ix_orders_exchange_order_id", "orders", ["exchange_order_id"])

    op.create_table(
        "fills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", postgresql.UUID(as_uuid=True)),
        sa.Column("fill_id", sa.String(64), unique=True),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("side", sa.String(8), nullable=False),
        sa.Column("quantity", sa.Numeric(20, 8), nullable=False),
        sa.Column("price", sa.Numeric(20, 8), nullable=False),
        sa.Column("fee", sa.Numeric(20, 8), default=0),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_fills_order_id", "fills", ["order_id"])
    op.create_index("ix_fills_symbol_ts", "fills", ["symbol", "ts"])
    op.create_index("ix_fills_fill_id", "fills", ["fill_id"])

    op.create_table(
        "positions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("strategy_id", postgresql.UUID(as_uuid=True)),
        sa.Column("leg_id", sa.String(64), unique=True),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("side", sa.String(8), nullable=False),
        sa.Column("quantity", sa.Numeric(20, 8), nullable=False),
        sa.Column("entry_price", sa.Numeric(20, 8), nullable=False),
        sa.Column("unrealized_pnl", sa.Numeric(20, 8), default=0),
        sa.Column("ladder_step", sa.Integer(), default=0),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_positions_strategy_symbol", "positions", ["strategy_id", "symbol"])
    op.create_index("ix_positions_leg_id", "positions", ["leg_id"])

    op.create_table(
        "market_snapshots",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("last_price", sa.Numeric(20, 8), nullable=False),
        sa.Column("volume_24h", sa.Numeric(20, 8)),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_market_snapshots_symbol_ts", "market_snapshots", ["symbol", "ts"])

    op.create_table(
        "events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("strategy_id", postgresql.UUID(as_uuid=True)),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_events_type_ts", "events", ["event_type", "ts"])
    op.create_index("ix_events_strategy_ts", "events", ["strategy_id", "ts"])
    op.create_index("ix_events_event_type", "events", ["event_type"])

    op.create_table(
        "errors",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("source", sa.String(64), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("details", postgresql.JSONB()),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_errors_source_ts", "errors", ["source", "ts"])
    op.create_index("ix_errors_severity_ts", "errors", ["severity", "ts"])
    op.create_index("ix_errors_source", "errors", ["source"])

    op.create_table(
        "backtest_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("strategy_id", postgresql.UUID(as_uuid=True)),
        sa.Column("start_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("parameters", postgresql.JSONB(), server_default="{}"),
        sa.Column("result_summary", postgresql.JSONB()),
        sa.Column("status", sa.String(32), default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_backtest_runs_strategy", "backtest_runs", ["strategy_id"])
    op.create_index("ix_backtest_runs_status", "backtest_runs", ["status"])


def downgrade() -> None:
    for table in (
        "backtest_runs",
        "errors",
        "events",
        "market_snapshots",
        "positions",
        "fills",
        "orders",
        "strategy_risk",
        "strategies",
        "api_credentials",
        "app_config",
    ):
        op.drop_table(table)
