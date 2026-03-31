from typing import Optional
from pydantic import BaseModel, Field
from ..core.enums import DocumentType, Tier


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
