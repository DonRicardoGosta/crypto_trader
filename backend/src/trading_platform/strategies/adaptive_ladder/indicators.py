"""Simple technical indicators."""

from __future__ import annotations

from decimal import Decimal

from trading_platform.core.models import Kline


def rsi(klines: list[Kline], period: int = 14) -> Decimal:
    if len(klines) < period + 1:
        return Decimal("50")
    gains = []
    losses = []
    for i in range(-period, 0):
        change = klines[i].close - klines[i - 1].close
        if change > 0:
            gains.append(change)
            losses.append(Decimal("0"))
        else:
            gains.append(Decimal("0"))
            losses.append(abs(change))
    avg_gain = sum(gains) / period if gains else Decimal("0")
    avg_loss = sum(losses) / period if losses else Decimal("1")
    if avg_loss == 0:
        return Decimal("100")
    rs = avg_gain / avg_loss
    return Decimal("100") - (Decimal("100") / (1 + rs))


def volatility_score(klines: list[Kline], period: int = 20) -> Decimal:
    if len(klines) < 2:
        return Decimal("0")
    recent = klines[-period:]
    returns = []
    for i in range(1, len(recent)):
        if recent[i - 1].close > 0:
            r = (recent[i].close - recent[i - 1].close) / recent[i - 1].close
            returns.append(abs(r))
    if not returns:
        return Decimal("0")
    return sum(returns) / len(returns) * Decimal("100")
