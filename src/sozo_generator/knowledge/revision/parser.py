"""
Review Comment Parser — classifies comments and maps to canonical targets.

Uses pattern matching and the existing CommentNormalizer to convert
free-text reviewer comments into structured ChangeRequests.
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Optional

from .models import (
    ChangeRequest,
    ChangeTarget,
    ChangeStatus,
    CommentCategory,
    CommentSeverity,
    ReviewComment,
    ReviewCommentSet,
)

logger = logging.getLogger(__name__)

# ── Category detection patterns ────────────────────────────────────────────

_CATEGORY_PATTERNS: list[tuple[CommentCategory, list[str]]] = [
    (CommentCategory.EVIDENCE_STRENGTH, [
        r"evidence", r"citation", r"pmid", r"reference", r"source",
        r"support.*claim", r"literature", r"study", r"trial",
    ]),
    (CommentCategory.CONTRAINDICATION, [
        r"contraindication", r"safety", r"adverse", r"risk",
        r"stopping rule", r"screening",
    ]),
    (CommentCategory.PROTOCOL_PARAMETER, [
        r"protocol", r"parameter", r"intensity", r"duration",
        r"frequency", r"dose", r"session", r"montage",
    ]),
    (CommentCategory.MODALITY_SPECIFICITY, [
        r"\btps\b", r"\btdcs\b", r"\btavns\b", r"\bces\b",
        r"neurolith", r"modality", r"stimulation",
    ]),
    (CommentCategory.AUDIENCE_TONE, [
        r"fellow", r"partner", r"too.*technical", r"simplif",
        r"audience", r"tone", r"accessible", r"advanced",
    ]),
    (CommentCategory.VISUAL_CHANGE, [
        r"visual", r"figure", r"image", r"diagram", r"map",
        r"move.*figure", r"add.*visual",
    ]),
    (CommentCategory.TABLE_CHANGE, [
        r"table", r"column", r"row", r"header", r"grid",
    ]),
    (CommentCategory.MISSING_CONTENT, [
        r"missing", r"add.*section", r"include", r"needs.*more",
        r"expand", r"elaborate", r"insufficient",
    ]),
    (CommentCategory.GOVERNANCE, [
        r"governance", r"consent", r"off.label", r"disclosure",
        r"regulatory",
    ]),
    (CommentCategory.STYLE, [
        r"style", r"wording", r"phrasing", r"rephrase",
        r"rewrite", r"clearer", r"vague",
    ]),
    (CommentCategory.FORMATTING, [
        r"format", r"spacing", r"heading", r"indent",
        r"numbering", r"layout",
    ]),
]

# ── Section slug mapping ──────────────────────────────────────────────────

_SECTION_KEYWORDS: dict[str, list[str]] = {
    "clinical_overview": ["overview", "introduction", "clinical overview"],
    "pathophysiology": ["pathophysiology", "mechanism", "neural"],
    "brain_anatomy": ["anatomy", "brain region", "neuroanatomy", "brain structure"],
    "network_profiles": ["network", "fnon", "connectivity", "dmn", "cen", "salience"],
    "phenotypes": ["phenotype", "subtype", "classification"],
    "protocols_tdcs": ["tdcs", "direct current", "electrode", "montage"],
    "protocols_tps": ["tps", "pulse stimulation", "neurolith", "ultrasound"],
    "safety": ["safety", "contraindication", "adverse", "monitoring"],
    "assessments": ["assessment", "scale", "outcome measure", "screening"],
    "responder_criteria": ["responder", "response", "non-responder", "tracking"],
    "evidence_summary": ["evidence", "gap", "quality"],
    "references": ["reference", "citation", "bibliography"],
    "inclusion_exclusion": ["inclusion", "exclusion", "eligibility"],
    "document_control": ["governance", "version", "document control"],
}

# ── Evidence-sensitive patterns ───────────────────────────────────────────

_EVIDENCE_SENSITIVE_PATTERNS = [
    r"evidence", r"pmid", r"citation", r"clinical claim",
    r"protocol.*param", r"contraindication", r"dose",
    r"intensity", r"frequency", r"efficacy", r"outcome",
]


def classify_comment(comment: ReviewComment) -> ReviewComment:
    """Classify a single review comment: detect category, severity, and section."""
    text_lower = comment.raw_text.lower()

    # Detect category
    best_category = CommentCategory.GENERAL
    best_score = 0
    for category, patterns in _CATEGORY_PATTERNS:
        score = sum(1 for p in patterns if re.search(p, text_lower))
        if score > best_score:
            best_score = score
            best_category = category
    comment.category = best_category

    # Detect target section (if not already specified)
    if not comment.target_section_slug:
        comment.target_section_slug = _detect_section(text_lower)

    # Detect severity
    if any(kw in text_lower for kw in ["critical", "incorrect", "wrong", "dangerous", "must"]):
        comment.severity = CommentSeverity.CRITICAL
    elif any(kw in text_lower for kw in ["should", "needs", "important", "weak", "missing"]):
        comment.severity = CommentSeverity.MAJOR
    elif any(kw in text_lower for kw in ["could", "consider", "suggest", "minor"]):
        comment.severity = CommentSeverity.MINOR
    else:
        comment.severity = CommentSeverity.SUGGESTION

    # Confidence
    comment.confidence = min(best_score / 3.0, 1.0)  # Normalize to 0-1
    comment.parsed = True

    return comment


def classify_all(comment_set: ReviewCommentSet) -> ReviewCommentSet:
    """Classify all comments in a set."""
    for comment in comment_set.comments:
        classify_comment(comment)
    return comment_set


def comments_to_change_requests(
    comment_set: ReviewCommentSet,
) -> list[ChangeRequest]:
    """Convert classified comments into structured change requests."""
    requests = []

    for comment in comment_set.comments:
        if not comment.parsed:
            classify_comment(comment)

        cr = ChangeRequest(
            source_comment_ids=[comment.comment_id],
            document_id=comment_set.document_id,
            condition_slug=comment_set.condition_slug,
            doc_type=comment_set.blueprint_slug,
            tier=comment_set.tier,
            target_section=comment.target_section_slug,
            original_comment=comment.raw_text,
            confidence=comment.confidence,
        )

        # Determine target type and action
        cr.target_type, cr.requested_action, cr.rationale = _determine_target(comment)

        # Safety checks
        text_lower = comment.raw_text.lower()
        cr.evidence_sensitive = any(
            re.search(p, text_lower) for p in _EVIDENCE_SENSITIVE_PATTERNS
        )
        cr.requires_manual_approval = (
            cr.evidence_sensitive
            or comment.severity == CommentSeverity.CRITICAL
            or cr.target_type in (ChangeTarget.KNOWLEDGE_PATCH, ChangeTarget.SHARED_RULE_PATCH)
        )

        # Block overly broad requests
        if any(kw in text_lower for kw in ["rewrite everything", "redo the whole", "start over"]):
            cr.target_type = ChangeTarget.BLOCKED
            cr.status = ChangeStatus.BLOCKED
            cr.rationale = "Broad rewrite requests must be decomposed into specific section changes"

        # Proposed resolution
        cr.proposed_resolution = _suggest_resolution(comment, cr)

        requests.append(cr)

    return requests


def _detect_section(text_lower: str) -> str:
    """Detect which section a comment refers to."""
    best_section = ""
    best_score = 0
    for section_slug, keywords in _SECTION_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > best_score:
            best_score = score
            best_section = section_slug
    return best_section


def _determine_target(comment: ReviewComment) -> tuple[ChangeTarget, str, str]:
    """Determine the target type and action for a change request."""
    cat = comment.category

    if cat == CommentCategory.VISUAL_CHANGE:
        return ChangeTarget.BLUEPRINT_PATCH, "update_visual", "Visual placement or type change"
    elif cat == CommentCategory.TABLE_CHANGE:
        return ChangeTarget.BLUEPRINT_PATCH, "update_table", "Table schema change"
    elif cat == CommentCategory.FORMATTING:
        return ChangeTarget.RENDERING_PATCH, "update_formatting", "Formatting or layout change"
    elif cat in (CommentCategory.AUDIENCE_TONE, CommentCategory.STYLE):
        return ChangeTarget.SECTION_OVERRIDE, "update_wording", "Wording or tone adjustment"
    elif cat == CommentCategory.GOVERNANCE:
        return ChangeTarget.SHARED_RULE_PATCH, "update_rule", "Governance or consent rule change"
    elif cat == CommentCategory.CONTRAINDICATION:
        return ChangeTarget.KNOWLEDGE_PATCH, "update_safety", "Safety or contraindication update"
    elif cat == CommentCategory.EVIDENCE_STRENGTH:
        return ChangeTarget.SECTION_OVERRIDE, "strengthen_evidence", "Evidence strengthening"
    elif cat == CommentCategory.PROTOCOL_PARAMETER:
        return ChangeTarget.KNOWLEDGE_PATCH, "update_protocol", "Protocol parameter update"
    elif cat == CommentCategory.MISSING_CONTENT:
        return ChangeTarget.SECTION_OVERRIDE, "add_content", "Add missing content"
    elif cat == CommentCategory.MODALITY_SPECIFICITY:
        return ChangeTarget.SECTION_OVERRIDE, "add_modality_detail", "Modality-specific content"
    else:
        return ChangeTarget.SECTION_OVERRIDE, "general_update", "General content update"


def _suggest_resolution(comment: ReviewComment, cr: ChangeRequest) -> str:
    """Suggest a resolution for the change request."""
    if cr.target_type == ChangeTarget.BLOCKED:
        return "Decompose into specific section-level change requests"
    if cr.evidence_sensitive:
        return f"Review evidence for section '{cr.target_section}' — may need additional PMIDs"
    if comment.category == CommentCategory.AUDIENCE_TONE:
        return f"Adjust tone/complexity in section '{cr.target_section}' for tier appropriateness"
    if comment.category == CommentCategory.VISUAL_CHANGE:
        return f"Update visual placement or type in blueprint for section '{cr.target_section}'"
    return f"Apply {cr.requested_action} to section '{cr.target_section}'"


# ── Comment ingestion helpers ─────────────────────────────────────────────


def ingest_from_json(path: str | Path) -> ReviewCommentSet:
    """Load review comments from a JSON file."""
    data = json.loads(Path(path).read_text())
    return ReviewCommentSet(**data)


def ingest_from_text(
    text: str,
    document_id: str,
    condition_slug: str = "",
    blueprint_slug: str = "",
    tier: str = "",
    reviewer_name: str = "",
) -> ReviewCommentSet:
    """Parse review comments from plain text (one per line)."""
    comment_set = ReviewCommentSet(
        document_id=document_id,
        condition_slug=condition_slug,
        blueprint_slug=blueprint_slug,
        tier=tier,
        reviewer_name=reviewer_name,
    )

    for line in text.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Check for section prefix: "[section_slug] comment text"
        match = re.match(r"\[([a-z_]+)\]\s*(.*)", line)
        if match:
            comment_set.add(match.group(2), section=match.group(1))
        else:
            comment_set.add(line)

    return comment_set
