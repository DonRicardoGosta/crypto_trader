"""Emit to Kafka and broadcast to realtime WebSocket hub."""

from __future__ import annotations

from typing import Any

from trading_platform.adapters.persistence.kafka_emitter import KafkaEventEmitter
from trading_platform.core.ports import EventEmitter
from trading_platform.engine.realtime_hub import hub


class BroadcastingEventEmitter(EventEmitter):
    def __init__(self, inner: KafkaEventEmitter | None = None) -> None:
        self._inner = inner or KafkaEventEmitter()

    async def start(self) -> None:
        await self._inner.start()

    async def stop(self) -> None:
        await self._inner.stop()

    async def emit(self, topic: str, event_type: str, payload: dict[str, Any]) -> None:
        await self._inner.emit(topic, event_type, payload)
        await hub.broadcast(event_type, {"topic": topic, **payload})

    async def emit_error(
        self,
        source: str,
        message: str,
        severity: str = "error",
        details: dict[str, Any] | None = None,
    ) -> None:
        await self._inner.emit_error(source, message, severity, details)
        await hub.broadcast("error", {"source": source, "message": message, "severity": severity})
