"""
DOCX Comment Extraction — extracts reviewer comments from Word documents.

Parses the OOXML package structure to extract comments, their anchor text,
and surrounding context. Maps them to canonical sections for the review pipeline.

Word comments live in:
- word/comments.xml — comment text, author, date, ID
- word/document.xml — commentRangeStart/End markers in paragraph runs

Usage:
    from sozo_generator.knowledge.revision.docx_comments import extract_docx_comments

    result = extract_docx_comments("reviewed_document.docx")
    for comment in result.comments:
        print(f"{comment.author}: {comment.text} → section: {comment.mapped_section}")
"""
from __future__ import annotations

import logging
import re
import uuid
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# OOXML namespaces
_NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
}
_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


# ── Models ────────────────────────────────────────────────────────────────


@dataclass
class MappingSignal:
    """One signal that contributed to a section mapping decision."""
    signal_type: str  # heading_match, keyword_match, text_overlap, position, comment_cue, alias
    section_slug: str
    score: float
    explanation: str = ""


@dataclass
class ExtractedDocxComment:
    """A single comment extracted from a DOCX file."""
    comment_id: str = ""
    docx_comment_id: str = ""  # Original Word comment ID
    source_docx: str = ""
    author: str = ""
    date: str = ""
    text: str = ""
    anchor_text: str = ""  # Text the comment is attached to
    surrounding_before: str = ""  # ~100 chars before anchor
    surrounding_after: str = ""  # ~100 chars after anchor
    full_paragraph_text: str = ""  # Full paragraph containing anchor
    preceding_heading: str = ""  # Nearest heading before this paragraph
    paragraph_index: int = -1
    inside_table: bool = False
    table_index: int = -1
    extraction_confidence: float = 1.0

    # Section mapping (populated by mapper)
    mapped_section: str = ""
    mapping_confidence: float = 0.0
    mapping_state: str = "unmapped"  # unmapped, high_confidence, medium_confidence, low_confidence, ambiguous
    alternate_sections: list[str] = field(default_factory=list)
    mapping_signals: list[MappingSignal] = field(default_factory=list)
    mapping_explanation: str = ""

    def __post_init__(self):
        if not self.comment_id:
            self.comment_id = f"dxc-{uuid.uuid4().hex[:8]}"


@dataclass
class DocxReviewIngestResult:
    """Result of extracting comments from a reviewed DOCX."""
    source_docx: str = ""
    document_id: str = ""
    comments: list[ExtractedDocxComment] = field(default_factory=list)
    comments_extracted: int = 0
    comments_mapped: int = 0
    comments_ambiguous: int = 0
    extraction_warnings: list[str] = field(default_factory=list)
    mapping_warnings: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        lines = [
            f"=== DOCX REVIEW INGEST ===",
            f"Source: {self.source_docx}",
            f"Comments extracted: {self.comments_extracted}",
            f"Comments mapped: {self.comments_mapped}",
            f"Ambiguous: {self.comments_ambiguous}",
        ]
        for c in self.comments:
            sec = f" → {c.mapped_section}" if c.mapped_section else " → (unmapped)"
            conf = f" (conf: {c.mapping_confidence:.0%})" if c.mapped_section else ""
            lines.append(f"  [{c.author}] {c.text[:60]}{sec}{conf}")
        if self.extraction_warnings:
            lines.append(f"\nWarnings: {'; '.join(self.extraction_warnings)}")
        return "\n".join(lines)


# ── DOCX Comment Extraction ──────────────────────────────────────────────


