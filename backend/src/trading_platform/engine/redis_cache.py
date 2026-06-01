"""Optional Redis pub/sub to invalidate config cache (plan §6)."""

from __future__ import annotations

import logging

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

CHANNEL = "trading:config:refresh"


class RedisConfigNotifier:
    def __init__(self, url: str = "redis://localhost:6379/0") -> None:
        self._url = url
        self._redis: aioredis.Redis | None = None

    async def connect(self) -> None:
        try:
            self._redis = aioredis.from_url(self._url, decode_responses=True)
            await self._redis.ping()
            logger.info("Redis config notifier connected")
        except Exception as e:
            logger.warning("Redis unavailable for config notify: %s", e)
            self._redis = None

    async def notify_refresh(self) -> None:
        if self._redis:
            await self._redis.publish(CHANNEL, "refresh")

    async def subscribe_loop(self, callback) -> None:
        if not self._redis:
            return
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(CHANNEL)
        async for msg in pubsub.listen():
            if msg.get("type") == "message":
                await callback()

    async def close(self) -> None:
        if self._redis:
            await self._redis.close()


_notifier: RedisConfigNotifier | None = None


def get_notifier() -> RedisConfigNotifier:
    global _notifier
    if _notifier is None:
        _notifier = RedisConfigNotifier()
    return _notifier
