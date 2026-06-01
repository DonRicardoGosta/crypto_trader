from decimal import Decimal

from trading_platform.core.enums import PositionSide
from trading_platform.core.ledger import SimulatedLedger
from trading_platform.core.models import OrderIntent, PositionLeg
from trading_platform.core.enums import OrderSide, OrderType
from trading_platform.engine.reconciliation import reconcile


def test_reconcile_ok():
    ledger = SimulatedLedger()
    leg = PositionLeg("1", "BTCUSDT", PositionSide.LONG, Decimal("1"), Decimal("100"))
    ledger.legs["1"] = leg
    result = reconcile([leg], ledger)
    assert result["ok"] is True


def test_reconcile_mismatch():
    ledger = SimulatedLedger()
    ledger.legs["1"] = PositionLeg("1", "BTCUSDT", PositionSide.LONG, Decimal("1"), Decimal("100"))
    exchange = [PositionLeg("2", "BTCUSDT", PositionSide.LONG, Decimal("2"), Decimal("100"))]
    result = reconcile(exchange, ledger)
    assert result["ok"] is False
