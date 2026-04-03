"""
Phase 8 Evidence Ingestion — Data Models
=========================================
Pydantic v2 models for the full evidence ingestion pipeline:

  PaperRaw            raw record from any retrieval source
  PICOExtract         LLM-extracted PICO + outcome fields
  ProtocolParameters  extracted neuromodulation protocol parameters
  EvidenceRecord      fully enriched record (paper + PICO + protocol)
  ConditionCorpus     complete corpus for one condition

All models use strict typing, sensible defaults, and UTC ISO timestamps.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, computed_field, model_validator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utc_now() -> str:
    """Return current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _new_uuid() -> str:
    """Return a fresh UUID4 as a string."""
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# ConsensusFinding
# ---------------------------------------------------------------------------

class ConsensusFinding(BaseModel):
    """
    A structured finding extracted directly from the Consensus API response.

    The Consensus API returns per-paper excerpts (claim sentences) alongside
    structured metadata.  This model captures both the raw API payload and
    the normalised fields used downstream.
    """

    consensus_paper_id: str = Field(
        ...,
        description="Consensus-internal paper identifier (from API response).",
    )
    query: str = Field(
        ...,
        description="The query string that produced this finding.",
    )
    claim: str = Field(
        ...,
        description="Claim excerpt / key finding sentence returned by Consensus.",
    )
    outcome_direction: Optional[Literal["positive", "negative", "null", "mixed", "unknown"]] = Field(
        default=None,
        description="Direction of the reported outcome as labelled by Consensus.",
    )
    study_type: Optional[str] = Field(
        default=None,
        description="Study design label from Consensus (e.g. 'RCT', 'Meta-Analysis').",
    )
    sample_size: Optional[int] = Field(
        default=None,
        description="Reported sample size (N) for the study.",
    )
    doi: Optional[str] = Field(
        default=None,
        description="DOI without 'https://doi.org/' prefix; used for deduplication.",
    )
    pmid: Optional[str] = Field(
        default=None,
        description="PubMed ID when available.",
    )
    title: Optional[str] = Field(
        default=None,
        description="Paper title as returned by Consensus.",
    )
    authors: list[str] = Field(
        default_factory=list,
        description="Author list as returned by Consensus.",
    )
    year: Optional[int] = Field(
        default=None,
        description="Publication year.",
    )
    journal: Optional[str] = Field(
        default=None,
        description="Journal / venue name.",
    )
    url: Optional[str] = Field(
        default=None,
        description="Consensus landing page URL for this paper.",
    )
    citation_count: int = Field(
        default=0,
        description="Citation count as reported by Consensus.",
    )
    retrieved_at: str = Field(
        default_factory=_utc_now,
        description="UTC ISO 8601 timestamp when this finding was retrieved.",
    )


# ---------------------------------------------------------------------------
# PaperRaw
# ---------------------------------------------------------------------------

class PaperRaw(BaseModel):
    """
    Raw bibliographic record as returned by a retrieval source before any
    LLM enrichment.  One PaperRaw is produced per paper per source; dedup
    happens downstream.
    """

    source: Literal["openalex", "semantic_scholar", "pubmed", "consensus", "manual"] = Field(
        ...,
        description="Which retrieval source produced this record.",
    )
    source_id: str = Field(
        ...,
        description=(
            "Primary identifier within the source system: OpenAlex Work ID, "
            "Semantic Scholar paperId, PubMed PMID, or a curator-assigned slug."
        ),
    )
    doi: Optional[str] = Field(
        default=None,
        description="Digital Object Identifier, without the 'https://doi.org/' prefix.",
    )
    pmid: Optional[str] = Field(
        default=None,
        description="PubMed identifier (numeric string).",
    )
    title: str = Field(..., description="Full paper title.")
    authors: list[str] = Field(
        default_factory=list,
        description="Author display names, ordered as they appear on the paper.",
    )
    year: Optional[int] = Field(
        default=None,
        description="Publication year (integer).",
    )
    journal: Optional[str] = Field(
        default=None,
        description="Journal or venue name.",
    )
    abstract: Optional[str] = Field(
        default=None,
        description="Full abstract text.",
    )
    open_access: bool = Field(
        default=False,
        description="True if the paper is open-access.",
    )
    oa_url: Optional[str] = Field(
        default=None,
        description="URL to the full-text PDF or landing page when open-access.",
    )
    s2_tldr: Optional[str] = Field(
        default=None,
        description="Semantic Scholar AI-generated TL;DR sentence (S2 only).",
    )
    s2_influential_citations: int = Field(
        default=0,
        description="Number of influential citations reported by Semantic Scholar.",
    )
    s2_citation_count: int = Field(
        default=0,
        description="Total citation count reported by Semantic Scholar.",
    )
    study_design: Optional[str] = Field(
        default=None,
        description=(
            "Coarse study-design label inferred from title/abstract: "
            "'RCT', 'meta_analysis', 'systematic_review', 'cohort', "
            "'pilot', 'case_series', 'review', or 'other'."
        ),
    )
    condition_tags: list[str] = Field(
        default_factory=list,
        description="Condition slugs this paper is tagged to (e.g. ['depression', 'anxiety']).",
    )
    modality_tags: list[str] = Field(
        default_factory=list,
        description="Neuromodulation modality labels this paper covers (e.g. ['tDCS', 'TMS']).",
    )
    fetched_at: str = Field(
        default_factory=_utc_now,
        description="UTC ISO 8601 timestamp when this record was retrieved.",
    )