def extract_docx_comments(docx_path: str | Path) -> DocxReviewIngestResult:
    """Extract all reviewer comments from a DOCX file.

    Parses word/comments.xml for comment text/author/date,
    and word/document.xml for comment anchor locations.
    """
    path = Path(docx_path)
    result = DocxReviewIngestResult(source_docx=str(path))

    if not path.exists():
        result.extraction_warnings.append(f"File not found: {path}")
        return result

    try:
        with zipfile.ZipFile(str(path)) as zf:
            # 1. Extract comments from word/comments.xml
            comments_data = _extract_comments_xml(zf)

            # 2. Extract document text, comment anchors, and heading map
            paragraphs, comment_ranges, heading_map = _extract_document_structure(zf)

            # 3. Build extracted comments with richer context
            for cid, cdata in comments_data.items():
                ec = ExtractedDocxComment(
                    docx_comment_id=cid,
                    source_docx=str(path),
                    author=cdata.get("author", ""),
                    date=cdata.get("date", ""),
                    text=cdata.get("text", ""),
                )

                # Find anchor text from comment ranges
                if cid in comment_ranges:
                    anchor_info = comment_ranges[cid]
                    ec.anchor_text = anchor_info.get("anchor_text", "")
                    ec.paragraph_index = anchor_info.get("paragraph_index", -1)
                    ec.surrounding_before = anchor_info.get("before", "")
                    ec.surrounding_after = anchor_info.get("after", "")
                    ec.full_paragraph_text = anchor_info.get("full_paragraph", "")
                    ec.extraction_confidence = 0.9
                else:
                    ec.extraction_confidence = 0.5
                    result.extraction_warnings.append(
                        f"Comment '{cid}' has no anchor range in document"
                    )

                # Find preceding heading for this comment
                if ec.paragraph_index >= 0:
                    ec.preceding_heading = _find_preceding_heading(
                        ec.paragraph_index, heading_map, paragraphs
                    )

                result.comments.append(ec)

            result.comments_extracted = len(result.comments)

    except zipfile.BadZipFile:
        result.extraction_warnings.append("File is not a valid DOCX/ZIP")
    except Exception as e:
        result.extraction_warnings.append(f"Extraction error: {e}")

    return result


def _extract_comments_xml(zf: zipfile.ZipFile) -> dict[str, dict]:
    """Extract comments from word/comments.xml."""
    comments = {}

    if "word/comments.xml" not in zf.namelist():
        return comments

    try:
        xml_bytes = zf.read("word/comments.xml")
        root = ET.fromstring(xml_bytes)

        for comment_el in root.findall(f"{_W}comment"):
            cid = comment_el.get(f"{_W}id", "")
            author = comment_el.get(f"{_W}author", "")
            date = comment_el.get(f"{_W}date", "")

            # Extract comment text from paragraphs within the comment
            text_parts = []
            for p in comment_el.findall(f".//{_W}p"):
                for r in p.findall(f".//{_W}r"):
                    t = r.find(f"{_W}t")
                    if t is not None and t.text:
                        text_parts.append(t.text)

            comments[cid] = {
                "author": author,
                "date": date,
                "text": " ".join(text_parts).strip(),
            }

    except Exception as e:
        logger.debug(f"Error parsing comments.xml: {e}")

    return comments


def _extract_document_structure(zf: zipfile.ZipFile) -> tuple[list[str], dict, dict]:
    """Extract paragraph text, comment range markers, and heading map from document.xml.

    Returns:
        paragraphs: list of paragraph text strings
        comment_ranges: dict of comment_id → anchor info
        heading_map: dict of paragraph_index → heading text (for bold/large paragraphs)
    """
    paragraphs = []
    comment_ranges: dict[str, dict] = {}
    heading_map: dict[int, str] = {}  # paragraph_index → heading text

    try:
        xml_bytes = zf.read("word/document.xml")
        root = ET.fromstring(xml_bytes)

        body = root.find(f"{_W}body")
        if body is None:
            return paragraphs, comment_ranges, heading_map

        active_ranges: dict[str, list[str]] = {}
        active_range_starts: dict[str, int] = {}

        for pi, p in enumerate(body.findall(f"{_W}p")):
            para_text_parts = []
            is_heading = False

            # Check paragraph properties for heading style or bold formatting
            pPr = p.find(f"{_W}pPr")
            if pPr is not None:
                pStyle = pPr.find(f"{_W}pStyle")
                if pStyle is not None:
                    style_val = pStyle.get(f"{_W}val", "")
                    if "heading" in style_val.lower() or "title" in style_val.lower():
                        is_heading = True

            for child in p:
                tag = child.tag

                if tag == f"{_W}commentRangeStart":
                    cid = child.get(f"{_W}id", "")
                    if cid:
                        active_ranges[cid] = []
                        active_range_starts[cid] = pi

                elif tag == f"{_W}commentRangeEnd":
                    cid = child.get(f"{_W}id", "")
                    if cid and cid in active_ranges:
                        anchor = " ".join(active_ranges[cid]).strip()
                        start_pi = active_range_starts.get(cid, pi)
                        before = paragraphs[start_pi - 1] if start_pi > 0 and paragraphs else ""

                        comment_ranges[cid] = {
                            "anchor_text": anchor,
                            "paragraph_index": start_pi,
                            "before": before[:200],
                            "after": "",
                            "full_paragraph": "",  # Filled after para text built
                        }
                        del active_ranges[cid]

                elif tag == f"{_W}r":
                    # Check if run is bold (heading-like)
                    rPr = child.find(f"{_W}rPr")
                    if rPr is not None:
                        bold = rPr.find(f"{_W}b")
                        sz = rPr.find(f"{_W}sz")
                        if bold is not None or (sz is not None and int(sz.get(f"{_W}val", "22")) >= 26):
                            is_heading = True

                    for t in child.findall(f"{_W}t"):
                        if t.text:
                            para_text_parts.append(t.text)
                            for cid in active_ranges:
                                active_ranges[cid].append(t.text)

            para_text = " ".join(para_text_parts).strip()
            paragraphs.append(para_text)

            # Record headings (bold or styled)
            if is_heading and para_text and len(para_text) < 200:
                heading_map[pi] = para_text

            # Fill full_paragraph for any comment ranges ending at this paragraph
            for cid, info in comment_ranges.items():
                if info.get("paragraph_index") == pi and not info.get("full_paragraph"):
                    info["full_paragraph"] = para_text

        # Fill "after" context
        for cid, info in comment_ranges.items():
            pi = info["paragraph_index"]
            if pi + 1 < len(paragraphs):
                info["after"] = paragraphs[pi + 1][:200]

    except Exception as e:
        logger.debug(f"Error parsing document.xml: {e}")

    return paragraphs, comment_ranges, heading_map


