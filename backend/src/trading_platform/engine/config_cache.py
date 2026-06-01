"""In-memory config cache — no sync DB in hot path."""

from __future__ import annotations

import asyncio
import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from trading_platform.adapters.persistence.models import StrategyRiskRow, StrategyRow
from trading_platform.config import settings
from trading_platform.core.enums import ExecutionMode
from trading_platform.core.models import StrategyConfig, StrategyRiskConfig


class ConfigCache:
    def __init__(self) -> None:
        self._engine = create_async_engine(settings.database_url)
        self._factory = async_sessionmaker(self._engine, expire_on_commit=False)
        self._strategies: dict[uuid.UUID, StrategyConfig] = {}
        self._running = False

    async def start(self) -> None:
        self._running = True
        asyncio.create_task(self._poll_loop())

    async def stop(self) -> None:
        self._running = False
        await self._engine.dispose()

    async def _poll_loop(self) -> None:
        while self._running:
            try:
                await self.refresh()
            except Exception:
                pass
            await asyncio.sleep(settings.config_cache_ttl_seconds)

    async def refresh(self) -> None:
        async with self._factory() as session:
            result = await session.execute(
                select(StrategyRow).where(StrategyRow.enabled.is_(True))
            )
            rows = result.scalars().all()
            for row in rows:
                risk = await session.get(StrategyRiskRow, row.id)
                if not risk:
                    continue
                self._strategies[row.id] = StrategyConfig(
                    id=row.id,
                    name=row.name,
                    strategy_type=row.strategy_type,
                    mode=ExecutionMode(row.mode),
                    enabled=row.enabled,
                    parameters=dict(row.parameters or {}),
                    risk=StrategyRiskConfig(
                        max_capital_usd=Decimal(str(risk.max_capital_usd)),
                        min_investment_usd=Decimal(str(risk.min_investment_usd)),
                        leverage_multiplier=risk.leverage_multiplier,
                        max_leverage_multiplier=risk.max_leverage_multiplier,
                    ),
                )

    def get_enabled(self) -> list[StrategyConfig]:
        return list(self._strategies.values())

    def get(self, strategy_id: uuid.UUID) -> StrategyConfig | None:
        return self._strategies.get(strategy_id)
