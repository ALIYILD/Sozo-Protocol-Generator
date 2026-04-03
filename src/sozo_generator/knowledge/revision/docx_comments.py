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
    paragraph_index: int = -1
    extraction_confidence: float = 1.0

    # Section mapping (populated later)
    mapped_section: str = ""
    mapping_confidence: float = 0.0
    alternate_sections: list[str] = field(default_factory=list)

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

            # 2. Extract document text and comment anchors
            paragraphs, comment_ranges = _extract_document_structure(zf)

            # 3. Build extracted comments
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
                    ec.extraction_confidence = 0.9
                else:
                    ec.extraction_confidence = 0.5
                    result.extraction_warnings.append(
                        f"Comment '{cid}' has no anchor range in document"
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


def _extract_document_structure(zf: zipfile.ZipFile) -> tuple[list[str], dict]:
    """Extract paragraph text and comment range markers from document.xml."""
    paragraphs = []
    comment_ranges: dict[str, dict] = {}  # comment_id → {anchor_text, paragraph_index, ...}

    try:
        xml_bytes = zf.read("word/document.xml")
        root = ET.fromstring(xml_bytes)

        body = root.find(f"{_W}body")
        if body is None:
            return paragraphs, comment_ranges

        # Track active comment ranges
        active_ranges: dict[str, list[str]] = {}  # comment_id → text pieces
        active_range_starts: dict[str, int] = {}  # comment_id → start paragraph index

        for pi, p in enumerate(body.findall(f"{_W}p")):
            para_text_parts = []

            for child in p:
                tag = child.tag

                # Comment range start
                if tag == f"{_W}commentRangeStart":
                    cid = child.get(f"{_W}id", "")
                    if cid:
                        active_ranges[cid] = []
                        active_range_starts[cid] = pi

                # Comment range end
                elif tag == f"{_W}commentRangeEnd":
                    cid = child.get(f"{_W}id", "")
                    if cid and cid in active_ranges:
                        anchor = " ".join(active_ranges[cid]).strip()
                        start_pi = active_range_starts.get(cid, pi)

                        # Get surrounding context
                        before = paragraphs[start_pi - 1] if start_pi > 0 and paragraphs else ""
                        after_idx = pi + 1

                        comment_ranges[cid] = {
                            "anchor_text": anchor,
                            "paragraph_index": start_pi,
                            "before": before[:150],
                            "after": "",  # Will fill after processing
                        }
                        del active_ranges[cid]

                # Run text
                elif tag == f"{_W}r":
                    for t in child.findall(f"{_W}t"):
                        if t.text:
                            text = t.text
                            para_text_parts.append(text)
                            # Add to any active comment ranges
                            for cid in active_ranges:
                                active_ranges[cid].append(text)

            para_text = " ".join(para_text_parts).strip()
            paragraphs.append(para_text)

        # Fill "after" context
        for cid, info in comment_ranges.items():
            pi = info["paragraph_index"]
            if pi + 1 < len(paragraphs):
                info["after"] = paragraphs[pi + 1][:150]

    except Exception as e:
        logger.debug(f"Error parsing document.xml: {e}")

    return paragraphs, comment_ranges


# ── Section Mapping ──────────────────────────────────────────────────────


def map_comments_to_sections(
    result: DocxReviewIngestResult,
    provenance_path: str | Path | None = None,
) -> DocxReviewIngestResult:
    """Map extracted DOCX comments to canonical document sections.

    Uses multiple signals: anchor text, surrounding context, section headings,
    and provenance data.
    """
    # Load section titles from provenance if available
    section_titles = _load_section_titles(provenance_path)

    for comment in result.comments:
        # Try to map using anchor text and context
        best_section, confidence, alternatives = _find_best_section(
            comment, section_titles
        )
        comment.mapped_section = best_section
        comment.mapping_confidence = confidence
        comment.alternate_sections = alternatives

        if best_section:
            result.comments_mapped += 1
        elif alternatives:
            result.comments_ambiguous += 1
            result.mapping_warnings.append(
                f"Comment '{comment.text[:40]}...' has ambiguous mapping: {alternatives}"
            )
        else:
            result.comments_ambiguous += 1
            result.mapping_warnings.append(
                f"Comment '{comment.text[:40]}...' could not be mapped to any section"
            )

    return result


def _load_section_titles(provenance_path: str | Path | None) -> dict[str, str]:
    """Load section slug → title mapping from provenance."""
    if not provenance_path:
        return {}

    path = Path(provenance_path)
    if not path.exists():
        return {}

    try:
        import json
        data = json.loads(path.read_text())
        return {
            s["section_slug"]: s.get("section_slug", "")
            for s in data.get("sections", [])
        }
    except Exception:
        return {}


# Section keywords for fuzzy matching
_SECTION_KEYWORDS = {
    "document_control": ["document control", "governance", "clinical responsibility", "version"],
    "clinical_overview": ["overview", "clinical overview", "epidemiology", "prevalence"],
    "pathophysiology": ["pathophysiology", "mechanism", "neural", "circuit", "dopamine"],
    "brain_anatomy": ["brain", "anatomy", "neuroanatomy", "region", "structure"],
    "network_profiles": ["network", "fnon", "dmn", "cen", "salience", "connectivity"],
    "phenotypes": ["phenotype", "subtype", "classification"],
    "protocols_tdcs": ["tdcs", "direct current", "electrode", "montage", "anode", "cathode"],
    "protocols_tps": ["tps", "pulse stimulation", "neurolith", "ultrasound", "off-label"],
    "safety": ["safety", "contraindication", "adverse", "monitoring", "screening"],
    "assessments": ["assessment", "scale", "outcome", "measure", "phq", "updrs"],
    "responder_criteria": ["responder", "response", "non-responder", "improvement"],
    "evidence_summary": ["evidence", "gap", "quality", "literature"],
    "references": ["reference", "citation", "pmid", "bibliography"],
    "inclusion_exclusion": ["inclusion", "exclusion", "eligibility", "criteria"],
    "followup": ["follow-up", "follow up", "reassessment", "decision"],
}


def _find_best_section(
    comment: ExtractedDocxComment,
    section_titles: dict[str, str],
) -> tuple[str, float, list[str]]:
    """Find the best matching section for a comment."""
    # Combine all available text signals
    signals = " ".join(filter(None, [
        comment.anchor_text,
        comment.surrounding_before,
        comment.surrounding_after,
        comment.text,
    ])).lower()

    if not signals.strip():
        return "", 0.0, []

    # Score each section
    scores: dict[str, float] = {}
    for section_slug, keywords in _SECTION_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in signals)
        if score > 0:
            scores[section_slug] = score

    if not scores:
        return "", 0.0, []

    # Sort by score
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    best_slug = ranked[0][0]
    best_score = ranked[0][1]

    # Normalize confidence (max keyword matches ~ 3-4 for a good match)
    confidence = min(best_score / 3.0, 1.0)

    # Alternatives (next best)
    alternatives = [slug for slug, _ in ranked[1:4]]

    return best_slug, confidence, alternatives


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
