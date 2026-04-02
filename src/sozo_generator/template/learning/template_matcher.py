"""Template matcher — scores uploaded templates against known SOZO document patterns."""
from __future__ import annotations
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from ..parser import TemplateParser, ParsedSection

logger = logging.getLogger(__name__)

@dataclass
class TemplateMatchCandidate:
    """A scored candidate doc type match."""
    doc_type: str = ""
    score: float = 0.0
    matched_keywords: list[str] = field(default_factory=list)


@dataclass
class TemplateMatchResult:
    """Result of matching an uploaded template against known patterns."""
    matched_doc_type: str = ""
    matched_tier: str = ""
    confidence: float = 0.0
    section_match_count: int = 0
    total_sections: int = 0
    table_match: bool = False
    condition_detected: str = ""
    warnings: list[str] = field(default_factory=list)
    section_ids: list[str] = field(default_factory=list)
    # Fallback candidates when confidence is weak
    candidates: list[TemplateMatchCandidate] = field(default_factory=list)

# Known section patterns per doc type (from gold_standard.py)
_DOC_TYPE_KEYWORDS = {
    "evidence_based_protocol": ["inclusion", "exclusion", "pathophysiology", "protocol", "evidence", "monitoring", "safety"],
    "handbook": ["stage_1", "stage_2", "stage_3", "governance", "modalities", "introduction"],
    "clinical_exam": ["examination", "screening", "phenotype", "scoring", "assessment"],
    "phenotype_classification": ["phenotype", "classification", "step1", "step2"],
    "responder_tracking": ["responder", "response", "classification", "tracking"],
    "psych_intake": ["intake", "prs", "clinical_interview", "psychiatric"],
    "network_assessment": ["network", "dmn", "cen", "smn", "limbic", "attention", "6_network"],
    "all_in_one_protocol": ["all_in_one", "combination", "sequencing", "tdcs_protocol", "tps_protocol"],
}

_TIER_KEYWORDS = {
    "fellow": ["fellow", "supervised", "doctor supervision"],
    "partners": ["partners", "fnon", "full framework", "6-network"],
}

class TemplateMatcher:
    """Matches uploaded templates against known SOZO document patterns."""

    def match(self, template_path: Path) -> TemplateMatchResult:
        """Score a template against all known doc type patterns."""
        parser = TemplateParser(template_path)
        sections = parser.parse()

        result = TemplateMatchResult(
            total_sections=len(sections),
            section_ids=[s.section_id for s in sections],
        )

        if not sections:
            result.warnings.append("No sections could be parsed from template")
            return result

        # Collect all text for matching
        all_text = " ".join(s.section_id + " " + s.title.lower() + " " + s.raw_content.lower()[:200]
                           for s in sections)
        filename = template_path.stem.lower()

        # Score against each doc type
        all_candidates: list[TemplateMatchCandidate] = []

        for doc_type, keywords in _DOC_TYPE_KEYWORDS.items():
            matched_kws = [kw for kw in keywords if kw in all_text or kw in filename]
            norm_score = len(matched_kws) / len(keywords) if keywords else 0
            all_candidates.append(TemplateMatchCandidate(
                doc_type=doc_type,
                score=norm_score,
                matched_keywords=matched_kws,
            ))

        all_candidates.sort(key=lambda c: c.score, reverse=True)
        best = all_candidates[0] if all_candidates else None

        if best and best.score > 0:
            result.matched_doc_type = best.doc_type
            result.confidence = min(best.score * 1.3, 1.0)
        else:
            result.matched_doc_type = "evidence_based_protocol"  # safe default
            result.confidence = 0.1

        # Store top 3 candidates for reviewer visibility
        result.candidates = [c for c in all_candidates if c.score > 0][:3]

        # Detect tier
        for tier, keywords in _TIER_KEYWORDS.items():
            if any(kw in all_text or kw in filename for kw in keywords):
                result.matched_tier = tier
                break
        if not result.matched_tier:
            result.matched_tier = "both"

        # Detect condition from content
        from ...ai.intent_parser import CONDITION_ALIASES
        for alias, slug in sorted(CONDITION_ALIASES.items(), key=lambda x: len(x[0]), reverse=True):
            if alias in all_text:
                result.condition_detected = slug
                break

        # Count section matches
        if result.matched_doc_type:
            pattern_kws = _DOC_TYPE_KEYWORDS[result.matched_doc_type]
            matched = sum(1 for s in sections
                         if any(kw in s.section_id for kw in pattern_kws))
            result.section_match_count = matched

        # Warnings
        if result.confidence < 0.3:
            cand_str = ", ".join(f"{c.doc_type} ({c.score:.0%})" for c in result.candidates[:3])
            result.warnings.append(
                f"Low confidence template match ({result.confidence:.0%}). "
                f"Best candidates: {cand_str or 'none'}. "
                f"Manual doc type selection recommended."
            )
        elif result.confidence < 0.6:
            result.warnings.append(
                f"Moderate confidence ({result.confidence:.0%}) for '{result.matched_doc_type}'. "
                f"Verify this is the intended document type."
            )
        if result.total_sections < 3:
            result.warnings.append("Very few sections detected — template may need Word Heading styles")

        return result
