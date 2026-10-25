"""Local encrypted demo vault. Production deployments must supply a managed key and object store."""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
from cryptography.fernet import Fernet

class EncryptedDocumentVault:
    def __init__(self) -> None:
        self.root = Path(__file__).resolve().parents[1] / "data" / "encrypted_documents"
        self.root.mkdir(parents=True, exist_ok=True)
        key_path = self.root.parent / ".local_vault_key"
        configured = os.getenv("SAKSHYA_DOCUMENT_ENCRYPTION_KEY")
        if configured:
            key = configured.encode()
            self.key_source = "ENVIRONMENT"
        elif key_path.exists():
            key = key_path.read_bytes()
            self.key_source = "LOCAL_DEMO_KEY"
        else:
            key = Fernet.generate_key()
            key_path.write_bytes(key)
            self.key_source = "LOCAL_DEMO_KEY"
        self.fernet = Fernet(key)

    def store(self, document_id: str, content: bytes) -> dict:
        encrypted = self.fernet.encrypt(content)
        path = self.root / f"{document_id}.bin"
        path.write_bytes(encrypted)
        return {"storage_ref": str(path.name), "sha256": hashlib.sha256(content).hexdigest(),
                "encrypted_at_rest": True, "key_source": self.key_source}
