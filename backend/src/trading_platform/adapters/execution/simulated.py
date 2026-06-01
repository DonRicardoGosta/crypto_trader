"""Shared simulated execution for dry-run and backtest."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from trading_platform.adapters.persistence.kafka_emitter import TOPIC_EVENTS
from trading_platform.core.enums import OrderSide, OrderStatus
from trading_platform.core.ledger import SimulatedLedger, SlippageModel
from trading_platform.core.models import (
    Balance,
    OrderIntent,
    OrderResult,
    PositionLeg,
)
from trading_platform.core.ports import ClockPort, EventEmitter, MarketDataPort


class SimulatedExecutionBase:
    def __init__(
        self,
        market: MarketDataPort,
        clock: ClockPort,
        ledger: SimulatedLedger,
        emitter: EventEmitter,
        strategy_id: str | None = None,
        slippage: SlippageModel | None = None,
    ) -> None:
        self._market = market
        self._clock = clock
        self._ledger = ledger
        self._emitter = emitter
        self._strategy_id = strategy_id
        self._slippage = slippage or SlippageModel()
        self._orders: dict[str, OrderResult] = {}

    @property
    def ledger(self) -> SimulatedLedger:
        return self._ledger

    async def place_order(self, intent: OrderIntent) -> OrderResult:
        ticker = await self._market.get_ticker(intent.symbol)
        price = intent.price or ticker.last_price
        if intent.side == OrderSide.BUY:
            fill_price = self._slippage.apply(price, OrderSide.BUY)
        else:
            fill_price = self._slippage.apply(price, OrderSide.SELL)

        ladder_step = int(intent.metadata.get("ladder_step", 0))
        fill = self._ledger.apply_fill(intent, fill_price, ladder_step=ladder_step)
        exchange_id = f"sim-{uuid4().hex[:12]}"
        result = OrderResult(
            client_order_id=intent.client_order_id,
            exchange_order_id=exchange_id,
            status=OrderStatus.FILLED,
            symbol=intent.symbol,
            side=intent.side,
            filled_qty=fill.quantity,
            avg_price=fill.price,
            raw={"simulated": True},
        )
        self._orders[intent.client_order_id] = result
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
                "filled_qty": float(fill.quantity),
                "avg_price": float(fill.price),
            },
        )
        await self._emitter.emit(
            TOPIC_EVENTS,
            "fill",
            {
                "strategy_id": self._strategy_id,
                "fill_id": fill.fill_id,
                "order_id": intent.client_order_id,
                "symbol": fill.symbol,
                "side": fill.side.value,
                "quantity": float(fill.quantity),
                "price": float(fill.price),
                "fee": float(fill.fee),
            },
        )
        return result

    async def cancel_order(self, symbol: str, exchange_order_id: str) -> bool:
        return True

    async def get_positions(self) -> list[PositionLeg]:
        return self._ledger.get_positions()

    async def get_balances(self) -> list[Balance]:
        return [
            Balance(
                asset="USDT",
                available=self._ledger.balance_usd,
                frozen=Decimal("0"),
                total=self._ledger.balance_usd,
            )
        ]

    async def get_open_orders(self, symbol: str | None = None) -> list[OrderResult]:
        return list(self._orders.values())