# ---------------------------------------------------------------------------
# PICOExtract
# ---------------------------------------------------------------------------

class PICOExtract(BaseModel):
    """
    PICO (Population / Intervention / Comparator / Outcomes) fields extracted
    by an LLM from the abstract or full text.  All fields are Optional because
    the LLM may not find every component in every paper.
    """

    # -- Population ----------------------------------------------------------
    population: Optional[str] = Field(
        default=None,
        description="Description of the study population (e.g. 'adults with MDD, HAM-D ≥ 18').",
    )
    population_n: Optional[int] = Field(
        default=None,
        description="Total enrolled sample size (N).",
    )

    # -- Intervention --------------------------------------------------------
    intervention: Optional[str] = Field(
        default=None,
        description="Active treatment arm description.",
    )

    # -- Comparator ----------------------------------------------------------
    comparator: Optional[str] = Field(
        default=None,
        description="Control or comparator arm (e.g. 'sham tDCS', 'placebo', 'waitlist').",
    )

    # -- Outcomes ------------------------------------------------------------
    outcomes_primary: Optional[str] = Field(
        default=None,
        description="Primary outcome measure(s) and reported result.",
    )
    outcomes_secondary: Optional[str] = Field(
        default=None,
        description="Secondary outcome measure(s) and reported result.",
    )
    result_summary: Optional[str] = Field(
        default=None,
        description="1-2 sentence plain-language summary of the key finding.",
    )
    effect_size: Optional[str] = Field(
        default=None,
        description="Reported effect size (e.g. 'Cohen d = 0.72', 'SMD = 0.45 [0.12–0.78]').",
    )
    p_value: Optional[str] = Field(
        default=None,
        description="Primary p-value or confidence interval as a string (e.g. 'p < 0.001').",
    )
    follow_up_weeks: Optional[int] = Field(
        default=None,
        description="Duration of follow-up after treatment end, in weeks.",
    )
    conclusion: Optional[str] = Field(
        default=None,
        description="Authors' stated conclusion sentence.",
    )

    # -- LLM meta -----------------------------------------------------------
    relevance_score: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description=(
            "LLM self-rated relevance to neuromodulation protocol design (1 = irrelevant, "
            "5 = directly informs parameter selection)."
        ),
    )
    irrelevant: bool = Field(
        default=False,
        description="True if the LLM judged the paper as not relevant; record will be excluded.",
    )
    irrelevance_reason: Optional[str] = Field(
        default=None,
        description="Free-text explanation when irrelevant=True.",
    )
    extraction_confidence: Optional[Literal["high", "medium", "low"]] = Field(
        default=None,
        description="LLM self-rated confidence in the extraction quality.",
    )

    @model_validator(mode="after")
    def _irrelevance_consistency(self) -> PICOExtract:
        """Warn if irrelevant is True but no reason is given."""
        if self.irrelevant and not self.irrelevance_reason:
            # Soft default — does not raise
            object.__setattr__(self, "irrelevance_reason", "No reason provided by LLM.")
        return self


