"""Domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from trading_platform.core.enums import (
    ExecutionMode,
    OrderSide,
    OrderStatus,
    OrderType,
    PositionSide,
)


@dataclass
class OrderIntent:
    """Strategy order proposal before risk check."""

    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Decimal | None = None
    position_side: PositionSide | None = None
    client_order_id: str = field(default_factory=lambda: str(uuid4()))
    reduce_only: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OrderResult:
    """Result after execution port places an order."""

    client_order_id: str
    exchange_order_id: str | None
    status: OrderStatus
    symbol: str
    side: OrderSide
    filled_qty: Decimal
    avg_price: Decimal | None
    message: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Fill:
    """Trade fill."""

    fill_id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: Decimal
    price: Decimal
    fee: Decimal
    ts: datetime


@dataclass
class PositionLeg:
    """Single position leg (supports multi-leg per symbol)."""

    leg_id: str
    symbol: str
    side: PositionSide
    quantity: Decimal
    entry_price: Decimal
    unrealized_pnl: Decimal = Decimal("0")
    ladder_step: int = 0


@dataclass
class Balance:
    """Account balance snapshot."""

    asset: str
    available: Decimal
    frozen: Decimal
    total: Decimal


@dataclass
class Ticker:
    """Market ticker."""

    symbol: str
    last_price: Decimal
    bid: Decimal | None = None
    ask: Decimal | None = None
    volume_24h: Decimal | None = None
    ts: datetime | None = None


@dataclass
class Kline:
    """OHLCV candle."""

    symbol: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    ts: datetime


@dataclass
class StrategyRiskConfig:
    """Per-strategy risk limits."""

    max_capital_usd: Decimal
    min_investment_usd: Decimal
    leverage_multiplier: int
    max_leverage_multiplier: int


@dataclass
class StrategyConfig:
    """Strategy runtime configuration."""

    id: UUID
    name: str
    strategy_type: str
    mode: ExecutionMode
    enabled: bool
    parameters: dict[str, Any]
    risk: StrategyRiskConfig


@dataclass
class RiskDecision:
    """Risk engine decision."""

    approved: bool
    reason: str | None = None
    adjusted_intent: OrderIntent | None = None


@dataclass
class BacktestParams:
    """Backtest run parameters."""

    strategy_id: UUID
    start_ts: datetime
    end_ts: datetime
    symbols: list[str] | None = None
    slippage_bps: int = 0
