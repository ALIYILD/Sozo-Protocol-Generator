from __future__ import annotations

import logging
from pathlib import Path
import yaml
from ..core.utils import read_yaml_file
from ..schemas.condition import AssessmentTool

logger = logging.getLogger(__name__)


class ScalesResolver:
    """Resolves validated assessment scales for conditions from the catalog."""

    def __init__(self, catalog_path: Path | str = "data/reference/scales_catalog.yaml"):
        self.catalog_path = Path(catalog_path)
        self._catalog: dict = {}
        self._load()

    def _load(self) -> None:
        if self.catalog_path.exists():
            data = read_yaml_file(self.catalog_path)
            self._catalog = data.get("scales", {})
            logger.debug(f"Loaded {len(self._catalog)} scales from catalog")
        else:
            logger.warning(f"Scales catalog not found at {self.catalog_path}")

    def get_scales_for_condition(self, condition_slug: str) -> list[AssessmentTool]:
        """Return all validated scales for a given condition."""
        tools = []
        for key, data in self._catalog.items():
            conditions = data.get("conditions", [])
            if condition_slug in conditions:
                tools.append(
                    AssessmentTool(
                        scale_key=key,
                        name=data.get("name", key),
                        abbreviation=data.get("abbreviation", key.upper()),
                        domains=data.get("domains", []),
                        evidence_pmid=data.get("pmid"),
                        timing="baseline",
                    )
                )
        return tools

    def get_scale(self, scale_key: str) -> dict:
        return self._catalog.get(scale_key, {})
