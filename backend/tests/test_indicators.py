from datetime import UTC, datetime
from decimal import Decimal

from trading_platform.core.models import Kline
from trading_platform.strategies.adaptive_ladder.indicators import rsi, volatility_score


def _klines(n):
    return [Kline("X", Decimal(i), Decimal(i)+1, Decimal(i)-1, Decimal(i), Decimal(1), datetime.now(UTC)) for i in range(n)]

def test_rsi_range():
    val = rsi(_klines(30))
    assert Decimal("0") <= val <= Decimal("100")

def test_volatility_non_negative():
    assert volatility_score(_klines(25)) >= Decimal("0")
