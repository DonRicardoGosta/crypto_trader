from decimal import Decimal

from trading_platform.core.enums import OrderSide, OrderType, PositionSide
from trading_platform.core.ledger import SimulatedLedger
from trading_platform.core.models import OrderIntent


def test_ledger_open_and_close():
    ledger = SimulatedLedger(initial_balance_usd=Decimal("1000"))
    intent = OrderIntent(
        symbol="ETHUSDT", side=OrderSide.BUY, order_type=OrderType.MARKET,
        quantity=Decimal("0.1"), position_side=PositionSide.LONG, metadata={"leverage": 1},
    )
    ledger.apply_fill(intent, Decimal("3000"))
    assert len(ledger.get_positions()) == 1
    close = OrderIntent(
        symbol="ETHUSDT", side=OrderSide.SELL, order_type=OrderType.MARKET,
        quantity=Decimal("0.1"), position_side=PositionSide.LONG, reduce_only=True,
    )
    ledger.apply_fill(close, Decimal("3100"))
    assert len(ledger.get_positions()) == 0
