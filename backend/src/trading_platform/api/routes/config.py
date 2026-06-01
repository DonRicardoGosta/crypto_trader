from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from trading_platform.adapters.persistence.models import ApiCredentialRow, AppConfigRow
from trading_platform.api.deps import get_session
from trading_platform.api.schemas import AppConfigSet, CredentialCreate, CredentialOut
from trading_platform.config import settings
from trading_platform.core.crypto import decrypt, encrypt

router = APIRouter()


@router.get("/config/{key}")
async def get_config(key: str, session: AsyncSession = Depends(get_session)):
    row = await session.get(AppConfigRow, key)
    if not row:
        return {"key": key, "value": {}}
    return {"key": key, "value": row.value}


@router.put("/config")
async def set_config(body: AppConfigSet, session: AsyncSession = Depends(get_session)):
    row = await session.get(AppConfigRow, body.key)
    if row:
        row.value = body.value
    else:
        session.add(AppConfigRow(key=body.key, value=body.value))
    await session.commit()
    return {"key": body.key, "value": body.value}


@router.get("/credentials", response_model=list[CredentialOut])
async def list_credentials(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ApiCredentialRow))
    return [
        CredentialOut(id=r.id, exchange=r.exchange, label=r.label, is_active=r.is_active)
        for r in result.scalars().all()
    ]


@router.post("/credentials", response_model=CredentialOut)
async def create_credential(body: CredentialCreate, session: AsyncSession = Depends(get_session)):
    row = ApiCredentialRow(
        id=uuid.uuid4(),
        exchange=body.exchange,
        label=body.label,
        api_key_encrypted=encrypt(body.api_key, settings.secrets_master_key),
        api_secret_encrypted=encrypt(body.api_secret, settings.secrets_master_key),
        is_active=True,
    )
    session.add(row)
    await session.commit()
    return CredentialOut(id=row.id, exchange=row.exchange, label=row.label, is_active=row.is_active)


@router.get("/credentials/{cred_id}/reveal")
async def reveal_credential(cred_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    row = await session.get(ApiCredentialRow, cred_id)
    if not row:
        raise HTTPException(404)
    return {
        "api_key": decrypt(row.api_key_encrypted, settings.secrets_master_key),
        "api_secret": decrypt(row.api_secret_encrypted, settings.secrets_master_key),
    }