# ── Heading finder ────────────────────────────────────────────────────────


def _find_preceding_heading(
    para_index: int,
    heading_map: dict[int, str],
    paragraphs: list[str],
) -> str:
    """Find the nearest heading before a given paragraph index."""
    # Check heading_map for explicit headings
    for hi in sorted(heading_map.keys(), reverse=True):
        if hi <= para_index:
            return heading_map[hi]

    # Fallback: scan backwards for short bold-looking paragraphs
    for i in range(para_index - 1, max(para_index - 10, -1), -1):
        if i >= 0 and i < len(paragraphs):
            text = paragraphs[i]
            if text and len(text) < 80 and text == text.strip():
                # Likely a heading-like paragraph
                return text
    return ""


# ── Section Mapping (Multi-Signal) ───────────────────────────────────────


# Expanded section aliases for better matching
_SECTION_ALIASES: dict[str, list[str]] = {
    "document_control": [
        "document control", "clinical responsibility", "governance", "version",
        "organization", "sozo brain center", "confidential",
    ],
    "clinical_overview": [
        "overview", "clinical overview", "epidemiology", "prevalence",
        "disease burden", "disorder characterized", "treatment landscape",
    ],
    "pathophysiology": [
        "pathophysiology", "mechanism", "neural circuit", "dopamine",
        "serotonin", "braak", "neurodegeneration", "alpha-synuclein",
        "neuroinflammation", "hpa axis", "circuit dysfunction",
    ],
    "brain_anatomy": [
        "brain", "anatomy", "neuroanatomy", "region", "structure",
        "substantia nigra", "basal ganglia", "prefrontal", "cortex",
        "brain map", "brodmann",
    ],
    "network_profiles": [
        "network", "fnon", "dmn", "default mode", "cen", "executive",
        "salience", "sensorimotor", "limbic", "attention", "connectivity",
        "dysfunction", "hypoactivation", "hyperactivation",
    ],
    "phenotypes": [
        "phenotype", "subtype", "classification", "tremor-dominant",
        "akinetic", "melancholic", "atypical", "treatment-resistant",
    ],
    "protocols_tdcs": [
        "tdcs", "direct current", "electrode", "montage", "anode", "cathode",
        "hdckit", "platoscience", "newronika", "2 ma",
    ],
    "protocols_tps": [
        "tps", "pulse stimulation", "neurolith", "ultrasound",
        "off-label", "tps target", "focused ultrasound", "mj/mm",
    ],
    "safety": [
        "safety", "contraindication", "adverse", "monitoring", "screening",
        "seizure", "pregnancy", "metal implant", "pacemaker", "stopping rule",
    ],
    "assessments": [
        "assessment", "scale", "outcome measure", "phq", "updrs", "moca",
        "ham-d", "madrs", "gad-7", "screening", "validated",
    ],
    "responder_criteria": [
        "responder", "response", "non-responder", "improvement",
        "partial responder", "week 4", "week 8", "30%", "15%",
    ],
    "evidence_summary": [
        "evidence summary", "evidence gap", "quality", "literature",
        "emerging evidence", "systematic review",
    ],
    "references": [
        "reference", "citation", "pmid", "bibliography", "doi",
    ],
    "inclusion_exclusion": [
        "inclusion", "exclusion", "eligibility", "criteria",
    ],
    "followup": [
        "follow-up", "follow up", "reassessment", "decision",
        "maintenance", "discharge",
    ],
}

