"""SQLAlchemy ORM models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AppConfigRow(Base):
    __tablename__ = "app_config"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ApiCredentialRow(Base):
    __tablename__ = "api_credentials"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exchange: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    api_key_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    api_secret_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class StrategyRow(Base):
    __tablename__ = "strategies"
    __table_args__ = (Index("ix_strategies_enabled_mode", "enabled", "mode"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    strategy_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    mode: Mapped[str] = mapped_column(String(16), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    parameters: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class StrategyRiskRow(Base):
    __tablename__ = "strategy_risk"

    strategy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True
    )
    max_capital_usd: Mapped[float] = mapped_column(Numeric(20, 8), nullable=False)
    min_investment_usd: Mapped[float] = mapped_column(Numeric(20, 8), nullable=False)
    leverage_multiplier: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_leverage_multiplier: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class OrderRow(Base):
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_strategy_created", "strategy_id", "created_at"),
        Index("ix_orders_symbol", "symbol"),
        Index("ix_orders_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), index=True)
    client_order_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    exchange_order_id: Mapped[str | None] = mapped_column(String(64), index=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    order_type: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(20, 8), nullable=False)
    filled_qty: Mapped[float] = mapped_column(Numeric(20, 8), default=0)
    price: Mapped[float | None] = mapped_column(Numeric(20, 8))
    avg_price: Mapped[float | None] = mapped_column(Numeric(20, 8))
    raw_response: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class FillRow(Base):
    __tablename__ = "fills"
    __table_args__ = (
        Index("ix_fills_order_id", "order_id"),
        Index("ix_fills_symbol_ts", "symbol", "ts"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    fill_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(20, 8), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(20, 8), nullable=False)
    fee: Mapped[float] = mapped_column(Numeric(20, 8), default=0)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class PositionRow(Base):
    __tablename__ = "positions"
    __table_args__ = (Index("ix_positions_strategy_symbol", "strategy_id", "symbol"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    leg_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(20, 8), nullable=False)
    entry_price: Mapped[float] = mapped_column(Numeric(20, 8), nullable=False)
    unrealized_pnl: Mapped[float] = mapped_column(Numeric(20, 8), default=0)
    ladder_step: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class MarketSnapshotRow(Base):
    __tablename__ = "market_snapshots"
    __table_args__ = (Index("ix_market_snapshots_symbol_ts", "symbol", "ts"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    last_price: Mapped[float] = mapped_column(Numeric(20, 8), nullable=False)
    volume_24h: Mapped[float | None] = mapped_column(Numeric(20, 8))
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class EventRow(Base):
    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_type_ts", "event_type", "ts"),
        Index("ix_events_strategy_ts", "strategy_id", "ts"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    strategy_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class ErrorRow(Base):
    __tablename__ = "errors"
    __table_args__ = (
        Index("ix_errors_source_ts", "source", "ts"),
        Index("ix_errors_severity_ts", "severity", "ts"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class BacktestRunRow(Base):
    __tablename__ = "backtest_runs"
    __table_args__ = (Index("ix_backtest_runs_strategy", "strategy_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    start_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    parameters: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    result_summary: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