# ---------------------------------------------------------------------------
# ProtocolParameters
# ---------------------------------------------------------------------------

class ProtocolParameters(BaseModel):
    """
    Neuromodulation protocol parameters extracted from a paper.  Only
    populated when the paper explicitly describes a stimulation protocol.
    All fields are Optional; downstream code must handle None gracefully.
    """

    # -- Modality & target ---------------------------------------------------
    modality: Optional[str] = Field(
        default=None,
        description=(
            "Stimulation modality: 'TMS', 'tDCS', 'tACS', 'NFB', 'PBM', "
            "'PEMF', 'VNS', 'CES', 'TPS', 'taVNS'."
        ),
    )
    target_region: Optional[str] = Field(
        default=None,
        description="Stimulation target region (e.g. 'Left DLPFC', 'M1', 'Cerebellum').",
    )

    # -- Frequency & intensity -----------------------------------------------
    frequency_hz: Optional[float] = Field(
        default=None,
        description="Stimulation frequency in Hz.",
    )
    intensity: Optional[str] = Field(
        default=None,
        description="Free-text intensity descriptor (e.g. '110% RMT', '2 mA', '40 mW/cm²').",
    )
    intensity_value: Optional[float] = Field(
        default=None,
        description="Numeric intensity value (unit specified separately in intensity_unit).",
    )
    intensity_unit: Optional[Literal["pct_rmt", "mA", "mW_cm2", "gauss", "other"]] = Field(
        default=None,
        description="Unit for intensity_value.",
    )

    # -- Pulse & pattern -----------------------------------------------------
    pulse_type: Optional[str] = Field(
        default=None,
        description=(
            "Pulse pattern: 'rTMS', 'iTBS', 'cTBS', 'single_pulse', 'paired_pulse', "
            "'biphasic', 'monophasic', 'DC'."
        ),
    )
    pulses_per_session: Optional[int] = Field(
        default=None,
        description="Total number of pulses delivered per session.",
    )

    # -- Dosing schedule -----------------------------------------------------
    sessions_total: Optional[int] = Field(
        default=None,
        description="Total number of stimulation sessions in the protocol.",
    )
    sessions_per_week: Optional[int] = Field(
        default=None,
        description="Number of sessions scheduled per week.",
    )
    session_duration_min: Optional[int] = Field(
        default=None,
        description="Duration of each session in minutes.",
    )

    # -- Electrode / coil geometry -------------------------------------------
    electrode_montage: Optional[str] = Field(
        default=None,
        description="Electrode montage description (tDCS/tACS/CES specific).",
    )
    anode_position: Optional[str] = Field(
        default=None,
        description="Anode electrode position (EEG 10-20 label or anatomical landmark).",
    )
    cathode_position: Optional[str] = Field(
        default=None,
        description="Cathode electrode position.",
    )
    coil_type: Optional[str] = Field(
        default=None,
        description="TMS coil geometry (e.g. 'figure-8', 'H-coil', 'circular').",
    )

    # -- PBM / LLLT specific -------------------------------------------------
    wavelength_nm: Optional[float] = Field(
        default=None,
        description="Light wavelength in nanometres (PBM/LLLT protocols only).",
    )
    energy_density_j_cm2: Optional[float] = Field(
        default=None,
        description="Energy density in J/cm² (PBM/LLLT protocols only).",
    )

    # -- Efficacy summary ----------------------------------------------------
    response_rate_pct: Optional[float] = Field(
        default=None,
        description="Response rate percentage reported in the paper.",
    )
    remission_rate_pct: Optional[float] = Field(
        default=None,
        description="Remission rate percentage reported in the paper.",
    )
    primary_outcome_measure: Optional[str] = Field(
        default=None,
        description=(
            "Primary clinical outcome scale used (e.g. 'HAM-D', 'MADRS', 'PHQ-9', "
            "'UPDRS', 'MMSE')."
        ),
    )


# ---------------------------------------------------------------------------
# EvidenceRecord
# ---------------------------------------------------------------------------

