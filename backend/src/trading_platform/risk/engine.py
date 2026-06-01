"""Risk engine — validates orders before execution."""

from __future__ import annotations

from decimal import Decimal

from trading_platform.core.ledger import SimulatedLedger
from trading_platform.core.models import OrderIntent, RiskDecision, StrategyRiskConfig


class RiskEngine:
    def __init__(self, risk: StrategyRiskConfig, ledger: SimulatedLedger | None = None) -> None:
        self._risk = risk
        self._ledger = ledger

    @property
    def risk_config(self) -> StrategyRiskConfig:
        return self._risk

    def update_leverage(self, new_leverage: int) -> None:
        self._risk = StrategyRiskConfig(
            max_capital_usd=self._risk.max_capital_usd,
            min_investment_usd=self._risk.min_investment_usd,
            leverage_multiplier=new_leverage,
            max_leverage_multiplier=self._risk.max_leverage_multiplier,
        )

    def order_notional(self, intent: OrderIntent, price: Decimal) -> Decimal:
        """Exposure = min_investment * leverage (stake stays fixed)."""
        stake = self._risk.min_investment_usd
        exposure = stake * Decimal(self._risk.leverage_multiplier)
        if intent.quantity > 0 and price > 0:
            return intent.quantity * price
        return exposure

    def propose_order(self, intent: OrderIntent, mark_price: Decimal) -> RiskDecision:
        notional = self.order_notional(intent, mark_price)
        open_risk = self._ledger.open_risk_usd() if self._ledger else Decimal("0")

        if open_risk + notional > self._risk.max_capital_usd:
            return RiskDecision(
                approved=False,
                reason=f"Exceeds max_capital_usd ({self._risk.max_capital_usd})",
            )

        stake_qty = self._compute_quantity(intent.symbol, mark_price)
        adjusted = OrderIntent(
            symbol=intent.symbol,
            side=intent.side,
            order_type=intent.order_type,
            quantity=stake_qty,
            price=intent.price,
            position_side=intent.position_side,
            client_order_id=intent.client_order_id,
            reduce_only=intent.reduce_only,
            metadata={
                **intent.metadata,
                "leverage": self._risk.leverage_multiplier,
                "stake_usd": str(self._risk.min_investment_usd),
            },
        )
        return RiskDecision(approved=True, adjusted_intent=adjusted)

    def _compute_quantity(self, symbol: str, price: Decimal) -> Decimal:
        if price <= 0:
            return Decimal("0")
        stake = self._risk.min_investment_usd
        exposure = stake * Decimal(self._risk.leverage_multiplier)
        return (exposure / price).quantize(Decimal("0.00000001"))

    def can_bump_leverage(self) -> bool:
        return self._risk.leverage_multiplier < self._risk.max_leverage_multiplier

    def bump_leverage(self) -> bool:
        if not self.can_bump_leverage():
            return False
        self.update_leverage(self._risk.leverage_multiplier + 1)
        return True
