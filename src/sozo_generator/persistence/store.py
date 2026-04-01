"""
Production-ready persistence abstraction.
JSON/file store for local development. Interface designed for database backends.
"""
from __future__ import annotations
import abc
import json
import logging
from pathlib import Path
from typing import Optional, TypeVar, Generic
from dataclasses import asdict

logger = logging.getLogger(__name__)
T = TypeVar("T")

class BaseStore(abc.ABC):
    """Abstract store interface — implement for JSON, SQLite, PostgreSQL, etc."""

    @abc.abstractmethod
    def save(self, key: str, data: dict) -> None: ...

    @abc.abstractmethod
    def load(self, key: str) -> Optional[dict]: ...

    @abc.abstractmethod
    def delete(self, key: str) -> bool: ...

    @abc.abstractmethod
    def list_keys(self, prefix: str = "") -> list[str]: ...

    @abc.abstractmethod
    def exists(self, key: str) -> bool: ...


class JSONFileStore(BaseStore):
    """JSON file-backed store. Each record is a file: {store_dir}/{key}.json"""

    def __init__(self, store_dir: Path):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, data: dict) -> None:
        path = self._key_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def load(self, key: str) -> Optional[dict]:
        path = self._key_path(key)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Failed to load %s: %s", key, e)
            return None

    def delete(self, key: str) -> bool:
        path = self._key_path(key)
        if path.exists():
            path.unlink()
            return True
        return False

    def list_keys(self, prefix: str = "") -> list[str]:
        keys = []
        for p in sorted(self.store_dir.rglob("*.json")):
            # Reconstruct the key from the relative path (strip .json)
            rel = p.relative_to(self.store_dir)
            key = str(rel).replace(".json", "").replace("\\", "/")
            if prefix and not key.startswith(prefix):
                continue
            keys.append(key)
        return keys

    def exists(self, key: str) -> bool:
        return self._key_path(key).exists()

    def _key_path(self, key: str) -> Path:
        # Support nested keys: "reviews/build-123" → store_dir/reviews/build-123.json
        return self.store_dir / f"{key}.json"


class NamespacedStore:
    """Wraps a BaseStore with a namespace prefix for logical separation."""

    def __init__(self, store: BaseStore, namespace: str):
        self._store = store
        self._ns = namespace

    def save(self, key: str, data: dict) -> None:
        self._store.save(f"{self._ns}/{key}", data)

    def load(self, key: str) -> Optional[dict]:
        return self._store.load(f"{self._ns}/{key}")

    def delete(self, key: str) -> bool:
        return self._store.delete(f"{self._ns}/{key}")

    def list_keys(self) -> list[str]:
        all_keys = self._store.list_keys(prefix=self._ns)
        # Strip namespace prefix
        prefix = f"{self._ns}/"
        return [k[len(prefix):] if k.startswith(prefix) else k for k in all_keys]

    def exists(self, key: str) -> bool:
        return self._store.exists(f"{self._ns}/{key}")