class EvidenceRecord(BaseModel):
    """
    Fully enriched record combining raw bibliographic data, LLM-extracted
    PICO fields, extracted protocol parameters, and pipeline metadata.

    This is the canonical unit stored in ConditionCorpus.records.
    """

    record_id: str = Field(
        default_factory=_new_uuid,
        description="UUID4 unique identifier for this record within the pipeline.",
    )
    condition_slug: str = Field(
        ...,
        description="Slug of the condition this record belongs to (e.g. 'depression').",
    )
    primary_modality: Optional[str] = Field(
        default=None,
        description="Primary modality assigned to this record after enrichment.",
    )

    # -- Core payload --------------------------------------------------------
    paper: PaperRaw = Field(..., description="Raw bibliographic record from retrieval source.")
    pico: Optional[PICOExtract] = Field(
        default=None,
        description="LLM-extracted PICO fields; None until extraction step runs.",
    )
    protocol_params: Optional[ProtocolParameters] = Field(
        default=None,
        description="Extracted protocol parameters; None if paper does not describe a protocol.",
    )
    consensus_finding: Optional[ConsensusFinding] = Field(
        default=None,
        description=(
            "Structured finding from Consensus API for this paper, if retrieved via "
            "the Consensus source.  None for records from other sources."
        ),
    )

    # -- Risk of bias (Phase 9 reserved) ------------------------------------
    rob_risk: Optional[Literal["low", "unclear", "high"]] = Field(
        default=None,
        description=(
            "Overall risk-of-bias rating from RobotReviewer (Phase 9). "
            "Reserved — always None in Phase 8."
        ),
    )
    rob_domains: Optional[dict[str, str]] = Field(
        default=None,
        description=(
            "Per-domain risk-of-bias ratings (Phase 9). "
            "Keys are Cochrane RoB 2.0 domain names; values are 'low'/'unclear'/'high'."
        ),
    )

    # -- Evidence grading ----------------------------------------------------
    evidence_grade: Optional[Literal["A", "B", "C", "D", "expert_opinion"]] = Field(
        default=None,
        description=(
            "GRADE-style evidence grade assigned by the pipeline: "
            "A (high), B (moderate), C (low), D (very low), expert_opinion."
        ),
    )

    # -- Inclusion / exclusion -----------------------------------------------
    included: bool = Field(
        default=True,
        description="False if this record has been filtered out of the active corpus.",
    )
    exclusion_reason: Optional[str] = Field(
        default=None,
        description="Human-readable reason for exclusion when included=False.",
    )

    # -- Pipeline provenance -------------------------------------------------
    ingested_at: str = Field(
        default_factory=_utc_now,
        description="UTC ISO 8601 timestamp when this record entered the pipeline.",
    )
    pipeline_version: str = Field(
        default="phase8_v1",
        description="Pipeline version string for reproducibility.",
    )

    # -- Computed properties -------------------------------------------------

    @computed_field  # type: ignore[misc]
    @property
    def citation_key(self) -> str:
        """
        Return a citation key in 'FirstAuthorYear' format, e.g. 'Brunoni2017'.
        Falls back to 'Unknown' + year if no authors are available.
        """
        year_str = str(self.paper.year) if self.paper.year else "XXXX"
        if self.paper.authors:
            first_author = self.paper.authors[0]
            # Strip trailing punctuation then split into tokens
            parts = [p.rstrip(".,;") for p in first_author.strip().split() if p]
            if parts:
                # The surname is the longest token (initials are 1-2 chars).
                # Handles "Brunoni AR", "AR Brunoni", "A.R. Brunoni", "Brunoni".
                surname = max(parts, key=len)
            else:
                surname = "Unknown"
            return f"{surname}{year_str}"
        return f"Unknown{year_str}"

    # -- Methods -------------------------------------------------------------

    def is_protocol_paper(self) -> bool:
        """
        Return True if this record contains extracted protocol parameters with
        at least a modality and a total session count defined.

        A 'protocol paper' is one from which concrete treatment parameters
        can be inferred for protocol generation.
        """
        if self.protocol_params is None:
            return False
        return (
            self.protocol_params.modality is not None
            and self.protocol_params.sessions_total is not None
        )


