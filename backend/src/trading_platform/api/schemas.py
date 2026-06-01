from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CredentialCreate(BaseModel):
    exchange: str = "bitunix"
    label: str
    api_key: str
    api_secret: str


class CredentialOut(BaseModel):
    id: uuid.UUID
    exchange: str
    label: str
    is_active: bool


class StrategyRiskIn(BaseModel):
    max_capital_usd: float
    min_investment_usd: float
    leverage_multiplier: int = 1
    max_leverage_multiplier: int = 20


class StrategyCreate(BaseModel):
    name: str
    strategy_type: str = "adaptive_ladder"
    mode: str = "dry_run"
    enabled: bool = False
    parameters: dict[str, Any] = Field(default_factory=dict)
    risk: StrategyRiskIn


class StrategyUpdate(BaseModel):
    name: str | None = None
    mode: str | None = None
    enabled: bool | None = None
    parameters: dict[str, Any] | None = None
    risk: StrategyRiskIn | None = None


class StrategyOut(BaseModel):
    id: uuid.UUID
    name: str
    strategy_type: str
    mode: str
    enabled: bool
    parameters: dict[str, Any]


class BacktestRequest(BaseModel):
    strategy_id: uuid.UUID
    start_ts: datetime
    end_ts: datetime
    symbols: list[str] | None = None
    slippage_bps: int = 0


class AppConfigSet(BaseModel):
    key: str
    value: dict[str, Any]
