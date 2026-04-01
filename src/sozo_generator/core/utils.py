from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any


def slugify(text: str) -> str:
    """Convert text to URL/file-safe slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", text)


def ensure_dir(path: Path | str) -> Path:
    """Create directory if it does not exist. Return Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_json(data: Any, path: Path | str, indent: int = 2) -> None:
    """Write data to JSON file."""
    p = Path(path)
    ensure_dir(p.parent)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False, default=str)


def read_json(path: Path | str) -> Any:
    """Read JSON file."""
    with open(Path(path), "r", encoding="utf-8") as f:
        return json.load(f)


def write_yaml_file(data: Any, path: Path | str) -> None:
    """Write data to YAML file."""
    import yaml
    p = Path(path)
    ensure_dir(p.parent)
    with open(p, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


def read_yaml_file(path: Path | str) -> Any:
    """Read YAML file."""
    import yaml
    with open(Path(path), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def content_hash(text: str) -> str:
    """Generate MD5 hash for content deduplication."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def current_date_str() -> str:
    """Return current date as YYYY-MM-DD string."""
    return datetime.now().strftime("%Y-%m-%d")


def current_month_year() -> str:
    """Return current date as 'Month YYYY' string."""
    return datetime.now().strftime("%B %Y")


def truncate_text(text: str, max_chars: int = 500) -> str:
    """Truncate text to max_chars, appending ellipsis if truncated."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "\u2026"


def clean_abstract(text: str) -> str:
    """Clean PubMed abstract text: remove XML tags, normalize whitespace."""
    # Remove XML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


PLACEHOLDER_PATTERN = re.compile(r"\[(?:PLACEHOLDER|TODO|REVIEW|TBD|INSERT)[^\]]*\]", re.IGNORECASE)


def has_placeholder(text: str) -> bool:
    """Check if text contains placeholder markers."""
    return bool(PLACEHOLDER_PATTERN.search(text))


def format_authors(authors: list[str], max_authors: int = 3) -> str:
    """Format author list for citation display."""
    if not authors:
        return ""
    if len(authors) <= max_authors:
        return ", ".join(authors)
    return ", ".join(authors[:max_authors]) + " et al."
