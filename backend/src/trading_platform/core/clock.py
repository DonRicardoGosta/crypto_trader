"""Clock implementations."""

from datetime import UTC, datetime

from trading_platform.core.ports import ClockPort


class WallClock(ClockPort):
    def now(self) -> datetime:
        return datetime.now(UTC)
