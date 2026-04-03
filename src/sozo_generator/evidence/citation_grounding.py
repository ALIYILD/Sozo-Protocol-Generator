"""
Claim-level citation grounding — traces each protocol claim to specific
evidence with supporting quotes, citation types, and evidence grades.

At protocol generation time, this service:
1. Identifies claims in generated section text
2. Retrieves relevant evidence from the study repository
3. Matches claims to supporting/contradicting evidence
4. Attaches structured citations with provenance
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Optional

from pydantic import BaseModel, Field

from ..core.enums import ClaimCategory, ConfidenceLabel, EvidenceRelation
from ..schemas.evidence import ArticleMetadata
from ..schemas.contracts import EvidenceItem
from .parameter_extractor import StimulationParameters
from .evidence_scorer import EvidenceScore

logger = logging.getLogger(__name__)


# ── Citation models ────────────────────────────────────────────────────


class GroundedCitation(BaseModel):
    """A single citation grounding a specific claim."""

    study_identifier: str = ""  # PMID or DOI
    title: str = ""
    authors_short: str = ""
    year: Optional[int] = None
    journal: Optional[str] = None

    citation_type: str = "supports"  # supports, informs, contradicts, safety_note
    claim_text: str = ""  # the specific claim being cited
    supporting_quote: str = ""  # relevant text from the abstract
    relevance_note: str = ""  # why this citation was chosen

    evidence_grade: str = "D"  # A/B/C/D
    quality_score: int = 0
    relevance_score: int = 0

    formatted_inline: str = ""  # e.g. "(Brunoni et al., 2017; PMID: 28493655)"
    formatted_reference: str = ""  # full bibliography entry


class GroundedSection(BaseModel):
    """A protocol section with grounded citations."""

    section_id: str = ""
    section_title: str = ""
    claims: list[GroundedClaim] = Field(default_factory=list)
    total_citations: int = 0
    evidence_grades: dict[str, int] = Field(default_factory=dict)  # A:3, B:2, etc.
    has_contradictions: bool = False
    needs_review: bool = False
    review_reasons: list[str] = Field(default_factory=list)


class GroundedClaim(BaseModel):
    """A single claim extracted from section text with its citations."""

    claim_id: str = ""
    claim_text: str = ""
    category: str = ""  # ClaimCategory value
    citations: list[GroundedCitation] = Field(default_factory=list)
    confidence: str = ""  # ConfidenceLabel value
    has_contradicting_evidence: bool = False
    unsupported: bool = False


# ── Claim extraction patterns ──────────────────────────────────────────

# Patterns that indicate protocol-relevant claims
_CLAIM_PATTERNS = [
    # Stimulation parameters
    re.compile(
        r"(?:apply|deliver|administer|use)\s+.{5,80}(?:mA|Hz|minutes?|sessions?|pulses?)",
        re.I,
    ),
    # Electrode placement
    re.compile(
        r"(?:anode|cathode|electrode|coil)\s+.{3,60}(?:over|at|on)\s+.{3,30}",
        re.I,
    ),
    # Target statements
    re.compile(
        r"(?:target(?:ing)?|stimulat(?:e|ing))\s+(?:the\s+)?(?:left|right|bilateral)?\s*"
        r"(?:DLPFC|M1|SMA|DMPFC|cerebellum|motor cortex|prefrontal)",
        re.I,
    ),
    # Dosing schedule
    re.compile(
        r"\d+\s+sessions?\s+.{3,40}(?:per\s+week|daily|over\s+\d+\s+weeks?)",
        re.I,
    ),
    # Safety statements
    re.compile(
        r"(?:contraindicated|safety|adverse|side\s+effect|precaution)",
        re.I,
    ),
    # Efficacy claims
    re.compile(
        r"(?:effective|efficacy|improvement|reduction|significant|beneficial|therapeutic)",
        re.I,
    ),
    # Assessment tool references
    re.compile(
        r"(?:measured|assessed|evaluated)\s+(?:using|with|by)\s+(?:the\s+)?"
        r"(?:HDRS|HAM-D|MADRS|BDI|VAS|UPDRS|MoCA|MMSE|CGI|PANSS|PHQ)",
        re.I,
    ),
]


class CitationGroundingService:
    """Grounds protocol section claims to evidence."""

    def __init__(self, max_citations_per_claim: int = 5):
        self.max_citations = max_citations_per_claim

    def ground_section(
        self,
        section_id: str,
        section_title: str,
        section_text: str,
        evidence_pool: list[tuple[ArticleMetadata, Optional[StimulationParameters], Optional[EvidenceScore]]],
        category: Optional[ClaimCategory] = None,
    ) -> GroundedSection:
        """Ground all claims in a section to available evidence.

        Args:
            section_id: Section identifier
            section_title: Section title
            section_text: The generated section text
            evidence_pool: List of (article, extraction, score) tuples
            category: Claim category for this section
        """
        grounded = GroundedSection(
            section_id=section_id,
            section_title=section_title,
        )

        # Extract claims from section text
        claims = self._extract_claims(section_text, section_id, category)

        if not claims:
            # Treat entire section as one claim
            claims = [GroundedClaim(
                claim_id=f"{section_id}-full",
                claim_text=section_text[:300],
                category=category.value if category else "",
            )]

        # Ground each claim
        for claim in claims:
            self._ground_claim(claim, evidence_pool)
            grounded.claims.append(claim)

            # Track grades
            for cit in claim.citations:
                grade = cit.evidence_grade
                grounded.evidence_grades[grade] = grounded.evidence_grades.get(grade, 0) + 1

            grounded.total_citations += len(claim.citations)

            if claim.has_contradicting_evidence:
                grounded.has_contradictions = True
                grounded.review_reasons.append(
                    f"Contradicting evidence for: {claim.claim_text[:60]}"
                )

            if claim.unsupported:
                grounded.needs_review = True
                grounded.review_reasons.append(
                    f"No evidence found for: {claim.claim_text[:60]}"
                )

        grounded.needs_review = grounded.needs_review or grounded.has_contradictions

        return grounded

    def _extract_claims(
        self,
        text: str,
        section_id: str,
        category: Optional[ClaimCategory],
    ) -> list[GroundedClaim]:
        """Extract individual claims from section text."""
        claims: list[GroundedClaim] = []
        seen_texts: set[str] = set()

        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", text)

        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue

            # Check if sentence contains a claim pattern
            is_claim = any(pattern.search(sentence) for pattern in _CLAIM_PATTERNS)
            if not is_claim:
                continue

            # Avoid duplicates
            norm = sentence.lower()[:80]
            if norm in seen_texts:
                continue
            seen_texts.add(norm)

            claims.append(GroundedClaim(
                claim_id=f"{section_id}-c{i}",
                claim_text=sentence[:300],
                category=category.value if category else "",
            ))

        return claims

    def _ground_claim(
        self,
        claim: GroundedClaim,
        evidence_pool: list[tuple[ArticleMetadata, Optional[StimulationParameters], Optional[EvidenceScore]]],
    ) -> None:
        """Match a claim to supporting evidence from the pool."""
        if not evidence_pool:
            claim.unsupported = True
            claim.confidence = ConfidenceLabel.INSUFFICIENT.value
            return

        # Score each article against this claim
        scored: list[tuple[float, ArticleMetadata, Optional[StimulationParameters], Optional[EvidenceScore]]] = []

        for article, extraction, ev_score in evidence_pool:
            match_score = self._claim_article_similarity(
                claim.claim_text, article, extraction,
            )
            scored.append((match_score, article, extraction, ev_score))

        # Sort by match score
        scored.sort(key=lambda x: x[0], reverse=True)

        # Take top-K
        for match_score, article, extraction, ev_score in scored[:self.max_citations]:
            if match_score < 0.1:
                break  # below minimum relevance

            citation = self._build_citation(
                article, extraction, ev_score, claim.claim_text, match_score,
            )
            claim.citations.append(citation)

            if citation.citation_type == "contradicts":
                claim.has_contradicting_evidence = True

        # Set confidence based on citation quality
        if not claim.citations:
            claim.unsupported = True
            claim.confidence = ConfidenceLabel.INSUFFICIENT.value
        else:
            grades = [c.evidence_grade for c in claim.citations]
            if "A" in grades:
                claim.confidence = ConfidenceLabel.HIGH.value
            elif "B" in grades:
                claim.confidence = ConfidenceLabel.MEDIUM.value
            else:
                claim.confidence = ConfidenceLabel.LOW.value

    def _claim_article_similarity(
        self,
        claim_text: str,
        article: ArticleMetadata,
        extraction: Optional[StimulationParameters],
    ) -> float:
        """Score how well an article supports a specific claim."""
        score = 0.0
        claim_lower = claim_text.lower()
        article_text = f"{article.title} {article.abstract or ''}".lower()

        # Keyword overlap between claim and article
        claim_words = set(re.findall(r"\b[a-z]{3,}\b", claim_lower))
        article_words = set(re.findall(r"\b[a-z]{3,}\b", article_text))

        if claim_words:
            overlap = len(claim_words & article_words)
            score += (overlap / len(claim_words)) * 0.4

        # Parameter specificity bonus
        if extraction and extraction.modality:
            if extraction.modality.lower() in claim_lower:
                score += 0.2

        if extraction and extraction.brain_target:
            if extraction.brain_target.lower() in claim_lower:
                score += 0.15

        # Numeric parameter matching
        claim_numbers = set(re.findall(r"\d+(?:\.\d+)?", claim_text))
        article_numbers = set(re.findall(r"\d+(?:\.\d+)?", article_text))
        if claim_numbers:
            num_overlap = len(claim_numbers & article_numbers)
            score += (num_overlap / len(claim_numbers)) * 0.15

        # Evidence level bonus
        if article.evidence_level.value in ("highest", "high"):
            score += 0.1

        return min(1.0, score)

    def _build_citation(
        self,
        article: ArticleMetadata,
        extraction: Optional[StimulationParameters],
        ev_score: Optional[EvidenceScore],
        claim_text: str,
        match_score: float,
    ) -> GroundedCitation:
        """Build a GroundedCitation from an article match."""
        # Determine citation type
        citation_type = self._determine_citation_type(article, claim_text)

        # Extract supporting quote from abstract
        supporting_quote = self._extract_supporting_quote(
            article.abstract or "", claim_text,
        )

        # Format inline citation
        from ..core.utils import format_authors
        authors = format_authors(article.authors, max_authors=2)
        year = article.year or "n.d."
        inline = f"({authors}, {year}"
        if article.pmid:
            inline += f"; PMID: {article.pmid}"
        inline += ")"

        # Format full reference
        full_authors = ", ".join(article.authors[:6])
        if len(article.authors) > 6:
            full_authors += " et al."
        ref = f"{full_authors} ({year}). {article.title}."
        if article.journal:
            ref += f" {article.journal}."
        if article.pmid:
            ref += f" PMID: {article.pmid}."
        if article.doi:
            ref += f" DOI: {article.doi}."

        return GroundedCitation(
            study_identifier=article.pmid or article.doi or "",
            title=article.title,
            authors_short=f"{authors}, {year}",
            year=article.year,
            journal=article.journal,
            citation_type=citation_type,
            claim_text=claim_text[:200],
            supporting_quote=supporting_quote,
            relevance_note=f"Match score: {match_score:.2f}",
            evidence_grade=ev_score.final_grade if ev_score else "C",
            quality_score=ev_score.quality.composite_score if ev_score and ev_score.quality else 0,
            relevance_score=ev_score.relevance.composite_score if ev_score and ev_score.relevance else 0,
            formatted_inline=inline,
            formatted_reference=ref,
        )

    @staticmethod
    def _determine_citation_type(
        article: ArticleMetadata, claim_text: str,
    ) -> str:
        """Determine if citation supports, informs, contradicts, or is a safety note."""
        text = f"{article.title} {article.abstract or ''}".lower()
        claim_lower = claim_text.lower()

        # Safety claims
        safety_keywords = ["contraindic", "adverse", "side effect", "safety", "precaution"]
        if any(kw in claim_lower for kw in safety_keywords):
            return "safety_note"

        # Contradiction signals
        negative_keywords = [
            "no effect", "ineffective", "no significant",
            "failed to demonstrate", "no improvement",
        ]
        if any(kw in text for kw in negative_keywords):
            # Only flag as contradiction if the claim is positive
            positive_claim = any(
                kw in claim_lower
                for kw in ["effective", "improvement", "reduction", "beneficial"]
            )
            if positive_claim:
                return "contradicts"

        # Indirect support
        if article.evidence_level.value in ("very_low", "low"):
            return "informs"

        return "supports"

    @staticmethod
    def _extract_supporting_quote(
        abstract: str, claim_text: str, max_length: int = 200,
    ) -> str:
        """Extract the most relevant sentence from abstract for the claim."""
        if not abstract:
            return ""

        sentences = re.split(r"(?<=[.!?])\s+", abstract)
        if not sentences:
            return ""

        # Find most similar sentence
        claim_words = set(re.findall(r"\b[a-z]{3,}\b", claim_text.lower()))
        best_sentence = ""
        best_overlap = 0

        for sentence in sentences:
            if len(sentence) < 15:
                continue
            sent_words = set(re.findall(r"\b[a-z]{3,}\b", sentence.lower()))
            overlap = len(claim_words & sent_words)
            if overlap > best_overlap:
                best_overlap = overlap
                best_sentence = sentence

        if best_sentence and len(best_sentence) > max_length:
            best_sentence = best_sentence[:max_length] + "..."

        return best_sentence
