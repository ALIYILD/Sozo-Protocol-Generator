"""
Evidence Grounding Validator — checks AI-generated content against evidence.

Validates that:
1. Clinical claims have supporting evidence
2. Referenced PMIDs actually exist in the research bundle
3. No unsupported efficacy/safety claims
4. Placeholder leakage from source template is detected
5. Off-label disclosures are present where required
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from ..template_profiles.models import DraftedSection, ResearchBundle

logger = logging.getLogger(__name__)

# Patterns that suggest unsupported clinical claims
_STRONG_CLAIM_PATTERNS = [
    r"(?:has been|is)\s+(?:proven|demonstrated|shown)\s+to\s+(?:cure|eliminate|reverse)",
    r"(?:definitively|conclusively)\s+(?:treats|cures)",
    r"100%\s+(?:effective|response|cure)\s+rate",
    r"guaranteed\s+(?:outcome|improvement|recovery)",
    r"FDA.approved\s+for",  # TPS is NOT FDA-approved for neuro conditions
    r"CE.marked\s+for\s+(?!Alzheimer)",  # TPS is only CE-marked for Alzheimer's
]

# Patterns for template/condition leakage
_LEAKAGE_PATTERNS = [
    r"\bParkinson(?:'s)?\b",
    r"\bPD\b(?!\s*=)",
    r"\[CONDITION\]",
    r"\[INSERT\]",
    r"\[TODO\]",
    r"\[PLACEHOLDER\]",
    r"\{condition\}",
    r"\{CONDITION\}",
]

# Required safety keywords per modality
_REQUIRED_SAFETY = {
    "tps": ["off-label", "informed consent", "NEUROLITH"],
    "tdcs": ["electrode", "impedance", "contraindication"],
}


@dataclass
class GroundingIssue:
    """A single grounding/validation issue."""

    section_id: str
    issue_type: str  # "unsupported_claim", "missing_citation", "placeholder_leakage", etc.
    severity: str  # "block", "warning", "info"
    message: str
    location: str = ""  # Line or context where issue was found


@dataclass
class GroundingResult:
    """Result of grounding validation for one section."""

    section_id: str
    grounding_score: float = 0.0  # 0-1
    issues: list[GroundingIssue] = field(default_factory=list)
    pmids_verified: int = 0
    pmids_unverified: int = 0
    claims_checked: int = 0
    claims_supported: int = 0

    @property
    def passed(self) -> bool:
        return not any(i.severity == "block" for i in self.issues)


class GroundingValidator:
    """Validates evidence grounding of generated sections.

    Usage:
        validator = GroundingValidator()
        result = validator.validate_section(drafted_section, research_bundle, target_condition)
    """

    def __init__(self, target_condition_slug: str = ""):
        self.target_slug = target_condition_slug

    def validate_section(
        self,
        section: DraftedSection,
        bundle: ResearchBundle,
        target_condition: str = "",
    ) -> GroundingResult:
        """Validate a single drafted section."""
        target = target_condition or self.target_slug
        result = GroundingResult(section_id=section.section_id)

        content = section.content or ""
        if not content:
            result.grounding_score = 0.0
            result.issues.append(GroundingIssue(
                section_id=section.section_id,
                issue_type="empty_section",
                severity="warning",
                message="Section has no content",
            ))
            return result

        # 1. Check for unsupported strong claims
        self._check_strong_claims(content, section.section_id, result)

        # 2. Verify PMID references
        self._verify_pmids(section, bundle, result)

        # 3. Check for template/condition leakage
        if target:
            self._check_leakage(content, section.section_id, target, result)

        # 4. Check placeholder leakage
        self._check_placeholder_leakage(content, section.section_id, result)

        # 5. Check citation density for evidence-heavy sections
        self._check_citation_density(section, result)

        # 6. Check safety requirements
        self._check_safety_requirements(content, section.section_id, result)

        # Compute grounding score
        total_checks = max(result.claims_checked, 1)
        result.grounding_score = result.claims_supported / total_checks
        if result.pmids_unverified > 0:
            result.grounding_score *= 0.8

        return result

    def validate_all(
        self,
        sections: list[DraftedSection],
        bundles: dict[str, ResearchBundle],
        target_condition: str = "",
    ) -> list[GroundingResult]:
        """Validate all sections."""
        results = []
        for section in sections:
            bundle = bundles.get(section.section_id, ResearchBundle(
                condition_slug=target_condition, section_id=section.section_id
            ))
            result = self.validate_section(section, bundle, target_condition)
            results.append(result)
        return results

    def _check_strong_claims(
        self, content: str, section_id: str, result: GroundingResult
    ):
        """Check for unsupported strong clinical claims."""
        for pattern in _STRONG_CLAIM_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                result.claims_checked += 1
                result.issues.append(GroundingIssue(
                    section_id=section_id,
                    issue_type="unsupported_claim",
                    severity="block",
                    message=f"Potentially unsupported claim: '{match.group()}'",
                    location=content[max(0, match.start() - 20):match.end() + 20],
                ))

    def _verify_pmids(
        self, section: DraftedSection, bundle: ResearchBundle, result: GroundingResult
    ):
        """Verify that referenced PMIDs exist in the research bundle."""
        bundle_pmids = {s.pmid for s in bundle.sources if s.pmid}

        for pmid in section.citations_used:
            result.claims_checked += 1
            if pmid in bundle_pmids:
                result.pmids_verified += 1
                result.claims_supported += 1
            else:
                result.pmids_unverified += 1
                result.issues.append(GroundingIssue(
                    section_id=section.section_id,
                    issue_type="unverified_pmid",
                    severity="warning",
                    message=f"PMID {pmid} not found in research bundle",
                ))

    def _check_leakage(
        self, content: str, section_id: str, target_condition: str, result: GroundingResult
    ):
        """Check for condition name leakage from source template."""
        # Skip if target IS parkinsons (no leakage possible from PD template)
        if target_condition == "parkinsons":
            return

        for pattern in _LEAKAGE_PATTERNS[:2]:  # Only check PD-specific patterns
            if re.search(pattern, content, re.IGNORECASE):
                result.issues.append(GroundingIssue(
                    section_id=section_id,
                    issue_type="condition_leakage",
                    severity="block",
                    message=f"Source condition name leaked into generated content (pattern: {pattern})",
                ))

    def _check_placeholder_leakage(
        self, content: str, section_id: str, result: GroundingResult
    ):
        """Check for unresolved placeholders."""
        for pattern in _LEAKAGE_PATTERNS[2:]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                result.issues.append(GroundingIssue(
                    section_id=section_id,
                    issue_type="placeholder_leakage",
                    severity="warning",
                    message=f"Unresolved placeholder: '{match}'",
                ))

    def _check_citation_density(self, section: DraftedSection, result: GroundingResult):
        """Check if evidence-heavy sections have enough citations."""
        # Evidence sections should have at least 1 citation per ~200 words
        word_count = len(section.content.split())
        if word_count > 200 and len(section.citations_used) == 0:
            result.issues.append(GroundingIssue(
                section_id=section.section_id,
                issue_type="low_citation_density",
                severity="warning",
                message=f"Section has {word_count} words but no citations",
            ))

    def _check_safety_requirements(
        self, content: str, section_id: str, result: GroundingResult
    ):
        """Check for required safety language."""
        content_lower = content.lower()
        section_lower = section_id.lower()

        for modality, keywords in _REQUIRED_SAFETY.items():
            if modality in section_lower:
                for kw in keywords:
                    if kw.lower() not in content_lower:
                        result.issues.append(GroundingIssue(
                            section_id=section_id,
                            issue_type="missing_safety_keyword",
                            severity="warning",
                            message=f"Missing required safety keyword for {modality}: '{kw}'",
                        ))
