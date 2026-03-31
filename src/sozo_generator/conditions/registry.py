import logging
from pathlib import Path
from typing import Optional, TYPE_CHECKING
import yaml
from ..core.utils import read_yaml_file
from ..core.exceptions import ConditionNotFoundError

if TYPE_CHECKING:
    from ..schemas.condition import ConditionSchema

logger = logging.getLogger(__name__)


class ConditionRegistry:
    """Central registry of all supported conditions.

    Two access modes:
    - get_meta(slug) → dict — lightweight metadata from condition_list.yaml
    - get_schema(slug) → ConditionSchema — full evidence-based schema from generator
    - get(slug) → ConditionSchema — alias for get_schema (preferred)
    """

    def __init__(self, condition_list_path: Path | str = "data/reference/condition_list.yaml"):
        self.condition_list_path = Path(condition_list_path)
        self._meta: dict[str, dict] = {}
        self._schema_cache: dict[str, "ConditionSchema"] = {}
        self._load()

    def _load(self) -> None:
        if not self.condition_list_path.exists():
            logger.warning(f"Condition list not found: {self.condition_list_path}")
        else:
            data = read_yaml_file(self.condition_list_path)
            for c in data.get("conditions", []):
                self._meta[c["slug"]] = c
            logger.info(f"Registered {len(self._meta)} conditions from YAML")

        # Always register from builders (authoritative)
        try:
            from .generators import CONDITION_BUILDERS
            for slug in CONDITION_BUILDERS:
                if slug not in self._meta:
                    self._meta[slug] = {"slug": slug}
            logger.info(f"Registry has {len(self._meta)} conditions total")
        except ImportError as e:
            logger.warning(f"Could not import CONDITION_BUILDERS: {e}")

    def get_meta(self, slug: str) -> dict:
        """Return lightweight metadata dict for a condition."""
        if slug not in self._meta:
            raise ConditionNotFoundError(f"Condition '{slug}' not found in registry")
        return self._meta[slug]

    def get_schema(self, slug: str) -> "ConditionSchema":
        """Return full ConditionSchema by calling the condition builder."""
        if slug in self._schema_cache:
            return self._schema_cache[slug]
        try:
            from .generators import CONDITION_BUILDERS
        except ImportError as e:
            raise ConditionNotFoundError(f"Cannot import condition builders: {e}")
        if slug not in CONDITION_BUILDERS:
            raise ConditionNotFoundError(f"No builder found for condition '{slug}'")
        schema = CONDITION_BUILDERS[slug]()
        self._schema_cache[slug] = schema
        return schema

    def get(self, slug: str) -> "ConditionSchema":
        """Return full ConditionSchema (preferred access method)."""
        return self.get_schema(slug)

    def list_slugs(self) -> list[str]:
        return list(self._meta.keys())

    def list_all(self) -> list[dict]:
        return list(self._meta.values())

    def exists(self, slug: str) -> bool:
        return slug in self._meta


_registry: Optional[ConditionRegistry] = None


def get_registry() -> ConditionRegistry:
    global _registry
    if _registry is None:
        _registry = ConditionRegistry()
    return _registry
