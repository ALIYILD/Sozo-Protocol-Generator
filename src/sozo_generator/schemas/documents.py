from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field
from ..core.enums import DocumentType, Tier, ConfidenceLabel


class SectionClaim(BaseModel):
    """A structured clinical claim attached to a section for traceability."""

    claim_id: str = ""
    text: str = ""
    category: str = ""  # ClaimCategory value
    confidence: str = ""  # ConfidenceLabel value
    supporting_pmids: list[str] = Field(default_factory=list)
    contradicting_pmids: list[str] = Field(default_factory=list)
    insufficient_evidence: bool = False
    requires_review: bool = False


class SectionContent(BaseModel):
    section_id: str
    title: str
    content: str = ""
    subsections: list["SectionContent"] = Field(default_factory=list)
    tables: list[dict] = Field(default_factory=list)
    figures: list[str] = Field(default_factory=list)  # paths to figure files
    review_flags: list[str] = Field(default_factory=list)
    evidence_pmids: list[str] = Field(default_factory=list)
    confidence_label: Optional[str] = None
    is_placeholder: bool = False
    # Phase 2: claim traceability
    claims: list[SectionClaim] = Field(default_factory=list)
    evidence_bundle_id: Optional[str] = None


class DocumentSpec(BaseModel):
    document_type: DocumentType
    tier: Tier
    condition_slug: str
    condition_name: str
    title: str
    subtitle: Optional[str] = None
    version: str = "1.0"
    date_label: str = ""
    audience: str = ""
    confidentiality_mark: str = "CONFIDENTIAL"
    sections: list[SectionContent] = Field(default_factory=list)
    figures: list[str] = Field(default_factory=list)
    references: list[dict] = Field(default_factory=list)
    review_flags: list[str] = Field(default_factory=list)
    output_filename: str = ""
    # Phase 2: build metadata
    build_id: Optional[str] = None
    evidence_snapshot_id: Optional[str] = None
    content_hash: Optional[str] = None
