"""Kafka consumer that writes events to PostgreSQL."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from trading_platform.adapters.persistence.kafka_emitter import (
    TOPIC_AUDIT,
    TOPIC_ERRORS,
    TOPIC_EVENTS,
    TOPIC_METRICS,
)
from trading_platform.adapters.persistence.models import (
    ErrorRow,
    EventRow,
    FillRow,
    OrderRow,
    PositionRow,
)
from trading_platform.config import settings

logger = logging.getLogger(__name__)

TOPICS = [TOPIC_EVENTS, TOPIC_ERRORS, TOPIC_METRICS, TOPIC_AUDIT]


class DbWriter:
    def __init__(self) -> None:
        self._engine = create_async_engine(settings.database_url)
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)
        self._consumer: AIOKafkaConsumer | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            *TOPICS,
            bootstrap_servers=settings.kafka_bootstrap,
            group_id="trading-db-writer",
            value_deserializer=lambda m: json.loads(m.decode()),
            auto_offset_reset="earliest",
        )
        await self._consumer.start()
        logger.info("DB writer started, consuming %s", TOPICS)

    async def stop(self) -> None:
        if self._consumer:
            await self._consumer.stop()
        await self._engine.dispose()

    async def run(self) -> None:
        if not self._consumer:
            await self.start()
        assert self._consumer is not None
        async for msg in self._consumer:
            try:
                await self._handle(msg.topic, msg.value)
            except Exception as e:
                logger.exception("Failed to persist message: %s", e)

    async def _handle(self, topic: str, envelope: dict[str, Any]) -> None:
        async with self._session_factory() as session:
            if topic == TOPIC_ERRORS:
                await self._write_error(session, envelope)
            else:
                await self._write_event(session, envelope, topic)
            await session.commit()

    async def _write_error(self, session: AsyncSession, envelope: dict[str, Any]) -> None:
        payload = envelope.get("payload", envelope)
        row = ErrorRow(
            source=payload.get("source", "unknown"),
            severity=payload.get("severity", "error"),
            message=payload.get("message", ""),
            details=payload.get("details"),
            ts=datetime.now(UTC),
        )
        session.add(row)

    async def _write_event(
        self, session: AsyncSession, envelope: dict[str, Any], topic: str
    ) -> None:
        event_type = envelope.get("event_type", "unknown")
        payload = envelope.get("payload", {})
        ts_str = envelope.get("ts")
        ts = datetime.fromisoformat(ts_str) if ts_str else datetime.now(UTC)

        row = EventRow(
            event_type=event_type,
            strategy_id=uuid.UUID(payload["strategy_id"])
            if payload.get("strategy_id")
            else None,
            payload={"topic": topic, **payload},
            ts=ts,
        )
        session.add(row)

        if event_type == "order" and payload.get("client_order_id"):
            await self._upsert_order(session, payload, ts)
        elif event_type == "fill":
            await self._insert_fill(session, payload, ts)
        elif event_type == "position":
            await self._upsert_position(session, payload, ts)

    async def _upsert_order(
        self, session: AsyncSession, payload: dict[str, Any], ts: datetime
    ) -> None:
        row = OrderRow(
            id=uuid.uuid4(),
            strategy_id=uuid.UUID(payload["strategy_id"])
            if payload.get("strategy_id")
            else None,
            client_order_id=payload["client_order_id"],
            exchange_order_id=payload.get("exchange_order_id"),
            symbol=payload["symbol"],
            side=payload["side"],
            order_type=payload.get("order_type", "market"),
            status=payload.get("status", "pending"),
            quantity=float(payload.get("quantity", 0)),
            filled_qty=float(payload.get("filled_qty", 0)),
            price=float(payload["price"]) if payload.get("price") else None,
            avg_price=float(payload["avg_price"]) if payload.get("avg_price") else None,
            raw_response=payload.get("raw"),
            created_at=ts,
        )
        session.add(row)

    async def _insert_fill(
        self, session: AsyncSession, payload: dict[str, Any], ts: datetime
    ) -> None:
        row = FillRow(
            id=uuid.uuid4(),
            order_id=uuid.UUID(payload["order_id"]) if payload.get("order_id") else uuid.uuid4(),
            fill_id=payload.get("fill_id", str(uuid.uuid4())),
            symbol=payload["symbol"],
            side=payload["side"],
            quantity=float(payload["quantity"]),
            price=float(payload["price"]),
            fee=float(payload.get("fee", 0)),
            ts=ts,
        )
        session.add(row)


    async def _upsert_position(
        self, session: AsyncSession, payload: dict[str, Any], ts: datetime
    ) -> None:
        if not payload.get("strategy_id"):
            return
        row = PositionRow(
            id=uuid.uuid4(),
            strategy_id=uuid.UUID(payload["strategy_id"]),
            leg_id=payload.get("leg_id", str(uuid.uuid4())),
            symbol=payload["symbol"],
            side=payload.get("side", "long"),
            quantity=float(payload.get("quantity", 0)),
            entry_price=float(payload.get("entry_price", 0)),
            unrealized_pnl=float(payload.get("unrealized_pnl", 0)),
            ladder_step=int(payload.get("step", 0)),
            updated_at=ts,
        )
        session.add(row)
