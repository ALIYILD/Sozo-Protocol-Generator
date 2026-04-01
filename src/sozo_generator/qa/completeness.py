"""
SOZO QA — Document completeness checker.
Verifies all expected documents exist and are non-trivial size.
"""
from __future__ import annotations

import logging
from pathlib import Path

from ..core.enums import DocumentType, Tier

logger = logging.getLogger(__name__)

# All 8 document types (as slug strings for file naming)
_DOC_TYPE_SLUGS: list[str] = [
    DocumentType.CLINICAL_EXAM.value,
    DocumentType.PHENOTYPE_CLASSIFICATION.value,
    DocumentType.RESPONDER_TRACKING.value,
    DocumentType.PSYCH_INTAKE.value,
    DocumentType.NETWORK_ASSESSMENT.value,
    DocumentType.HANDBOOK.value,
    DocumentType.ALL_IN_ONE_PROTOCOL.value,
    DocumentType.EVIDENCE_BASED_PROTOCOL.value,
]

_TIERS: list[str] = [Tier.FELLOW.value, Tier.PARTNERS.value]

_SMALL_FILE_THRESHOLD_BYTES = 5000


class CompletenessChecker:
    """Checks that all expected output documents exist and are non-trivially sized."""

    def _expected_filenames(self, condition_slug: str) -> list[str]:
        """Return list of expected .docx filenames for a condition."""
        files: list[str] = []
        for doc_type_slug in _DOC_TYPE_SLUGS:
            for tier in _TIERS:
                files.append(f"{condition_slug}_{doc_type_slug}_{tier}.docx")
        return files

    def check_condition(self, condition_slug: str, output_dir: Path) -> dict:
        """
        Check completeness for a single condition.

        Returns a dict with keys:
            condition, total_expected, total_found, missing, small_files, passed
        """
        expected = self._expected_filenames(condition_slug)
        missing: list[str] = []
        small_files: list[str] = []
        found_count = 0

        for filename in expected:
            file_path = output_dir / filename
            if not file_path.exists():
                logger.warning(
                    "Completeness check: missing file %s for condition '%s'",
                    filename,
                    condition_slug,
                )
                missing.append(filename)
            else:
                found_count += 1
                size = file_path.stat().st_size
                if size < _SMALL_FILE_THRESHOLD_BYTES:
                    logger.warning(
                        "Completeness check: small file %s (%d bytes) for condition '%s'",
                        filename,
                        size,
                        condition_slug,
                    )
                    small_files.append(filename)

        passed = len(missing) == 0 and len(small_files) == 0

        return {
            "condition": condition_slug,
            "total_expected": len(expected),
            "total_found": found_count,
            "missing": missing,
            "small_files": small_files,
            "passed": passed,
        }

    def check_all(self, output_dir: Path) -> dict[str, dict]:
        """
        Run check_condition for all condition slugs found in output_dir.

        Detects slugs by scanning for .docx files whose names match the
        expected naming pattern ``{slug}_{doc_type_slug}_{tier}.docx``.
        """
        if not output_dir.exists():
            logger.warning(
                "Completeness check: output_dir does not exist: %s", output_dir
            )
            return {}

        # Build a set of known suffix patterns to strip when extracting slugs
        known_suffixes: set[str] = set()
        for doc_type_slug in _DOC_TYPE_SLUGS:
            for tier in _TIERS:
                known_suffixes.add(f"_{doc_type_slug}_{tier}")

        slugs: set[str] = set()
        for docx_file in output_dir.glob("*.docx"):
            stem = docx_file.stem  # filename without .docx
            for suffix in known_suffixes:
                if stem.endswith(suffix):
                    slug = stem[: -len(suffix)]
                    slugs.add(slug)
                    break

        if not slugs:
            logger.warning(
                "Completeness check: no generated files found in %s", output_dir
            )
            return {}

        results: dict[str, dict] = {}
        for slug in sorted(slugs):
            results[slug] = self.check_condition(slug, output_dir)

        return results