# ---------------------------------------------------------------------------
# ConditionCorpus
# ---------------------------------------------------------------------------

class ConditionCorpus(BaseModel):
    """
    The complete evidence corpus for a single clinical condition, as produced
    by the Phase 8 ingestion pipeline.

    Contains all EvidenceRecords (included and excluded), aggregate statistics,
    and provenance metadata.
    """

    condition_slug: str = Field(..., description="Machine-readable condition identifier.")
    condition_name: str = Field(..., description="Human-readable condition name.")
    modalities_covered: list[str] = Field(
        default_factory=list,
        description="Modalities for which evidence was retrieved.",
    )
    total_papers_fetched: int = Field(
        default=0,
        description="Total records retrieved across all sources before dedup/exclusion.",
    )
    total_included: int = Field(
        default=0,
        description="Records remaining after exclusion filters.",
    )
    total_excluded: int = Field(
        default=0,
        description="Records removed by exclusion filters.",
    )
    records: list[EvidenceRecord] = Field(
        default_factory=list,
        description="All EvidenceRecord objects (both included and excluded).",
    )

    # -- Build metadata ------------------------------------------------------
    build_date: str = Field(
        default_factory=_utc_now,
        description="UTC ISO 8601 timestamp when this corpus was built.",
    )
    query_config_version: str = Field(
        default="",
        description="Version tag of the ConditionQueryConfig used to build this corpus.",
    )

    # -- Breakdown dicts -----------------------------------------------------
    sources_breakdown: dict[str, int] = Field(
        default_factory=lambda: {"openalex": 0, "semantic_scholar": 0, "pubmed": 0, "manual": 0},
        description="Count of fetched papers per retrieval source.",
    )
    evidence_grade_breakdown: dict[str, int] = Field(
        default_factory=lambda: {"A": 0, "B": 0, "C": 0, "D": 0, "expert_opinion": 0},
        description="Count of included papers per GRADE evidence level.",
    )
    rob_breakdown: dict[str, int] = Field(
        default_factory=lambda: {"low": 0, "unclear": 0, "high": 0},
        description="Risk-of-bias distribution (populated in Phase 9).",
    )

    pipeline_version: str = Field(
        default="phase8_v1",
        description="Pipeline version for reproducibility.",
    )

    # -- Properties ----------------------------------------------------------

    @property
    def included_records(self) -> list[EvidenceRecord]:
        """Return only EvidenceRecords where included=True."""
        return [r for r in self.records if r.included]

    @property
    def protocol_papers(self) -> list[EvidenceRecord]:
        """
        Return included records that qualify as protocol papers, i.e. those
        where is_protocol_paper() returns True.
        """
        return [r for r in self.included_records if r.is_protocol_paper()]

    # -- Methods -------------------------------------------------------------

    def by_modality(self, modality: str) -> list[EvidenceRecord]:
        """
        Filter included records by primary_modality (case-insensitive exact match).

        Parameters
        ----------
        modality:
            Modality label to filter on (e.g. 'tDCS', 'TMS').

        Returns
        -------
        list[EvidenceRecord]
            Included records whose primary_modality matches the given label.
        """
        modality_lower = modality.lower()
        return [
            r for r in self.included_records
            if r.primary_modality is not None
            and r.primary_modality.lower() == modality_lower
        ]

    def to_summary_dict(self) -> dict[str, Any]:
        """
        Return a summary dictionary suitable for logging or status reporting.
        The full records list is omitted; only aggregate statistics are included.

        Returns
        -------
        dict[str, Any]
            Summary-level metadata about the corpus.
        """
        return {
            "condition_slug": self.condition_slug,
            "condition_name": self.condition_name,
            "modalities_covered": self.modalities_covered,
            "total_papers_fetched": self.total_papers_fetched,
            "total_included": self.total_included,
            "total_excluded": self.total_excluded,
            "protocol_papers_count": len(self.protocol_papers),
            "sources_breakdown": self.sources_breakdown,
            "evidence_grade_breakdown": self.evidence_grade_breakdown,
            "rob_breakdown": self.rob_breakdown,
            "build_date": self.build_date,
            "query_config_version": self.query_config_version,
            "pipeline_version": self.pipeline_version,
        }
