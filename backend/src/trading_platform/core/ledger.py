"""Simulated ledger for dry-run and backtest."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import uuid4

from trading_platform.core.enums import OrderSide, PositionSide
from trading_platform.core.models import Fill, OrderIntent, PositionLeg


@dataclass
class FeeModel:
    maker_bps: Decimal = Decimal("2")
    taker_bps: Decimal = Decimal("5")

    def compute_fee(self, notional: Decimal, is_maker: bool = False) -> Decimal:
        bps = self.maker_bps if is_maker else self.taker_bps
        return notional * bps / Decimal("10000")


@dataclass
class SlippageModel:
    bps: Decimal = Decimal("0")

    def apply(self, price: Decimal, side: OrderSide) -> Decimal:
        slip = price * self.bps / Decimal("10000")
        if side == OrderSide.BUY:
            return price + slip
        return price - slip


@dataclass
class SimulatedLedger:
    """Tracks positions and PnL for simulated execution."""

    initial_balance_usd: Decimal = Decimal("10000")
    fee_model: FeeModel = field(default_factory=FeeModel)
    legs: dict[str, PositionLeg] = field(default_factory=dict)
    realized_pnl: Decimal = Decimal("0")
    total_fees: Decimal = Decimal("0")
    balance_usd: Decimal = field(init=False)

    def __post_init__(self) -> None:
        self.balance_usd = self.initial_balance_usd

    def open_risk_usd(self) -> Decimal:
        return sum(
            (leg.quantity * leg.entry_price for leg in self.legs.values()),
            start=Decimal("0"),
        )

    def apply_fill(
        self,
        intent: OrderIntent,
        fill_price: Decimal,
        fill_qty: Decimal | None = None,
        ladder_step: int = 0,
    ) -> Fill:
        qty = fill_qty or intent.quantity
        price = fill_price
        notional = qty * price
        fee = self.fee_model.compute_fee(notional)
        self.total_fees += fee
        self.balance_usd -= fee

        pos_side = intent.position_side or (
            PositionSide.LONG if intent.side == OrderSide.BUY else PositionSide.SHORT
        )
        leg_id = f"{intent.symbol}:{pos_side.value}:{ladder_step}:{uuid4().hex[:8]}"

        if intent.reduce_only:
            self._reduce_position(intent.symbol, pos_side, qty, price)
        else:
            leg = PositionLeg(
                leg_id=leg_id,
                symbol=intent.symbol,
                side=pos_side,
                quantity=qty,
                entry_price=price,
                ladder_step=ladder_step,
            )
            self.legs[leg_id] = leg
            self.balance_usd -= notional / Decimal(intent.metadata.get("leverage", 1))

        return Fill(
            fill_id=str(uuid4()),
            order_id=intent.client_order_id,
            symbol=intent.symbol,
            side=intent.side,
            quantity=qty,
            price=price,
            fee=fee,
            ts=intent.metadata.get("ts") or __import__("datetime").datetime.now(__import__("datetime").UTC),
        )

    def _reduce_position(
        self,
        symbol: str,
        side: PositionSide,
        qty: Decimal,
        price: Decimal,
    ) -> None:
        remaining = qty
        to_remove: list[str] = []
        for lid, leg in self.legs.items():
            if leg.symbol != symbol or leg.side != side:
                continue
            if remaining <= 0:
                break
            close_qty = min(remaining, leg.quantity)
            if side == PositionSide.LONG:
                pnl = (price - leg.entry_price) * close_qty
            else:
                pnl = (leg.entry_price - price) * close_qty
            self.realized_pnl += pnl
            self.balance_usd += pnl
            leg.quantity -= close_qty
            remaining -= close_qty
            if leg.quantity <= 0:
                to_remove.append(lid)
        for lid in to_remove:
            del self.legs[lid]

    def update_unrealized(self, symbol: str, mark_price: Decimal) -> None:
        for leg in self.legs.values():
            if leg.symbol != symbol:
                continue
            if leg.side == PositionSide.LONG:
                leg.unrealized_pnl = (mark_price - leg.entry_price) * leg.quantity
            else:
                leg.unrealized_pnl = (leg.entry_price - mark_price) * leg.quantity

    def get_positions(self) -> list[PositionLeg]:
        return list(self.legs.values())