# Signal weights for multi-signal scoring
_SIGNAL_WEIGHTS = {
    "heading_match": 4.0,    # Preceding heading matches section title
    "keyword_match": 1.0,    # Keyword/alias found in combined text
    "comment_cue": 2.0,      # Comment text contains strong section cue
    "heading_alias": 3.0,    # Heading text matches section alias
    "anchor_overlap": 2.5,   # Anchor text overlaps with section-specific terms
}


def map_comments_to_sections(
    result: DocxReviewIngestResult,
    provenance_path: str | Path | None = None,
    blueprint_slug: str = "",
) -> DocxReviewIngestResult:
    """Map extracted DOCX comments to canonical document sections.

    Uses multi-signal scoring:
    1. Heading match (preceding heading → section title)
    2. Keyword/alias matching (expanded vocabulary)
    3. Comment text cues (strong section-specific terms)
    4. Anchor text overlap
    5. Provenance section ordering
    """
    provenance_sections = _load_provenance_sections(provenance_path)
    blueprint_sections = _load_blueprint_sections(blueprint_slug)

    for comment in result.comments:
        signals, ranked = _score_all_sections(comment, provenance_sections, blueprint_sections)
        comment.mapping_signals = signals

        if ranked:
            best_slug, best_score = ranked[0]
            comment.mapped_section = best_slug
            comment.mapping_confidence = _calibrate_confidence(best_score, ranked)
            comment.alternate_sections = [slug for slug, _ in ranked[1:4]]

            # Determine mapping state
            if comment.mapping_confidence >= 0.7:
                comment.mapping_state = "high_confidence"
            elif comment.mapping_confidence >= 0.4:
                comment.mapping_state = "medium_confidence"
            elif comment.mapping_confidence >= 0.2:
                comment.mapping_state = "low_confidence"
            else:
                comment.mapping_state = "ambiguous"

            # Build explanation
            top_signals = sorted(signals, key=lambda s: -s.score)[:3]
            explanations = [s.explanation for s in top_signals if s.explanation and s.section_slug == best_slug]
            comment.mapping_explanation = "; ".join(explanations) if explanations else f"Best match: {best_slug}"

            result.comments_mapped += 1
        else:
            comment.mapping_state = "unmapped"
            result.comments_ambiguous += 1
            result.mapping_warnings.append(
                f"Comment '{comment.text[:40]}...' could not be mapped"
            )

    return result


def _load_provenance_sections(path: str | Path | None) -> list[dict]:
    """Load section metadata from provenance sidecar."""
    if not path:
        return []
    p = Path(path)
    if not p.exists():
        return []
    try:
        import json
        data = json.loads(p.read_text())
        return data.get("sections", [])
    except Exception:
        return []


def _load_blueprint_sections(blueprint_slug: str) -> list[dict]:
    """Load section definitions from a blueprint."""
    if not blueprint_slug:
        return []
    try:
        from ..loader import load_blueprint
        bp = load_blueprint(blueprint_slug)
        if bp:
            return [{"slug": s.slug, "title": s.title, "order": s.order} for s in bp.sections]
    except Exception:
        pass
    return []


