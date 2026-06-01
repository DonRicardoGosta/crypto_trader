import pytest

from trading_platform.engine import state as engine_state


@pytest.mark.asyncio
async def test_emergency_stop_toggle():
    await engine_state.set_emergency_stop(True)
    assert engine_state.is_emergency_stop() is True
    await engine_state.set_emergency_stop(False)
    assert engine_state.is_emergency_stop() is False
