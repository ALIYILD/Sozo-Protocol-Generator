"""
Canonical data loader for protocol, handbook, and assessment data.

Supports loading from:
1. YAML files in data/reference/protocol_data/ (preferred)
2. Legacy Python dict modules (fallback during migration)

Usage:
    from sozo_generator.core.data_loader import load_protocol_data, load_shared_protocol_data

    shared = load_shared_protocol_data()
    pd_data = load_protocol_data("parkinsons")
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)

_DATA_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "data" / "reference"
_PROTOCOL_DIR = _DATA_ROOT / "protocol_data"


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file and return its contents as a dict."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_shared_protocol_data() -> dict[str, Any]:
    """Load shared device/safety protocol data (_shared.yaml)."""
    shared_path = _PROTOCOL_DIR / "_shared.yaml"
    if shared_path.exists():
        logger.debug(f"Loading shared protocol data from {shared_path}")
        return _load_yaml(shared_path)
    logger.warning("Shared protocol data YAML not found; returning empty dict")
    return {}


def load_protocol_data(slug: str) -> Optional[dict[str, Any]]:
    """Load protocol data for a single condition.

    Checks YAML first, falls back to legacy Python dicts if YAML not found.
    Returns None if no data source is available.
    """
    yaml_path = _PROTOCOL_DIR / f"{slug}.yaml"
    if yaml_path.exists():
        logger.debug(f"Loading protocol data for {slug} from YAML")
        return _load_yaml(yaml_path)

    # Fallback: try legacy Python module
    return _load_from_legacy_module(slug)


def _load_from_legacy_module(slug: str) -> Optional[dict[str, Any]]:
    """Try to load from scripts/protocol_data.py as fallback."""
    try:
        import importlib
        import sys
        # Add scripts/ to path temporarily
        scripts_dir = str(Path(__file__).resolve().parent.parent.parent.parent / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        mod = importlib.import_module("protocol_data")
        conditions = getattr(mod, "CONDITIONS", {})
        if slug in conditions:
            logger.debug(f"Loaded protocol data for {slug} from legacy Python module")
            return conditions[slug]
    except ImportError:
        logger.debug(f"Legacy protocol_data module not importable for {slug}")
    except Exception as e:
        logger.debug(f"Failed to load legacy data for {slug}: {e}")
    return None


def list_available_conditions() -> list[str]:
    """List all conditions that have YAML protocol data files."""
    if not _PROTOCOL_DIR.exists():
        return []
    return sorted(
        p.stem for p in _PROTOCOL_DIR.glob("*.yaml")
        if not p.stem.startswith("_")
    )


def load_condition_list() -> list[dict[str, Any]]:
    """Load the master condition list from data/reference/condition_list.yaml."""
    path = _DATA_ROOT / "condition_list.yaml"
    if path.exists():
        data = _load_yaml(path)
        return data.get("conditions", [])
    return []
