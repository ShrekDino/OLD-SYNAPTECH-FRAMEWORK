import json
import logging
import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from src.shared.constants import AES_KEY_SIZE, AES_NONCE_SIZE
from src.shared.schemas import EncryptedBlob

logger = logging.getLogger(__name__)


class EncryptionService:
    _instance: Optional["EncryptionService"] = None

    def __init__(self, master_key: Optional[bytes] = None):
        self._master_key = master_key or AESGCM.generate_key(bit_length=AES_KEY_SIZE * 8)
        self._aesgcm = AESGCM(self._master_key)
        self._key_id = os.urandom(8).hex()

    @classmethod
    def get_instance(cls) -> "EncryptionService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def encrypt_blob(self, plaintext: bytes, aad: bytes = b"") -> EncryptedBlob:
        nonce = os.urandom(AES_NONCE_SIZE)
        ciphertext = self._aesgcm.encrypt(nonce, plaintext, aad)
        return EncryptedBlob(
            ciphertext=ciphertext,
            nonce=nonce,
            tag=b"",
            key_id=self._key_id,
            s3_uri="",
        )

    def decrypt_blob(self, blob: EncryptedBlob, aad: bytes = b"") -> bytes:
        return self._aesgcm.decrypt(blob.nonce, blob.ciphertext, aad)

    def encrypt_dict(self, data: dict) -> EncryptedBlob:
        serialized = json.dumps(data, default=str).encode("utf-8")
        return self.encrypt_blob(serialized)

    def decrypt_dict(self, blob: EncryptedBlob) -> dict:
        plaintext = self.decrypt_blob(blob)
        return json.loads(plaintext.decode("utf-8"))

    @property
    def key_id(self) -> str:
        return self._key_id
