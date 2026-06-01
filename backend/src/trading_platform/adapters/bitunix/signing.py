"""Bitunix API signature (double SHA256)."""

from __future__ import annotations

import hashlib
import json
import secrets
import time


def generate_nonce() -> str:
    return secrets.token_hex(16)


def sign_request(
    api_key: str,
    secret_key: str,
    query_params: str = "",
    body: str = "",
) -> dict[str, str]:
    nonce = generate_nonce()
    timestamp = str(int(time.time() * 1000))
    digest_input = nonce + timestamp + api_key + query_params + body
    digest = hashlib.sha256(digest_input.encode()).hexdigest()
    sign = hashlib.sha256((digest + secret_key).encode()).hexdigest()
    return {
        "api-key": api_key,
        "nonce": nonce,
        "timestamp": timestamp,
        "sign": sign,
        "Content-Type": "application/json",
    }


def sign_ws_params(api_key: str, secret_key: str, params: dict[str, str]) -> dict[str, str]:
    nonce = generate_nonce()
    timestamp = str(int(time.time() * 1000))
    sorted_params = "".join(
        f"{k}{v}" for k, v in sorted(params.items()) if k != "sign"
    )
    f"apiKey{api_key}nonce{nonce}symbol{params.get('symbol', '')}timestamp{timestamp}"
    if "symbol" not in params:
        pass
    digest = hashlib.sha256((nonce + timestamp + api_key + sorted_params).encode()).hexdigest()
    sign = hashlib.sha256((digest + secret_key).encode()).hexdigest()
    return {
        "apiKey": api_key,
        "nonce": nonce,
        "timestamp": timestamp,
        "sign": sign,
    }


def body_string(data: dict | None) -> str:
    if not data:
        return ""
    return json.dumps(data, separators=(",", ":"))
