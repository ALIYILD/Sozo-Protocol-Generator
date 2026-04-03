"""
Visualization request/response schemas.

Every visual is schema-first: typed request in, structured response out,
with explanation, evidence linkage, and confidence metadata.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class VisualType(str, Enum):
    SPECTRAL_TOPOMAP = "spectral_topomap"
    TARGET_OVERLAY = "target_overlay"
    NETWORK_HEXAGON = "network_hexagon"
    CONNECTIVITY_HEATMAP = "connectivity_heatmap"
    BRAIN_MAP = "brain_map"
    MRI_TARGET = "mri_target"
    BEFORE_AFTER = "before_after"
    DOSE_RESPONSE = "dose_response"
    TREATMENT_TIMELINE = "treatment_timeline"


class RenderFormat(str, Enum):
    PNG = "png"
    PLOTLY_JSON = "plotly_json"
    BOTH = "both"


# ── Evidence Link ────────────────────────────────────────────────────────


class VisualEvidenceLink(BaseModel):
    pmid: str = ""
    claim: str = ""
    relevance: str = ""


# ── Explanation ──────────────────────────────────────────────────────────


class VisualExplanation(BaseModel):
    """Clinician-facing explanation attached to every visual."""
    summary: str = ""
    reasoning_chain: list[str] = Field(default_factory=list)
    eeg_findings: list[str] = Field(default_factory=list)
    network_interpretation: str = ""
    phenotype_link: str = ""
    protocol_link: str = ""
    confidence_note: str = ""


# ── Metadata ─────────────────────────────────────────────────────────────


class VisualMetadata(BaseModel):
    condition_slug: str = ""
    protocol_id: str = ""
    modality: str = ""
    targets: list[str] = Field(default_factory=list)
    bands: list[str] = Field(default_factory=list)
    timepoint: str = ""  # "baseline", "week4", "week8"
    comparison_type: str = ""  # "before_after", "longitudinal"
    source_generator: str = ""
    generator_version: str = "1.0"


# ── Request ──────────────────────────────────────────────────────────────


class VisualizationRequest(BaseModel):
    """Schema-first request for any SOZO visual."""
    visual_type: VisualType
    condition_slug: str = ""
    tier: str = "fellow"
    render_format: RenderFormat = RenderFormat.PNG

    # Protocol context
    protocol_id: str = ""
    modality: str = ""
    anodes: list[str] = Field(default_factory=list)
    cathodes: list[str] = Field(default_factory=list)
    tps_targets: list[str] = Field(default_factory=list)

    # Network context
    network_dysfunctions: dict[str, dict] = Field(default_factory=dict)

    # EEG/QEEG features (for topomaps)
    spectral_data: dict[str, dict[str, float]] = Field(default_factory=dict)
    intensity_map: dict[str, float] = Field(default_factory=dict)

    # Before/after comparison
    baseline_features: dict[str, Any] = Field(default_factory=dict)
    followup_features: dict[str, Any] = Field(default_factory=dict)

    # MRI targets
    targets: list[dict] = Field(default_factory=list)

    # Timeline phases
    phases: list[dict] = Field(default_factory=list)

    # Output options
    title: str = ""
    subtitle: str = ""
    dpi: int = 200
    figsize: Optional[tuple] = None


# ── Response ─────────────────────────────────────────────────────────────


class VisualizationResponse(BaseModel):
    """Structured response from the visualization service."""
    visual_id: str = Field(default_factory=lambda: _uid("vis-"))
    visual_type: str = ""
    render_format: str = "png"
    generated_at: str = Field(default_factory=_now)

    # Output
    image_bytes: Optional[bytes] = None  # PNG bytes (excluded from JSON serialization)
    image_path: str = ""
    plotly_json: Optional[dict] = None

    # Explanation + evidence
    explanation: VisualExplanation = Field(default_factory=VisualExplanation)
    evidence: list[VisualEvidenceLink] = Field(default_factory=list)
    confidence: float = 0.0
    metadata: VisualMetadata = Field(default_factory=VisualMetadata)

    # Status
    success: bool = False
    error: str = ""
    warnings: list[str] = Field(default_factory=list)

    class Config:
        # Exclude bytes from JSON serialization
        json_encoders = {bytes: lambda v: f"<{len(v)} bytes>"}
