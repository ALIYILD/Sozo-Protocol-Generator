"""Shared Pydantic validators for SOZO schemas."""
from __future__ import annotations

import re

_PMID_PATTERN = re.compile(r"^\d{1,9}$")


def validate_pmid(value: str | None) -> str | None:
    """Validate that a PMID is a non-empty string of 1-9 digits, or None.

    PubMed IDs are positive integers stored as strings. This validator
    rejects empty strings, whitespace-only strings, and non-numeric values.
    None is allowed (optional PMID fields).
    """
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None  # Treat empty/whitespace as absent
    if not _PMID_PATTERN.match(stripped):
        raise ValueError(
            f"Invalid PMID '{value}': must be 1-9 digits (e.g. '12345678')"
        )
    return stripped


def validate_pmid_list(values: list[str]) -> list[str]:
    """Validate a list of PMIDs, filtering out empty strings and None-like entries."""
    validated = []
    for v in values:
        result = validate_pmid(v)
        if result is not None:
            validated.append(result)
    return validated
