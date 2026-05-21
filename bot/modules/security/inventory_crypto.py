from __future__ import annotations
import base64
import hashlib

from cryptography.fernet import Fernet


class InventoryCipher:
    def __init__(self, secret: str) -> None:
        if not secret:
            msg = "inventory_encryption_key_required"
            raise ValueError(msg)

        key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
        self._fernet = Fernet(key)

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        return self._fernet.decrypt(value.encode()).decode()
