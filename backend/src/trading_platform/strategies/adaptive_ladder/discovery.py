"""Automatic coin discovery."""

from __future__ import annotations

from decimal import Decimal

from trading_platform.adapters.bitunix.rest import BitunixRestClient
from trading_platform.core.models import Kline
from trading_platform.strategies.adaptive_ladder.indicators import volatility_score


async def discover_symbols(
    client: BitunixRestClient,
    max_symbols: int = 5,
    min_volume_24h: Decimal = Decimal("1000000"),
    excluded: list[str] | None = None,
) -> list[str]:
    excluded_set = {s.upper() for s in (excluded or [])}
    tickers = await client.get_tickers()
    scored: list[tuple[str, Decimal]] = []

    for t in tickers:
        sym = (t.get("symbol") or t.get("instId", "")).upper()
        if not sym or sym in excluded_set:
            continue
        vol = Decimal(str(t.get("volume") or t.get("vol24h") or t.get("quoteVolume", "0")))
        if vol < min_volume_24h:
            continue
        scored.append((sym, vol))

    scored.sort(key=lambda x: x[1], reverse=True)
    candidates = [s for s, _ in scored[: max_symbols * 3]]

    ranked: list[tuple[str, Decimal]] = []
    for sym in candidates:
        try:
            klines = await client.get_klines(sym, "15min", 30)
            if klines:
                vol_score = volatility_score(klines)
                ranked.append((sym, vol_score))
        except Exception:
            ranked.append((sym, Decimal("0")))

    ranked.sort(key=lambda x: x[1], reverse=True)
    return [s for s, _ in ranked[:max_symbols]]


def rank_with_klines(
    symbols: list[str],
    klines_map: dict[str, list[Kline]],
    volumes: dict[str, Decimal],
) -> list[str]:
    scored: list[tuple[str, Decimal]] = []
    for sym in symbols:
        klines = klines_map.get(sym, [])
        vol_s = volatility_score(klines) if klines else Decimal("0")
        vol24 = volumes.get(sym, Decimal("0"))
        score = vol_s + vol24 / Decimal("10000000")
        scored.append((sym, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [s for s, _ in scored]
