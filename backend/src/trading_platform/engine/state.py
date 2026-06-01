"""Shared runtime state between API and engine."""

from __future__ import annotations

import asyncio

_emergency_stop: bool = False
_lock = asyncio.Lock()


def is_emergency_stop() -> bool:
    return _emergency_stop


async def set_emergency_stop(active: bool) -> None:
    global _emergency_stop
    async with _lock:
        _emergency_stop = active
