"""
SOZO QA — Citation format and validity checker.
Checks citations are properly formatted and not fabricated.
"""
import logging
import re
from collections import Counter

from ..schemas.condition import ConditionSchema

logger = logging.getLogger(__name__)

_PMID_RE = re.compile(r"PMID:\s*(\d{7,9})", re.IGNORECASE)
_DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s\"'<>]+", re.IGNORECASE)
_PLACEHOLDER_PATTERNS = re.compile(
    r"\[CITATION NEEDED\]|\[PLACEHOLDER\]|\[REF\]|\bTBD\b|\bXXX\b",
    re.IGNORECASE,
)

_MIN_VALID_PMIDS = 3


def _ref_to_str(ref) -> str:
    """Coerce a reference entry (str or dict) to a plain string."""
    if isinstance(ref, str):
        return ref
    if isinstance(ref, dict):
        for key in ("citation", "text", "reference", "source", "raw"):
            if key in ref and isinstance(ref[key], str):
                return ref[key]
        return " ".join(str(v) for v in ref.values())
    return str(ref)


class CitationChecker:
    """Checks citation formatting and flags potential issues."""

    def check_condition_citations(self, condition: ConditionSchema) -> dict:
        """
        Check all citations for a condition.

        Returns a dict with keys:
            condition, total_citations, valid_pmid_format,
            has_doi_format, placeholder_citations,
            duplicate_pmids, issues, passed
        """
        refs = condition.references or []
        total_citations = len(refs)

        pmid_counter: Counter = Counter()
        valid_pmid_count = 0
        doi_count = 0
        placeholder_count = 0
        issues: list[str] = []

        for ref in refs:
            text = _ref_to_str(ref)

            # PMID extraction
            pmids_in_ref = _PMID_RE.findall(text)
            for pmid in pmids_in_ref:
                pmid_counter[pmid] += 1
                valid_pmid_count += 1

            # DOI detection
            if _DOI_RE.search(text):
                doi_count += 1

            # Placeholder detection
            if _PLACEHOLDER_PATTERNS.search(text):
                placeholder_count += 1
                logger.warning(
                    "Citation check: placeholder citation found in condition '%s': %.80s",
                    condition.slug,
                    text,
                )

        # Duplicate PMIDs (appear more than once across all references)
        duplicate_pmids: list[str] = [
            pmid for pmid, count in pmid_counter.items() if count > 1
        ]

        # Build issues list
        if placeholder_count > 0:
            issues.append(
                f"{placeholder_count} placeholder citation(s) found — requires human review."
            )

        if valid_pmid_count < _MIN_VALID_PMIDS:
            issues.append(
                f"Only {valid_pmid_count} valid PMID(s) found; minimum required is {_MIN_VALID_PMIDS}."
            )

        if duplicate_pmids:
            issues.append(
                f"Duplicate PMIDs detected: {', '.join(duplicate_pmids)}."
            )

        if total_citations == 0:
            issues.append("No references found for this condition.")

        passed = placeholder_count == 0 and valid_pmid_count >= _MIN_VALID_PMIDS

        if not passed:
            logger.warning(
                "Citation check: condition '%s' failed — %s",
                condition.slug,
                "; ".join(issues),
            )

        return {
            "condition": condition.slug,
            "total_citations": total_citations,
            "valid_pmid_format": valid_pmid_count,
            "has_doi_format": doi_count,
            "placeholder_citations": placeholder_count,
            "duplicate_pmids": duplicate_pmids,
            "issues": issues,
            "passed": passed,
        }
