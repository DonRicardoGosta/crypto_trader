"""AES-256-GCM encryption for API credentials."""

from __future__ import annotations

import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _derive_key(master_key: str) -> bytes:
    return hashlib.sha256(master_key.encode()).digest()


def encrypt(plaintext: str, master_key: str) -> str:
    key = _derive_key(master_key)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ciphertext).decode()


def decrypt(token: str, master_key: str) -> str:
    key = _derive_key(master_key)
    raw = base64.b64decode(token)
    nonce, ciphertext = raw[:12], raw[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None).decode()
