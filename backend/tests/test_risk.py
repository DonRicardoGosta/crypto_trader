from decimal import Decimal

from trading_platform.core.enums import OrderSide, OrderType
from trading_platform.core.ledger import SimulatedLedger
from trading_platform.core.models import OrderIntent, StrategyRiskConfig
from trading_platform.risk.engine import RiskEngine


def test_risk_approves_within_capital():
    risk_cfg = StrategyRiskConfig(
        max_capital_usd=Decimal("100"),
        min_investment_usd=Decimal("1"),
        leverage_multiplier=5,
        max_leverage_multiplier=10,
    )
    ledger = SimulatedLedger(initial_balance_usd=Decimal("100"))
    engine = RiskEngine(risk_cfg, ledger)
    intent = OrderIntent(symbol="BTCUSDT", side=OrderSide.BUY, order_type=OrderType.MARKET, quantity=Decimal("0"))
    decision = engine.propose_order(intent, Decimal("50000"))
    assert decision.approved

def test_leverage_bump():
    risk_cfg = StrategyRiskConfig(
        max_capital_usd=Decimal("1000"),
        min_investment_usd=Decimal("1"),
        leverage_multiplier=1,
        max_leverage_multiplier=5,
    )
    engine = RiskEngine(risk_cfg)
    assert engine.bump_leverage()
    assert engine.risk_config.leverage_multiplier == 2
