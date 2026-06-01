"""Engine control endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from trading_platform.adapters.persistence.models import StrategyRow
from trading_platform.api.deps import get_session
from trading_platform.engine import state as engine_state
from trading_platform.engine.realtime_hub import hub

router = APIRouter()


@router.get("/status")
async def engine_status():
    return {"emergency_stop": engine_state.is_emergency_stop()}


@router.post("/emergency-stop")
async def emergency_stop():
    await engine_state.set_emergency_stop(True)
    await hub.broadcast("emergency_stop", {"active": True})
    return {"emergency_stop": True}


@router.post("/emergency-stop/reset")
async def reset_emergency_stop():
    await engine_state.set_emergency_stop(False)
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


@router.post("/reconcile/{strategy_id}")
async def reconcile_strategy(strategy_id: str):
    """Reconcile live exchange positions vs ledger (dry-run uses ledger only)."""
    from trading_platform.adapters.bitunix.rest import BitunixRestClient
    from trading_platform.adapters.execution.live import BitunixLiveExecution
    from trading_platform.adapters.persistence.kafka_emitter import InMemoryEventEmitter
    from trading_platform.core.ledger import SimulatedLedger
    from trading_platform.engine.reconciliation import reconcile_live

    emitter = InMemoryEventEmitter()
    client = BitunixRestClient(emitter=emitter)
    ledger = SimulatedLedger()
    execution = BitunixLiveExecution(client, emitter, strategy_id)
    result = await reconcile_live(execution, ledger)
    await client.close()
    return result


@router.get("/strategies/enabled")
async def list_enabled(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(StrategyRow).where(StrategyRow.enabled.is_(True)))
    return [
        {"id": str(r.id), "name": r.name, "mode": r.mode, "strategy_type": r.strategy_type}
        for r in result.scalars().all()
    ]