def _score_all_sections(
    comment: ExtractedDocxComment,
    provenance_sections: list[dict],
    blueprint_sections: list[dict],
) -> tuple[list[MappingSignal], list[tuple[str, float]]]:
    """Score all candidate sections using multiple signals."""
    scores: dict[str, float] = {}
    all_signals: list[MappingSignal] = []

    # Build combined text from all available context
    combined_lower = " ".join(filter(None, [
        comment.text,
        comment.anchor_text,
        comment.surrounding_before,
        comment.surrounding_after,
        comment.full_paragraph_text,
    ])).lower()

    heading_lower = (comment.preceding_heading or "").lower()

    for section_slug, aliases in _SECTION_ALIASES.items():
        section_score = 0.0

        # Signal 1: Preceding heading matches section
        if heading_lower:
            # Check if heading contains the section slug or aliases
            heading_matches = sum(1 for a in aliases if a in heading_lower)
            if heading_matches > 0:
                w = _SIGNAL_WEIGHTS["heading_match"] * heading_matches
                section_score += w
                signal = MappingSignal(
                    signal_type="heading_match",
                    section_slug=section_slug,
                    score=w,
                    explanation=f"Preceding heading '{comment.preceding_heading[:50]}' matches section '{section_slug}'",
                )
                all_signals.append(signal)

            # Also check if heading text is an alias directly
            for a in aliases:
                if heading_lower.startswith(a) or a.startswith(heading_lower[:10]):
                    w = _SIGNAL_WEIGHTS["heading_alias"]
                    section_score += w
                    all_signals.append(MappingSignal(
                        signal_type="heading_alias", section_slug=section_slug, score=w,
                        explanation=f"Heading '{heading_lower[:30]}' is alias for '{section_slug}'",
                    ))
                    break

        # Signal 2: Keyword/alias in combined text
        keyword_hits = sum(1 for a in aliases if a in combined_lower)
        if keyword_hits > 0:
            w = _SIGNAL_WEIGHTS["keyword_match"] * keyword_hits
            section_score += w
            all_signals.append(MappingSignal(
                signal_type="keyword_match", section_slug=section_slug, score=w,
                explanation=f"{keyword_hits} keyword(s) matched for '{section_slug}'",
            ))

        # Signal 3: Comment text contains strong section cue
        comment_lower = comment.text.lower()
        comment_cue_hits = sum(1 for a in aliases if a in comment_lower)
        if comment_cue_hits > 0:
            w = _SIGNAL_WEIGHTS["comment_cue"] * comment_cue_hits
            section_score += w
            all_signals.append(MappingSignal(
                signal_type="comment_cue", section_slug=section_slug, score=w,
                explanation=f"Comment text directly references '{section_slug}' concepts",
            ))

        # Signal 4: Anchor text has strong overlap
        if comment.anchor_text:
            anchor_lower = comment.anchor_text.lower()
            anchor_hits = sum(1 for a in aliases if a in anchor_lower)
            if anchor_hits > 0:
                w = _SIGNAL_WEIGHTS["anchor_overlap"] * anchor_hits
                section_score += w
                all_signals.append(MappingSignal(
                    signal_type="anchor_overlap", section_slug=section_slug, score=w,
                    explanation=f"Anchor text overlaps with '{section_slug}' terminology",
                ))

        if section_score > 0:
            scores[section_slug] = section_score

    # Rank by total score
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    return all_signals, ranked


def _calibrate_confidence(best_score: float, ranked: list[tuple[str, float]]) -> float:
    """Calibrate mapping confidence based on absolute score and margin over second-best."""
    if not ranked:
        return 0.0

    # Absolute confidence from score (strong match = high score)
    abs_conf = min(best_score / 8.0, 1.0)  # 8 points = max confidence

    # Margin over second-best (separation = more confidence)
    if len(ranked) >= 2:
        margin = (ranked[0][1] - ranked[1][1]) / max(ranked[0][1], 0.1)
        margin_bonus = margin * 0.3  # Up to 30% bonus for clear separation
    else:
        margin_bonus = 0.2  # Only one candidate = moderate bonus

    confidence = min(abs_conf + margin_bonus, 1.0)
    return round(confidence, 2)


# ── Integration Helper ────────────────────────────────────────────────────


def docx_comments_to_review_set(
    ingest_result: DocxReviewIngestResult,
    condition_slug: str = "",
    blueprint_slug: str = "",
    tier: str = "",
) -> "ReviewCommentSet":
    """Convert extracted DOCX comments into a ReviewCommentSet for the review pipeline."""
    from .models import ReviewCommentSet, CommentSeverity

    comment_set = ReviewCommentSet(
        document_id=ingest_result.document_id or ingest_result.source_docx,
        condition_slug=condition_slug,
        blueprint_slug=blueprint_slug,
        tier=tier,
        reviewer_name=ingest_result.comments[0].author if ingest_result.comments else "",
    )

    for ec in ingest_result.comments:
        comment_set.add(
            raw_text=ec.text,
            section=ec.mapped_section,
            severity="major" if ec.mapping_confidence > 0.5 else "suggestion",
        )

    return comment_set
