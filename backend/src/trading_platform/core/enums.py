"""Shared enumerations."""

from enum import StrEnum


class ExecutionMode(StrEnum):
    LIVE = "live"
    DRY_RUN = "dry_run"
    BACKTEST = "backtest"


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    MARKET = "market"
    LIMIT = "limit"


class PositionSide(StrEnum):
    LONG = "long"
    SHORT = "short"


class OrderStatus(StrEnum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class EventType(StrEnum):
    ORDER = "order"
    FILL = "fill"
    POSITION = "position"
    CONFIG = "config"
    MODE_SWITCH = "mode_switch"
    LEVERAGE_BUMP = "leverage_bump"
    LEVERAGE_BUMP_EXHAUSTED = "leverage_bump_exhausted"
    SYSTEM = "system"


class ErrorSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
