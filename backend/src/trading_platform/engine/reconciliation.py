"""Reconcile exchange positions with internal ledger (live mode)."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from trading_platform.core.ledger import SimulatedLedger
from trading_platform.core.models import PositionLeg
from trading_platform.core.ports import ExecutionPort


def reconcile(
    exchange_positions: list[PositionLeg],
    ledger: SimulatedLedger,
) -> dict[str, Any]:
    ledger_map = {(p.symbol, p.side.value): p for p in ledger.get_positions()}
    exchange_map = {(p.symbol, p.side.value): p for p in exchange_positions}
    mismatches: list[dict[str, Any]] = []

    for key, leg in ledger_map.items():
        other = exchange_map.get(key)
        if not other:
            mismatches.append({"type": "missing_on_exchange", "symbol": leg.symbol, "side": leg.side.value})
        elif abs(leg.quantity - other.quantity) > Decimal("0.0001"):
            mismatches.append(
                {
                    "type": "qty_mismatch",
                    "symbol": leg.symbol,
                    "ledger_qty": str(leg.quantity),
                    "exchange_qty": str(other.quantity),
                }
            )

    for key in exchange_map:
        if key not in ledger_map:
            mismatches.append({"type": "missing_on_ledger", "symbol": key[0], "side": key[1]})

    return {"ok": len(mismatches) == 0, "mismatches": mismatches}


async def reconcile_live(execution: ExecutionPort, ledger: SimulatedLedger) -> dict[str, Any]:
    positions = await execution.get_positions()
    return reconcile(positions, ledger)
