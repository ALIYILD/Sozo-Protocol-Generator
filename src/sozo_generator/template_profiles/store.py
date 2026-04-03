"""
Template Profile Storage — save, load, list, and manage template profiles.

Profiles are stored as JSON files in a configurable directory
(default: data/template_profiles/).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from .models import TemplateProfile

logger = logging.getLogger(__name__)

DEFAULT_PROFILES_DIR = Path("data/template_profiles")


class TemplateProfileStore:
    """Persistent storage for learned template profiles."""

    def __init__(self, profiles_dir: str | Path | None = None):
        self.profiles_dir = Path(profiles_dir) if profiles_dir else DEFAULT_PROFILES_DIR
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    def save(self, profile: TemplateProfile) -> Path:
        """Save a template profile to disk."""
        filename = f"{profile.profile_id}.json"
        path = self.profiles_dir / filename
        data = profile.model_dump(mode="json")
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        logger.info(f"Template profile saved: {path}")
        return path

    def load(self, profile_id: str) -> Optional[TemplateProfile]:
        """Load a template profile by ID."""
        path = self.profiles_dir / f"{profile_id}.json"
        if not path.exists():
            logger.warning(f"Template profile not found: {profile_id}")
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return TemplateProfile(**data)
        except Exception as e:
            logger.error(f"Failed to load template profile {profile_id}: {e}")
            return None

    def list_profiles(self) -> list[dict]:
        """List all stored template profiles (summary info only)."""
        profiles = []
        for path in sorted(self.profiles_dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                profiles.append({
                    "profile_id": data.get("profile_id", path.stem),
                    "name": data.get("name", ""),
                    "source_filename": data.get("source_filename", ""),
                    "template_type": data.get("template_type", ""),
                    "inferred_doc_type": data.get("inferred_doc_type", ""),
                    "tier": data.get("tier", ""),
                    "source_condition": data.get("source_condition", ""),
                    "total_sections": data.get("total_sections", 0),
                    "created_at": data.get("created_at", ""),
                })
            except Exception as e:
                logger.debug(f"Could not read profile {path}: {e}")
        return profiles

    def exists(self, profile_id: str) -> bool:
        """Check if a profile exists."""
        return (self.profiles_dir / f"{profile_id}.json").exists()

    def delete(self, profile_id: str) -> bool:
        """Delete a template profile."""
        path = self.profiles_dir / f"{profile_id}.json"
        if path.exists():
            path.unlink()
            logger.info(f"Deleted template profile: {profile_id}")
            return True
        return False
