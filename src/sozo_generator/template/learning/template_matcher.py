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
        best_type = ""
        best_score = 0.0

        for doc_type, keywords in _DOC_TYPE_KEYWORDS.items():
            score = 0
            for kw in keywords:
                if kw in all_text or kw in filename:
                    score += 1
            # Normalize
            norm_score = score / len(keywords) if keywords else 0
            if norm_score > best_score:
                best_score = norm_score
                best_type = doc_type

        result.matched_doc_type = best_type
        result.confidence = min(best_score * 1.3, 1.0)  # slight boost

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
        if best_type:
            pattern_kws = _DOC_TYPE_KEYWORDS[best_type]
            matched = sum(1 for s in sections
                         if any(kw in s.section_id for kw in pattern_kws))
            result.section_match_count = matched

        # Warnings
        if result.confidence < 0.3:
            result.warnings.append("Low confidence template match — manual doc type selection recommended")
        if result.total_sections < 3:
            result.warnings.append("Very few sections detected — template may need Word Heading styles")

        return result
