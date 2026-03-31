import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class EvidenceCache:
    """File-based cache for PubMed query results and processed evidence."""

    def __init__(self, cache_dir: Path | str, ttl_days: int = 30):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_days = ttl_days

    def _key_to_path(self, key: str) -> Path:
        h = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{h}.json"

    def get(self, key: str) -> Optional[Any]:
        path = self._key_to_path(key)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                record = json.load(f)
            cached_at = datetime.fromisoformat(record.get("cached_at", "2000-01-01"))
            if datetime.now() - cached_at > timedelta(days=self.ttl_days):
                logger.debug(f"Cache expired for key: {key[:60]}")
                return None
            return record.get("data")
        except Exception as e:
            logger.warning(f"Cache read error for {key[:60]}: {e}")
            return None

    def set(self, key: str, data: Any) -> None:
        path = self._key_to_path(key)
        record = {
            "key": key[:200],
            "cached_at": datetime.now().isoformat(),
            "data": data,
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, default=str)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

    def invalidate(self, key: str) -> None:
        path = self._key_to_path(key)
        if path.exists():
            path.unlink()

    def clear_condition(self, condition_slug: str) -> int:
        """Clear all cache entries containing condition_slug in key."""
        cleared = 0
        for p in self.cache_dir.glob("*.json"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    record = json.load(f)
                if condition_slug in record.get("key", ""):
                    p.unlink()
                    cleared += 1
            except Exception:
                pass
        return cleared

    def stats(self) -> dict:
        files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in files)
        return {
            "total_entries": len(files),
            "total_size_kb": round(total_size / 1024, 2),
            "cache_dir": str(self.cache_dir),
        }
