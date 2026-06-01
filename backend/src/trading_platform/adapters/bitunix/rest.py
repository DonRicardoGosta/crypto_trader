"""Bitunix REST client."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from urllib.parse import urlencode

import httpx

from trading_platform.adapters.bitunix.signing import body_string, sign_request
from trading_platform.core.models import Balance, Kline, Ticker
from trading_platform.core.ports import EventEmitter

logger = logging.getLogger(__name__)

BASE_URL = "https://fapi.bitunix.com"


class BitunixRestClient:
    def __init__(
        self,
        api_key: str = "",
        secret_key: str = "",
        emitter: EventEmitter | None = None,
    ) -> None:
        self._api_key = api_key
        self._secret_key = secret_key
        self._emitter = emitter
        self._client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        signed: bool = False,
    ) -> dict[str, Any]:
        params = params or {}
        query = urlencode(sorted(params.items())) if params else ""
        body_str = body_string(body) if body else ""
        headers: dict[str, str] = {}
        if signed and self._api_key:
            headers = sign_request(self._api_key, self._secret_key, query, body_str)

        url = path if not query else f"{path}?{query}"
        try:
            if method == "GET":
                resp = await self._client.get(url, headers=headers)
            else:
                resp = await self._client.post(url, content=body_str or None, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and data.get("code") not in (None, "0", 0):
                raise BitunixApiError(data.get("msg", "Unknown error"), data)
            return data if isinstance(data, dict) else {"data": data}
        except Exception as e:
            if self._emitter:
                await self._emitter.emit_error("bitunix.rest", str(e), details={"path": path})
            raise

    async def get_tickers(self) -> list[dict[str, Any]]:
        """Public tickers — uses common futures endpoint pattern."""
        data = await self._request("GET", "/api/v1/futures/market/tickers")
        items = data.get("data", data)
        if isinstance(items, list):
            return items
        return items.get("list", []) if isinstance(items, dict) else []

    async def get_ticker(self, symbol: str) -> Ticker:
        tickers = await self.get_tickers()
        for t in tickers:
            sym = t.get("symbol") or t.get("instId", "")
            if sym.upper() == symbol.upper():
                return Ticker(
                    symbol=sym,
                    last_price=Decimal(str(t.get("lastPrice") or t.get("last", "0"))),
                    volume_24h=Decimal(str(t.get("volume") or t.get("vol24h", "0"))),
                    ts=datetime.now(UTC),
                )
        return Ticker(symbol=symbol, last_price=Decimal("0"), ts=datetime.now(UTC))

    async def get_klines(
        self,
        symbol: str,
        interval: str = "1min",
        limit: int = 100,
    ) -> list[Kline]:
        data = await self._request(
            "GET",
            "/api/v1/futures/market/kline",
            params={"symbol": symbol, "interval": interval, "limit": limit},
        )
        rows = data.get("data", [])
        klines: list[Kline] = []
        for row in rows:
            if isinstance(row, list) and len(row) >= 6:
                klines.append(
                    Kline(
                        symbol=symbol,
                        open=Decimal(str(row[0])),
                        high=Decimal(str(row[1])),
                        low=Decimal(str(row[2])),
                        close=Decimal(str(row[3])),
                        volume=Decimal(str(row[4])),
                        ts=datetime.fromtimestamp(int(row[5]) / 1000, tz=UTC),
                    )
                )
            elif isinstance(row, dict):
                klines.append(
                    Kline(
                        symbol=symbol,
                        open=Decimal(str(row.get("o", 0))),
                        high=Decimal(str(row.get("h", 0))),
                        low=Decimal(str(row.get("l", 0))),
                        close=Decimal(str(row.get("c", 0))),
                        volume=Decimal(str(row.get("b", 0))),
                        ts=datetime.now(UTC),
                    )
                )
        return klines

    async def place_order(
        self,
        symbol: str,
        side: str,
        qty: str,
        order_type: str = "market",
        price: str | None = None,
        leverage: int = 1,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "symbol": symbol,
            "side": side.upper(),
            "qty": qty,
            "orderType": order_type.upper(),
            "leverage": leverage,
        }
        if price:
            body["price"] = price
        return await self._request(
            "POST", "/api/v1/futures/trade/place_order", body=body, signed=True
        )

    async def cancel_order(self, symbol: str, order_id: str) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/api/v1/futures/trade/cancel_order",
            body={"symbol": symbol, "orderId": order_id},
            signed=True,
        )

    async def get_positions(self) -> list[dict[str, Any]]:
        data = await self._request("GET", "/api/v1/futures/position/list", signed=True)
        return data.get("data", []) if isinstance(data.get("data"), list) else []

    async def get_balances(self) -> list[Balance]:
        data = await self._request("GET", "/api/v1/futures/account/balance", signed=True)
        items = data.get("data", [])
        if isinstance(items, dict):
            items = [items]
        return [
            Balance(
                asset=b.get("coin", "USDT"),
                available=Decimal(str(b.get("available", 0))),
                frozen=Decimal(str(b.get("frozen", 0))),
                total=Decimal(str(b.get("balance", b.get("total", 0)))),
            )
            for b in items
        ]


class BitunixApiError(Exception):
    def __init__(self, message: str, raw: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.raw = raw or {}

    @property
    def is_margin_error(self) -> bool:
        msg = str(self).lower()
        return "margin" in msg or "insufficient" in msg or "notional" in msg
