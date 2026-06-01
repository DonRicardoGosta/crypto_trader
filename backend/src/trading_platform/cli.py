import asyncio
import logging

import uvicorn

from trading_platform.config import settings

logging.basicConfig(level=logging.INFO)


def run_api():
    uvicorn.run(
        "trading_platform.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )


def run_realtime_ws():
    uvicorn.run(
        "trading_platform.api.ws_app:ws_app",
        host=settings.api_host,
        port=settings.realtime_ws_port,
        reload=False,
    )


async def _run_engine():
    from sqlalchemy import select

    from trading_platform.adapters.persistence.broadcast_emitter import BroadcastingEventEmitter
    from trading_platform.adapters.persistence.kafka_emitter import KafkaEventEmitter
    from trading_platform.adapters.persistence.models import ApiCredentialRow
    from trading_platform.api.deps import async_session
    from trading_platform.config import settings as s
    from trading_platform.core.crypto import decrypt
    from trading_platform.engine.config_cache import ConfigCache
    from trading_platform.engine.runner import StrategyRunner

    emitter = BroadcastingEventEmitter(KafkaEventEmitter())
    await emitter.start()
    cache = ConfigCache()
    api_key, secret = "", ""
    try:
        async with async_session() as session:
            result = await session.execute(
                select(ApiCredentialRow).where(ApiCredentialRow.is_active.is_(True)).limit(1)
            )
            cred = result.scalar_one_or_none()
            if cred:
                api_key = decrypt(cred.api_key_encrypted, s.secrets_master_key)
                secret = decrypt(cred.api_secret_encrypted, s.secrets_master_key)
    except Exception:
        pass
    runner = StrategyRunner(cache, emitter, api_key, secret)
    await cache.refresh()
    await runner.start()
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await runner.stop()
        await emitter.stop()
        await cache.stop()


def run_engine():
    asyncio.run(_run_engine())


async def _run_db_writer():
    from trading_platform.adapters.persistence.db_writer import DbWriter

    writer = DbWriter()
    await writer.run()


def run_db_writer():
    asyncio.run(_run_db_writer())
