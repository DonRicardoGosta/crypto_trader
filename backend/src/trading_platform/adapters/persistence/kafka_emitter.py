"""Kafka event emitter with bounded fallback queue."""

from __future__ import annotations

import json
import logging
from collections import deque
from datetime import UTC, datetime
from typing import Any

from aiokafka import AIOKafkaProducer

from trading_platform.config import settings
from trading_platform.core.ports import EventEmitter

logger = logging.getLogger(__name__)

TOPIC_EVENTS = "trading.events"
TOPIC_ERRORS = "trading.errors"
TOPIC_METRICS = "trading.metrics"
TOPIC_AUDIT = "trading.audit"


class KafkaEventEmitter(EventEmitter):
    def __init__(self, bootstrap: str | None = None) -> None:
        self._bootstrap = bootstrap or settings.kafka_bootstrap
        self._producer: AIOKafkaProducer | None = None
        self._queue: deque[tuple[str, dict[str, Any]]] = deque(
            maxlen=settings.event_queue_max_size
        )
        self._connected = False

    async def start(self) -> None:
        try:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self._bootstrap,
                acks=1,
                value_serializer=lambda v: json.dumps(v, default=str).encode(),
            )
            await self._producer.start()
            self._connected = True
            await self._flush_queue()
            logger.info("Kafka producer connected to %s", self._bootstrap)
        except Exception as e:
            logger.warning("Kafka unavailable, using fallback queue: %s", e)
            self._connected = False

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()

    async def _flush_queue(self) -> None:
        if not self._producer or not self._connected:
            return
        while self._queue:
            topic, payload = self._queue.popleft()
            await self._send(topic, payload)

    async def _send(self, topic: str, payload: dict[str, Any]) -> None:
        if self._producer and self._connected:
            try:
                await self._producer.send_and_wait(topic, payload)
                return
            except Exception as e:
                logger.warning("Kafka send failed: %s", e)
                self._connected = False
        if len(self._queue) >= settings.event_queue_max_size:
            self._queue.popleft()
        self._queue.append((topic, payload))

    async def emit(self, topic: str, event_type: str, payload: dict[str, Any]) -> None:
        envelope = {
            "event_type": event_type,
            "ts": datetime.now(UTC).isoformat(),
            "payload": payload,
        }
        await self._send(topic, envelope)

    async def emit_error(
        self,
        source: str,
        message: str,
        severity: str = "error",
        details: dict[str, Any] | None = None,
    ) -> None:
        await self.emit(
            TOPIC_ERRORS,
            "error",
            {
                "source": source,
                "severity": severity,
                "message": message,
                "details": details or {},
            },
        )


class InMemoryEventEmitter(EventEmitter):
    """For tests without Kafka."""

    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict[str, Any]]] = []

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    async def emit(self, topic: str, event_type: str, payload: dict[str, Any]) -> None:
        self.events.append((topic, event_type, payload))

    async def emit_error(
        self,
        source: str,
        message: str,
        severity: str = "error",
        details: dict[str, Any] | None = None,
    ) -> None:
        await self.emit(TOPIC_ERRORS, "error", {"source": source, "message": message})
