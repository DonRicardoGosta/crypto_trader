"""Live execution via Bitunix REST."""

from __future__ import annotations

from decimal import Decimal

from trading_platform.adapters.bitunix.rest import BitunixApiError, BitunixRestClient
from trading_platform.adapters.persistence.kafka_emitter import TOPIC_EVENTS
from trading_platform.core.enums import OrderStatus, PositionSide
from trading_platform.core.ledger import SimulatedLedger
from trading_platform.core.models import Balance, OrderIntent, OrderResult, PositionLeg
from trading_platform.core.ports import EventEmitter, ExecutionPort


class BitunixLiveExecution(ExecutionPort):
    def __init__(
        self,
        client: BitunixRestClient,
        emitter: EventEmitter,
        strategy_id: str | None = None,
        ledger: SimulatedLedger | None = None,
    ) -> None:
        self._client = client
        self._emitter = emitter
        self._strategy_id = strategy_id
        self._ledger = ledger  # reconciliation only

    async def place_order(self, intent: OrderIntent) -> OrderResult:
        leverage = int(intent.metadata.get("leverage", 1))
        try:
            raw = await self._client.place_order(
                symbol=intent.symbol,
                side=intent.side.value,
                qty=str(intent.quantity),
                order_type=intent.order_type.value,
                price=str(intent.price) if intent.price else None,
                leverage=leverage,
            )
            data = raw.get("data", raw)
            exchange_id = str(data.get("orderId", data.get("id", "")))
            result = OrderResult(
                client_order_id=intent.client_order_id,
                exchange_order_id=exchange_id,
                status=OrderStatus.OPEN,
                symbol=intent.symbol,
                side=intent.side,
                filled_qty=Decimal(str(data.get("filledQty", 0))),
                avg_price=Decimal(str(data["avgPrice"])) if data.get("avgPrice") else None,
                raw=raw,
            )
            await self._emitter.emit(
                TOPIC_EVENTS,
                "order",
                {
                    "strategy_id": self._strategy_id,
                    "client_order_id": intent.client_order_id,
                    "exchange_order_id": exchange_id,
                    "symbol": intent.symbol,
                    "side": intent.side.value,
                    "status": result.status.value,
                    "quantity": float(intent.quantity),
                    "raw": raw,
                },
            )
            return result
        except BitunixApiError as e:
            await self._emitter.emit_error(
                "bitunix.live",
                str(e),
                details={"client_order_id": intent.client_order_id, "raw": e.raw},
            )
            return OrderResult(
                client_order_id=intent.client_order_id,
                exchange_order_id=None,
                status=OrderStatus.REJECTED,
                symbol=intent.symbol,
                side=intent.side,
                filled_qty=Decimal("0"),
                avg_price=None,
                message=str(e),
                raw=e.raw,
            )

    async def cancel_order(self, symbol: str, exchange_order_id: str) -> bool:
        try:
            await self._client.cancel_order(symbol, exchange_order_id)
            return True
        except Exception:
            return False

    async def get_positions(self) -> list[PositionLeg]:
        raw_positions = await self._client.get_positions()
        legs: list[PositionLeg] = []
        for p in raw_positions:
            side = PositionSide.LONG if p.get("side", "").lower() in ("buy", "long") else PositionSide.SHORT
            legs.append(
                PositionLeg(
                    leg_id=str(p.get("positionId", p.get("id", ""))),
                    symbol=p.get("symbol", ""),
                    side=side,
                    quantity=Decimal(str(p.get("qty", p.get("quantity", 0)))),
                    entry_price=Decimal(str(p.get("avgPrice", p.get("entryPrice", 0)))),
                )
            )
        return legs

    async def get_balances(self) -> list[Balance]:
        return await self._client.get_balances()

    async def get_open_orders(self, symbol: str | None = None) -> list[OrderResult]:
        return []
