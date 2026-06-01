import pytest

from trading_platform.adapters.persistence.broadcast_emitter import BroadcastingEventEmitter
from trading_platform.adapters.persistence.kafka_emitter import InMemoryEventEmitter
from trading_platform.engine.realtime_hub import hub


@pytest.mark.asyncio
async def test_broadcast_emitter_reaches_hub():
    inner = InMemoryEventEmitter()
    emitter = BroadcastingEventEmitter(inner)
    received = []

    class Capture:
        async def send_text(self, data: str):
            received.append(data)

    ws = Capture()
    await hub.register_client(ws)  # type: ignore[arg-type]
    await emitter.emit("trading.events", "fill", {"symbol": "BTCUSDT"})
    assert received
    await hub.disconnect(ws)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_hub_broadcast_load():
    """Phase F: basic WS fan-out load (100 clients)."""
    messages = []

    class FakeWS:
        def __init__(self, i: int):
            self.i = i

        async def send_text(self, data: str):
            messages.append((self.i, data))

    clients = [FakeWS(i) for i in range(100)]
    for c in clients:
        await hub.register_client(c)  # type: ignore[arg-type]
    await hub.broadcast("test", {"n": 1})
    assert len(messages) == 100
    for c in clients:
        await hub.disconnect(c)  # type: ignore[arg-type]
