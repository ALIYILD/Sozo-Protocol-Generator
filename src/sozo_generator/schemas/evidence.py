from __future__ import annotations

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
from ..core.enums import EvidenceLevel, EvidenceType, ClaimCategory, ConfidenceLabel


class ArticleMetadata(BaseModel):
    """Metadata for a single PubMed or manual evidence source."""
    pmid: Optional[str] = None
    doi: Optional[str] = None
    title: str
    authors: list[str] = Field(default_factory=list)
    journal: Optional[str] = None
    year: Optional[int] = None
    publication_date: Optional[str] = None
    abstract: Optional[str] = None
    url: Optional[str] = None
    evidence_type: EvidenceType = EvidenceType.NARRATIVE_REVIEW
    evidence_level: EvidenceLevel = EvidenceLevel.MEDIUM
    score: int = Field(default=3, ge=1, le=5)
    condition_slug: Optional[str] = None
    modalities: list[str] = Field(default_factory=list)
    claim_categories: list[ClaimCategory] = Field(default_factory=list)
    key_findings: list[str] = Field(default_factory=list)
    notes: Optional[str] = None
    manually_added: bool = False
    cached_at: Optional[str] = None


class EvidenceClaim(BaseModel):
    """A single clinical claim with its evidence provenance."""
    claim_id: str
    text: str
    category: ClaimCategory
    confidence: ConfidenceLabel
    evidence_level: EvidenceLevel
    supporting_pmids: list[str] = Field(default_factory=list)
    supporting_sources: list[ArticleMetadata] = Field(default_factory=list)
    contradicting_sources: list[ArticleMetadata] = Field(default_factory=list)
    review_flags: list[str] = Field(default_factory=list)
    clinical_language: str = ""  # generated language prefix
    condition_slug: str = ""
    modality: Optional[str] = None
    requires_review: bool = False
    reviewer_note: Optional[str] = None


class EvidenceDossier(BaseModel):
    """Complete evidence summary for one condition."""
    condition_slug: str
    condition_name: str
    generated_at: str
    total_sources: int = 0
    sources_by_level: dict[str, int] = Field(default_factory=dict)
    articles: list[ArticleMetadata] = Field(default_factory=list)
    claims: list[EvidenceClaim] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    review_flags: list[str] = Field(default_factory=list)
    overall_evidence_quality: EvidenceLevel = EvidenceLevel.MEDIUM
    recommended_scales: list[str] = Field(default_factory=list)
    search_queries_used: list[str] = Field(default_factory=list)
    pubmed_fetch_date: Optional[str] = None
