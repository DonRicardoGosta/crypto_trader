"""Adaptive Ladder strategy — multi-leg, coin discovery, leverage bump."""

from __future__ import annotations

import logging
from decimal import Decimal
from uuid import uuid4

from trading_platform.adapters.persistence.kafka_emitter import TOPIC_AUDIT, TOPIC_EVENTS
from trading_platform.core.enums import EventType, OrderSide, OrderType, PositionSide
from trading_platform.core.models import OrderIntent, Ticker
from trading_platform.strategies.adaptive_ladder.discovery import discover_symbols
from trading_platform.strategies.adaptive_ladder.indicators import rsi
from trading_platform.strategies.base import Strategy

logger = logging.getLogger(__name__)


class AdaptiveLadderStrategy(Strategy):
  async def on_tick(self, tickers: dict[str, Ticker]) -> None:
    if not self._active_symbols:
      await self._refresh_symbols()
    for symbol in self._active_symbols:
      await self._process_symbol(symbol, tickers.get(symbol))

  async def on_klines(self, symbol: str, klines: list) -> None:
    if symbol in self._active_symbols:
      ticker = await self.market.get_ticker(symbol)
      await self._process_symbol(symbol, ticker, klines)

  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self._active_symbols: list[str] = list(self.param("symbols", []))
    self._ladder_steps: dict[str, int] = {}
    self._pending_bump: dict[str, tuple[OrderSide, PositionSide | None]] = {}

  async def _refresh_symbols(self) -> None:
    max_sym = int(self.param("max_active_symbols", 5))
    excluded = self.param("excluded_symbols", [])
    min_vol = Decimal(str(self.param("min_volume_24h", "1000000")))
    rest = getattr(self.market, "_client", None)
    if rest:
      self._active_symbols = await discover_symbols(rest, max_sym, min_vol, excluded)
    elif not self._active_symbols:
      self._active_symbols = ["BTCUSDT", "ETHUSDT"]

  async def _process_symbol(
    self,
    symbol: str,
    ticker: Ticker | None,
    klines: list | None = None,
  ) -> None:
    if not ticker or ticker.last_price <= 0:
      return

    klines = klines or await self.market.get_klines(symbol, "15min", 50)
    if len(klines) < 20:
      return

    await self._update_trailing_stops(symbol, ticker.last_price)

    rsi_val = rsi(klines)
    step = self._ladder_steps.get(symbol, 0)
    max_steps = int(self.param("max_ladder_steps", 5))
    ladder_pct = Decimal(str(self.param("ladder_step_pct", "0.5"))) / Decimal("100")

    if symbol in self._pending_bump:
      await self._retry_with_bump(symbol, ticker.last_price)
      return

    if step >= max_steps:
      return

    last_close = klines[-1].close
    threshold = last_close * ladder_pct * Decimal(step + 1)

    if rsi_val < Decimal("35"):
      await self._open_leg(symbol, OrderSide.BUY, PositionSide.LONG, ticker.last_price, step)
    elif rsi_val > Decimal("65"):
      await self._open_leg(symbol, OrderSide.SELL, PositionSide.SHORT, ticker.last_price, step)
    elif step > 0 and abs(ticker.last_price - last_close) > threshold:
      await self._open_leg(
        symbol,
        OrderSide.BUY if ticker.last_price < last_close else OrderSide.SELL,
        PositionSide.LONG if ticker.last_price < last_close else PositionSide.SHORT,
        ticker.last_price,
        step,
      )

  async def _open_leg(
    self,
    symbol: str,
    side: OrderSide,
    pos_side: PositionSide,
    price: Decimal,
    step: int,
  ) -> None:
    intent = OrderIntent(
      symbol=symbol,
      side=side,
      order_type=OrderType.MARKET,
      quantity=Decimal("0"),
      position_side=pos_side,
      metadata={"ladder_step": step},
    )
    decision = self.risk.propose_order(intent, price)
    if not decision.approved or not decision.adjusted_intent:
      return

    result = await self.execution.place_order(decision.adjusted_intent)
    if result.message and "margin" in result.message.lower():
      self._pending_bump[symbol] = (side, pos_side)
      return

    if hasattr(result, "status") and str(result.status) == "rejected":
      raw_msg = result.message or ""
      if "margin" in raw_msg.lower() or "insufficient" in raw_msg.lower():
        self._pending_bump[symbol] = (side, pos_side)
      return

    self._ladder_steps[symbol] = step + 1
    emitter = getattr(self.execution, "_emitter", None)
    if emitter:
      await emitter.emit(
        TOPIC_EVENTS,
        EventType.POSITION.value,
        {"symbol": symbol, "step": step, "side": side.value},
      )

  async def _retry_with_bump(self, symbol: str, price: Decimal) -> None:
    pending = self._pending_bump.pop(symbol, None)
    if not pending:
      return
    side, pos_side = pending
    if not self.risk.bump_leverage():
      emitter = getattr(self.execution, "_emitter", None)
      if emitter:
        await emitter.emit(
          TOPIC_AUDIT,
          EventType.LEVERAGE_BUMP_EXHAUSTED.value,
          {
            "strategy_id": str(self.config.id),
            "symbol": symbol,
            "leverage": self.risk.risk_config.leverage_multiplier,
          },
        )
      return
    emitter = getattr(self.execution, "_emitter", None)
    if emitter:
      await emitter.emit(
        TOPIC_AUDIT,
        EventType.LEVERAGE_BUMP.value,
        {
          "strategy_id": str(self.config.id),
          "symbol": symbol,
          "new_leverage": self.risk.risk_config.leverage_multiplier,
        },
      )
    step = self._ladder_steps.get(symbol, 0)
    await self._open_leg(symbol, side, pos_side, price, step)

  async def _update_trailing_stops(self, symbol: str, mark: Decimal) -> None:
    max_dd_pct = Decimal(str(self.param("max_drawdown_pct", "5"))) / Decimal("100")
    ledger = getattr(self.execution, "ledger", None) or getattr(
      self.execution, "_ledger", None
    )
    if not ledger:
      return
    ledger.update_unrealized(symbol, mark)
    for leg in list(ledger.get_positions()):
      if leg.symbol != symbol:
        continue
      dd = abs(leg.unrealized_pnl) / (leg.quantity * leg.entry_price + Decimal("0.0001"))
      if leg.unrealized_pnl < 0 and dd >= max_dd_pct:
        close_side = OrderSide.SELL if leg.side == PositionSide.LONG else OrderSide.BUY
        intent = OrderIntent(
          symbol=symbol,
          side=close_side,
          order_type=OrderType.MARKET,
          quantity=leg.quantity,
          position_side=leg.side,
          reduce_only=True,
          client_order_id=str(uuid4()),
        )
        await self.execution.place_order(intent)
