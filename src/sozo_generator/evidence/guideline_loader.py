from __future__ import annotations

import logging
from pathlib import Path
from ..core.utils import read_yaml_file, read_json
from ..schemas.evidence import ArticleMetadata
from ..core.enums import EvidenceType, EvidenceLevel

logger = logging.getLogger(__name__)


class GuidelineLoader:
    """Loads manually curated guideline sources from YAML/JSON drop-in files."""

    def __init__(self, guidelines_dir: Path | str = "data/raw/guidelines/"):
        self.guidelines_dir = Path(guidelines_dir)

    def load_for_condition(self, condition_slug: str) -> list[ArticleMetadata]:
        """Load all manual guideline entries for a condition."""
        articles = []
        # Try YAML first
        yaml_path = self.guidelines_dir / f"{condition_slug}_guidelines.yaml"
        json_path = self.guidelines_dir / f"{condition_slug}_guidelines.json"

        source_path = None
        if yaml_path.exists():
            source_path = yaml_path
            data = read_yaml_file(source_path)
        elif json_path.exists():
            source_path = json_path
            data = read_json(source_path)
        else:
            logger.debug(f"No manual guidelines for condition: {condition_slug}")
            return []

        for entry in data.get("sources", []):
            try:
                articles.append(
                    ArticleMetadata(
                        pmid=entry.get("pmid"),
                        doi=entry.get("doi"),
                        title=entry["title"],
                        authors=entry.get("authors", []),
                        journal=entry.get("journal"),
                        year=entry.get("year"),
                        abstract=entry.get("abstract"),
                        evidence_type=EvidenceType(
                            entry.get("type", EvidenceType.CLINICAL_PRACTICE_GUIDELINE.value)
                        ),
                        evidence_level=EvidenceLevel(
                            entry.get("level", EvidenceLevel.HIGHEST.value)
                        ),
                        score=entry.get("score", 5),
                        key_findings=entry.get("key_findings", []),
                        manually_added=True,
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to parse guideline entry: {e}")

        logger.info(f"Loaded {len(articles)} manual guideline sources for {condition_slug}")
        return articles
