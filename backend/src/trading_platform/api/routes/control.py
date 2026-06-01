"""Engine control endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from trading_platform.adapters.persistence.models import StrategyRow
from trading_platform.api.deps import get_session
from trading_platform.engine.realtime_hub import hub

router = APIRouter()

_engine_stop_flag: bool = False


@router.get("/status")
async def engine_status():
    return {"emergency_stop": _engine_stop_flag}


@router.post("/emergency-stop")
async def emergency_stop():
    global _engine_stop_flag
    _engine_stop_flag = True
    await hub.broadcast("emergency_stop", {"active": True})
    return {"emergency_stop": True}


@router.post("/emergency-stop/reset")
async def reset_emergency_stop():
    global _engine_stop_flag
    _engine_stop_flag = False
    await hub.broadcast("emergency_stop", {"active": False})
    return {"emergency_stop": False}


@router.post("/strategies/{strategy_id}/mode/{mode}")
async def set_strategy_mode(
    strategy_id: str,
    mode: str,
    session: AsyncSession = Depends(get_session),
):
    import uuid

    row = await session.get(StrategyRow, uuid.UUID(strategy_id))
    if not row:
        return {"error": "not found"}
    row.mode = mode
    await session.commit()
    await hub.broadcast("mode_switch", {"strategy_id": strategy_id, "mode": mode})
    return {"strategy_id": strategy_id, "mode": mode}


@router.get("/strategies/enabled")
async def list_enabled(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(StrategyRow).where(StrategyRow.enabled.is_(True)))
    return [
        {"id": str(r.id), "name": r.name, "mode": r.mode, "strategy_type": r.strategy_type}
        for r in result.scalars().all()
    ]
