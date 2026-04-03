"""
Knowledge Loader — loads and validates YAML knowledge objects.

Reads YAML files from sozo_knowledge/knowledge/ and parses them
into validated Pydantic models.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TypeVar, Type

import yaml
from pydantic import BaseModel

from .schemas import (
    KnowledgeCondition,
    KnowledgeModality,
    KnowledgeAssessment,
    KnowledgeBrainTarget,
    KnowledgeEvidenceMap,
    KnowledgeContraindication,
    SharedClinicalRule,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

KNOWLEDGE_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "sozo_knowledge" / "knowledge"


def _load_yaml(path: Path) -> dict:
    """Load a single YAML file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_and_validate(path: Path, model_class: Type[T]) -> T:
    """Load a YAML file and validate it against a Pydantic model."""
    data = _load_yaml(path)
    return model_class(**data)


def load_conditions(knowledge_dir: Path | None = None) -> dict[str, KnowledgeCondition]:
    """Load all condition knowledge objects."""
    base = (knowledge_dir or KNOWLEDGE_ROOT) / "conditions"
    conditions = {}
    if not base.exists():
        return conditions
    for path in sorted(base.glob("*.yaml")):
        if path.stem.startswith("_"):
            continue
        try:
            condition = _load_and_validate(path, KnowledgeCondition)
            conditions[condition.slug] = condition
            logger.debug(f"Loaded condition: {condition.slug}")
        except Exception as e:
            logger.error(f"Failed to load condition {path.name}: {e}")
    return conditions


def load_modalities(knowledge_dir: Path | None = None) -> dict[str, KnowledgeModality]:
    """Load all modality knowledge objects."""
    base = (knowledge_dir or KNOWLEDGE_ROOT) / "modalities"
    modalities = {}
    if not base.exists():
        return modalities
    for path in sorted(base.glob("*.yaml")):
        if path.stem.startswith("_"):
            continue
        try:
            mod = _load_and_validate(path, KnowledgeModality)
            modalities[mod.slug] = mod
            logger.debug(f"Loaded modality: {mod.slug}")
        except Exception as e:
            logger.error(f"Failed to load modality {path.name}: {e}")
    return modalities


def load_assessments(knowledge_dir: Path | None = None) -> dict[str, KnowledgeAssessment]:
    """Load all assessment knowledge objects."""
    base = (knowledge_dir or KNOWLEDGE_ROOT) / "assessments"
    assessments = {}
    if not base.exists():
        return assessments
    for path in sorted(base.glob("*.yaml")):
        if path.stem.startswith("_"):
            continue
        try:
            asmt = _load_and_validate(path, KnowledgeAssessment)
            assessments[asmt.slug] = asmt
        except Exception as e:
            logger.error(f"Failed to load assessment {path.name}: {e}")
    return assessments


def load_brain_targets(knowledge_dir: Path | None = None) -> dict[str, KnowledgeBrainTarget]:
    """Load all brain target knowledge objects."""
    base = (knowledge_dir or KNOWLEDGE_ROOT) / "targets"
    targets = {}
    if not base.exists():
        return targets
    for path in sorted(base.glob("*.yaml")):
        if path.stem.startswith("_"):
            continue
        try:
            target = _load_and_validate(path, KnowledgeBrainTarget)
            targets[target.slug] = target
        except Exception as e:
            logger.error(f"Failed to load brain target {path.name}: {e}")
    return targets


def load_evidence_maps(knowledge_dir: Path | None = None) -> list[KnowledgeEvidenceMap]:
    """Load all evidence map objects."""
    base = (knowledge_dir or KNOWLEDGE_ROOT) / "evidence_maps"
    maps = []
    if not base.exists():
        return maps
    for path in sorted(base.glob("*.yaml")):
        if path.stem.startswith("_"):
            continue
        try:
            data = _load_yaml(path)
            # File may contain a list of evidence maps
            if isinstance(data, list):
                for item in data:
                    maps.append(KnowledgeEvidenceMap(**item))
            elif isinstance(data, dict):
                if "maps" in data:
                    for item in data["maps"]:
                        maps.append(KnowledgeEvidenceMap(**item))
                else:
                    maps.append(KnowledgeEvidenceMap(**data))
        except Exception as e:
            logger.error(f"Failed to load evidence map {path.name}: {e}")
    return maps


def load_contraindications(knowledge_dir: Path | None = None) -> dict[str, KnowledgeContraindication]:
    """Load all contraindication profiles."""
    base = (knowledge_dir or KNOWLEDGE_ROOT) / "contraindications"
    contras = {}
    if not base.exists():
        return contras
    for path in sorted(base.glob("*.yaml")):
        if path.stem.startswith("_"):
            continue
        try:
            data = _load_yaml(path)
            if "contraindications" in data:
                for item in data["contraindications"]:
                    c = KnowledgeContraindication(**item)
                    contras[c.slug] = c
            else:
                c = KnowledgeContraindication(**data)
                contras[c.slug] = c
        except Exception as e:
            logger.error(f"Failed to load contraindication {path.name}: {e}")
    return contras


def load_shared_rules(knowledge_dir: Path | None = None) -> dict[str, SharedClinicalRule]:
    """Load all shared clinical rules."""
    base = (knowledge_dir or KNOWLEDGE_ROOT) / "shared"
    rules = {}
    if not base.exists():
        return rules
    for path in sorted(base.glob("*.yaml")):
        if path.stem.startswith("_"):
            continue
        try:
            data = _load_yaml(path)
            if "rules" in data:
                for item in data["rules"]:
                    r = SharedClinicalRule(**item)
                    rules[r.slug] = r
            else:
                r = SharedClinicalRule(**data)
                rules[r.slug] = r
        except Exception as e:
            logger.error(f"Failed to load shared rule {path.name}: {e}")
    return rules
