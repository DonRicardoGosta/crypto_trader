"""Strategy registry."""

from __future__ import annotations

from trading_platform.strategies.adaptive_ladder.strategy import AdaptiveLadderStrategy
from trading_platform.strategies.base import Strategy

_REGISTRY: dict[str, type[Strategy]] = {
    "adaptive_ladder": AdaptiveLadderStrategy,
}


def get_strategy_class(strategy_type: str) -> type[Strategy]:
    if strategy_type not in _REGISTRY:
        raise ValueError(f"Unknown strategy type: {strategy_type}")
    return _REGISTRY[strategy_type]


def register_strategy(name: str, cls: type[Strategy]) -> None:
    _REGISTRY[name] = cls
