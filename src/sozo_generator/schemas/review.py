from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field
from ..core.enums import ReviewFlag


class ReviewItem(BaseModel):
    flag: ReviewFlag
    location: str  # section, document, or field name
    description: str
    severity: str = "warning"  # info | warning | error
    suggested_action: Optional[str] = None
    auto_resolvable: bool = False


class DocumentQAResult(BaseModel):
    document_type: str
    tier: str
    condition_slug: str
    completeness_score: float = 0.0
    evidence_coverage: float = 0.0
    has_placeholders: bool = False
    missing_sections: list[str] = Field(default_factory=list)
    review_items: list[ReviewItem] = Field(default_factory=list)
    passed: bool = False
    notes: list[str] = Field(default_factory=list)


class ConditionQAReport(BaseModel):
    condition_slug: str
    condition_name: str
    generated_at: str
    total_documents: int = 0
    passed_documents: int = 0
    overall_completeness: float = 0.0
    overall_evidence_coverage: float = 0.0
    document_results: list[DocumentQAResult] = Field(default_factory=list)
    unresolved_flags: list[ReviewItem] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    ready_for_clinical_review: bool = False
