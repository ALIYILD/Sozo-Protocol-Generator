"""
SOZO QA — Evidence coverage checker.
Verifies conditions have sufficient evidence backing.
"""
import logging
import re

from ..schemas.condition import ConditionSchema

logger = logging.getLogger(__name__)

_PMID_RE = re.compile(r"PMID[:\s]\s*(\d{7,9})", re.IGNORECASE)
_CONFIDENCE_PASS_THRESHOLD = 0.6


def _extract_text_from_reference(ref) -> str:
    """Return a plain string from either a str or dict reference entry."""
    if isinstance(ref, str):
        return ref
    if isinstance(ref, dict):
        # Prefer common fields that might contain the PMID string
        for key in ("citation", "text", "reference", "source", "raw"):
            if key in ref and isinstance(ref[key], str):
                return ref[key]
        # Fallback: join all string values
        return " ".join(str(v) for v in ref.values())
    return str(ref)


class EvidenceCoverageChecker:
    """Checks whether a condition has sufficient evidence backing."""

    def check_condition(self, condition: ConditionSchema) -> dict:
        """
        Check evidence coverage for a single ConditionSchema.

        Returns a dict with keys:
            condition, has_references, reference_count,
            has_real_pmids, has_protocols, protocol_count,
            has_networks, has_phenotypes, evidence_gaps,
            confidence_score, passed
        """
        refs = condition.references or []
        has_references = bool(refs)
        reference_count = len(refs)

        # Check for at least one real PMID across all reference strings
        has_real_pmids = False
        for ref in refs:
            text = _extract_text_from_reference(ref)
            if _PMID_RE.search(text):
                has_real_pmids = True
                break

        protocols = condition.protocols or []
        has_protocols = bool(protocols)
        protocol_count = len(protocols)

        has_networks = bool(condition.network_profiles)
        has_phenotypes = bool(condition.phenotypes)

        evidence_gaps: list[str] = list(condition.evidence_gaps or [])

        confidence_score = round(
            (has_references * 0.3)
            + (has_real_pmids * 0.2)
            + (has_protocols * 0.2)
            + (has_networks * 0.2)
            + (has_phenotypes * 0.1),
            4,
        )

        passed = confidence_score >= _CONFIDENCE_PASS_THRESHOLD

        if not passed:
            logger.warning(
                "Evidence coverage: condition '%s' failed with confidence_score=%.2f",
                condition.slug,
                confidence_score,
            )

        return {
            "condition": condition.slug,
            "has_references": has_references,
            "reference_count": reference_count,
            "has_real_pmids": has_real_pmids,
            "has_protocols": has_protocols,
            "protocol_count": protocol_count,
            "has_networks": has_networks,
            "has_phenotypes": has_phenotypes,
            "evidence_gaps": evidence_gaps,
            "confidence_score": confidence_score,
            "passed": passed,
        }

    def check_all_conditions(self, registry) -> dict[str, dict]:
        """
        Run check_condition for every condition in a ConditionRegistry.

        ``registry`` should expose a ``list_all()`` method returning raw
        condition dicts, or a list of ConditionSchema objects.
        """
        results: dict[str, dict] = {}

        raw_conditions = (
            registry.list_all()
            if hasattr(registry, "list_all")
            else list(registry)
        )

        for raw in raw_conditions:
            try:
                if isinstance(raw, ConditionSchema):
                    condition = raw
                else:
                    condition = ConditionSchema(**raw)
                results[condition.slug] = self.check_condition(condition)
            except Exception as exc:
                slug = raw.get("slug", "<unknown>") if isinstance(raw, dict) else str(raw)
                logger.warning(
                    "Evidence coverage: could not check condition '%s' — %s",
                    slug,
                    exc,
                )

        return results
