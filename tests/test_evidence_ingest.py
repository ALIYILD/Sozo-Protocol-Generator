"""
test_evidence_ingest.py
=======================
Comprehensive pytest suite for the Phase 8 evidence ingestion pipeline.

Covers:
- PaperRaw, PICOExtract, ProtocolParameters, EvidenceRecord, ConditionCorpus Pydantic models
- grade_evidence() grading function
- CONDITION_CONFIGS completeness and structural correctness
- EvidenceIngestor deduplication logic (mocked API calls)
- PICOExtractor LLM response parsing and error handling (mocked LLM calls)
- Corpus save-and-load round-trip (using tmp_path)

All external API calls and LLM calls are mocked — no network requests are made.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from sozo_generator.evidence.phase8.models import (
    PaperRaw,
    PICOExtract,
    ProtocolParameters,
    EvidenceRecord,
    ConditionCorpus,
)
from sozo_generator.evidence.phase8.config import (
    CONDITION_CONFIGS,
    ALL_CONDITION_SLUGS,
    PIPELINE_VERSION,
)
from sozo_generator.evidence.phase8.pico_extractor import PICOExtractor, grade_evidence

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "phase8_sample_papers.json"


@pytest.fixture
def sample_papers() -> list[PaperRaw]:
    """Load sample PaperRaw objects from fixture file."""
    data = json.loads(FIXTURE_PATH.read_text())
    return [PaperRaw(**p) for p in data]


@pytest.fixture
def rct_paper(sample_papers: list[PaperRaw]) -> PaperRaw:
    """First paper from fixture (RCT, tDCS + depression)."""
    return sample_papers[0]


@pytest.fixture
def meta_paper(sample_papers: list[PaperRaw]) -> PaperRaw:
    """Second paper from fixture (meta-analysis, TMS + depression)."""
    return sample_papers[1]


@pytest.fixture
def duplicate_paper(sample_papers: list[PaperRaw]) -> PaperRaw:
    """Fifth paper — same DOI as first, different source."""
    return sample_papers[4]


@pytest.fixture
def irrelevant_paper(sample_papers: list[PaperRaw]) -> PaperRaw:
    """Sixth paper — irrelevant to neuromodulation."""
    return sample_papers[5]


# ---------------------------------------------------------------------------
# Mock LLM response constant
# ---------------------------------------------------------------------------

MOCK_LLM_RESPONSE = json.dumps([{
    "paper_index": 0,
    "pico": {
        "population": "Adults with MDD", "population_n": 40,
        "intervention": "tDCS 2mA F3/Fp2 20min", "comparator": "sham",
        "outcomes_primary": "HAM-D reduction", "outcomes_secondary": "MADRS",
        "result_summary": "Active tDCS significantly reduced HAM-D scores vs sham.",
        "effect_size": "d=0.72", "p_value": "p<0.001", "follow_up_weeks": 4,
        "conclusion": "tDCS is effective for MDD.", "relevance_score": 5,
        "irrelevant": False, "irrelevance_reason": None, "extraction_confidence": "high",
    },
    "protocol_params": {
        "modality": "tDCS", "target_region": "Left DLPFC",
        "frequency_hz": None, "intensity": "2 mA", "intensity_value": 2.0,
        "intensity_unit": "mA", "pulse_type": "DC", "pulses_per_session": None,
        "sessions_total": 20, "sessions_per_week": 5, "session_duration_min": 20,
        "electrode_montage": "F3/Fp2", "anode_position": "F3", "cathode_position": "Fp2",
        "coil_type": None, "wavelength_nm": None, "energy_density_j_cm2": None,
        "response_rate_pct": 60.0, "remission_rate_pct": 35.0,
        "primary_outcome_measure": "HAM-D",
    },
}])


# ===========================================================================
# TestPaperRawModel
# ===========================================================================

class TestPaperRawModel:
    """Tests for the PaperRaw Pydantic model."""

    def test_paper_raw_creates_with_required_fields(self) -> None:
        """source, source_id, and title are required fields."""
        paper = PaperRaw(source="openalex", source_id="W123", title="Test Paper")
        assert paper.source == "openalex"
        assert paper.source_id == "W123"
        assert paper.title == "Test Paper"

    def test_paper_raw_requires_source(self) -> None:
        """Omitting source raises ValidationError."""
        with pytest.raises(ValidationError):
            PaperRaw(source_id="W123", title="Test Paper")  # type: ignore[call-arg]

    def test_paper_raw_requires_source_id(self) -> None:
        """Omitting source_id raises ValidationError."""
        with pytest.raises(ValidationError):
            PaperRaw(source="openalex", title="Test Paper")  # type: ignore[call-arg]

    def test_paper_raw_requires_title(self) -> None:
        """Omitting title raises ValidationError."""
        with pytest.raises(ValidationError):
            PaperRaw(source="openalex", source_id="W123")  # type: ignore[call-arg]

    def test_paper_raw_fetched_at_auto_populated(self) -> None:
        """fetched_at is auto-set to a non-empty UTC timestamp."""
        paper = PaperRaw(source="pubmed", source_id="123", title="Paper")
        assert paper.fetched_at
        assert "T" in paper.fetched_at  # ISO 8601 format contains 'T'

    def test_paper_raw_defaults(self) -> None:
        """Default values: open_access=False, list fields empty, int fields 0."""
        paper = PaperRaw(source="pubmed", source_id="123", title="Paper")
        assert paper.open_access is False
        assert paper.authors == []
        assert paper.condition_tags == []
        assert paper.modality_tags == []
        assert paper.s2_influential_citations == 0
        assert paper.s2_citation_count == 0

    def test_paper_raw_doi_optional(self) -> None:
        """doi=None is a valid state."""
        paper = PaperRaw(source="openalex", source_id="W99", title="No DOI Paper", doi=None)
        assert paper.doi is None

    def test_paper_raw_from_fixture(self, sample_papers: list[PaperRaw]) -> None:
        """All 6 fixture papers load successfully."""
        assert len(sample_papers) == 6
        for p in sample_papers:
            assert isinstance(p, PaperRaw)
            assert p.title


# ===========================================================================
# TestPICOExtractModel
# ===========================================================================

class TestPICOExtractModel:
    """Tests for the PICOExtract Pydantic model."""

    def test_pico_all_optional(self) -> None:
        """PICOExtract() with no arguments is valid — all fields are optional."""
        pico = PICOExtract()
        assert pico.population is None
        assert pico.intervention is None
        assert pico.relevance_score is None

    def test_pico_relevance_score_range_valid(self) -> None:
        """relevance_score values 1 through 5 are all valid."""
        for score in range(1, 6):
            pico = PICOExtract(relevance_score=score)
            assert pico.relevance_score == score

    def test_pico_relevance_score_zero_raises(self) -> None:
        """relevance_score=0 is below the minimum of 1 and raises ValidationError."""
        with pytest.raises(ValidationError):
            PICOExtract(relevance_score=0)

    def test_pico_relevance_score_six_raises(self) -> None:
        """relevance_score=6 exceeds the maximum of 5 and raises ValidationError."""
        with pytest.raises(ValidationError):
            PICOExtract(relevance_score=6)

    def test_pico_irrelevance_consistency(self) -> None:
        """irrelevant=True with no reason gets a default reason string (no crash)."""
        pico = PICOExtract(irrelevant=True, irrelevance_reason=None)
        assert pico.irrelevant is True
        assert pico.irrelevance_reason is not None
        assert len(pico.irrelevance_reason) > 0

    def test_pico_extraction_confidence_valid_values(self) -> None:
        """Only 'high', 'medium', and 'low' are accepted for extraction_confidence."""
        for val in ("high", "medium", "low"):
            pico = PICOExtract(extraction_confidence=val)  # type: ignore[arg-type]
            assert pico.extraction_confidence == val

    def test_pico_extraction_confidence_invalid_raises(self) -> None:
        """An invalid extraction_confidence string raises ValidationError."""
        with pytest.raises(ValidationError):
            PICOExtract(extraction_confidence="excellent")  # type: ignore[arg-type]


# ===========================================================================
# TestProtocolParametersModel
# ===========================================================================

class TestProtocolParametersModel:
    """Tests for the ProtocolParameters Pydantic model."""

    def test_protocol_params_all_optional(self) -> None:
        """ProtocolParameters() with no arguments is valid — all fields are optional."""
        params = ProtocolParameters()
        assert params.modality is None
        assert params.sessions_total is None
        assert params.intensity_unit is None

    def test_protocol_params_intensity_unit_valid_values(self) -> None:
        """Valid intensity_unit literals are accepted."""
        for unit in ("pct_rmt", "mA", "mW_cm2", "gauss", "other"):
            params = ProtocolParameters(intensity_unit=unit)  # type: ignore[arg-type]
            assert params.intensity_unit == unit

    def test_protocol_params_intensity_unit_invalid_raises(self) -> None:
        """An invalid intensity_unit string raises ValidationError."""
        with pytest.raises(ValidationError):
            ProtocolParameters(intensity_unit="volts")  # type: ignore[arg-type]


# ===========================================================================
# TestEvidenceRecordModel
# ===========================================================================

class TestEvidenceRecordModel:
    """Tests for the EvidenceRecord Pydantic model."""

    def _make_paper(self, **kwargs) -> PaperRaw:
        defaults = {"source": "openalex", "source_id": "W001", "title": "Test"}
        defaults.update(kwargs)
        return PaperRaw(**defaults)

    def _make_record(self, **kwargs) -> EvidenceRecord:
        paper = kwargs.pop("paper", self._make_paper())
        defaults = {"condition_slug": "depression", "paper": paper}
        defaults.update(kwargs)
        return EvidenceRecord(**defaults)

    def test_record_id_auto_generated(self) -> None:
        """record_id is automatically set to a UUID4 string."""
        record = self._make_record()
        assert record.record_id
        # UUID4 strings are 36 chars with hyphens
        assert len(record.record_id) == 36
        assert record.record_id.count("-") == 4

    def test_record_ids_are_unique(self) -> None:
        """Each record gets a different auto-generated UUID."""
        r1 = self._make_record()
        r2 = self._make_record()
        assert r1.record_id != r2.record_id

    def test_citation_key_format(self) -> None:
        """Citation key is 'FirstAuthorSurname' + year, e.g. 'Brunoni2022'."""
        paper = self._make_paper(authors=["Brunoni AR", "Valiengo L"], year=2022)
        record = self._make_record(paper=paper)
        assert record.citation_key == "Brunoni2022"

    def test_citation_key_unknown_when_no_authors(self) -> None:
        """When authors list is empty, citation key falls back to 'UnknownXXXX'."""
        paper = self._make_paper(authors=[], year=2019)
        record = self._make_record(paper=paper)
        assert record.citation_key == "Unknown2019"

    def test_citation_key_unknown_when_no_year(self) -> None:
        """When year is None, the year portion is 'XXXX'."""
        paper = self._make_paper(authors=[], year=None)
        record = self._make_record(paper=paper)
        assert record.citation_key == "UnknownXXXX"

    def test_is_protocol_paper_true(self) -> None:
        """is_protocol_paper() returns True when modality and sessions_total are set."""
        params = ProtocolParameters(modality="tDCS", sessions_total=20)
        record = self._make_record(protocol_params=params)
        assert record.is_protocol_paper() is True

    def test_is_protocol_paper_false_no_params(self) -> None:
        """is_protocol_paper() returns False when protocol_params is None."""
        record = self._make_record(protocol_params=None)
        assert record.is_protocol_paper() is False

    def test_is_protocol_paper_false_incomplete(self) -> None:
        """is_protocol_paper() returns False when only modality is set (no sessions_total)."""
        params = ProtocolParameters(modality="TMS", sessions_total=None)
        record = self._make_record(protocol_params=params)
        assert record.is_protocol_paper() is False

    def test_rob_fields_reserved_none(self) -> None:
        """rob_risk and rob_domains default to None in Phase 8."""
        record = self._make_record()
        assert record.rob_risk is None
        assert record.rob_domains is None


# ===========================================================================
# TestConditionCorpus
# ===========================================================================

class TestConditionCorpus:
    """Tests for the ConditionCorpus Pydantic model and its properties."""

    def _make_paper(self, **kwargs) -> PaperRaw:
        defaults = {"source": "openalex", "source_id": "W001", "title": "Paper"}
        defaults.update(kwargs)
        return PaperRaw(**defaults)

    def _make_record(self, included: bool = True, protocol_params=None, modality: str | None = None) -> EvidenceRecord:
        return EvidenceRecord(
            condition_slug="depression",
            paper=self._make_paper(source_id=f"W{id(object())}"),
            included=included,
            primary_modality=modality,
            protocol_params=protocol_params,
        )

    def _make_corpus(self, records: list[EvidenceRecord]) -> ConditionCorpus:
        return ConditionCorpus(
            condition_slug="depression",
            condition_name="Major Depressive Disorder",
            records=records,
            total_papers_fetched=len(records),
            total_included=sum(1 for r in records if r.included),
            total_excluded=sum(1 for r in records if not r.included),
        )

    def test_included_records_filters_correctly(self) -> None:
        """included_records property returns only records where included=True."""
        r_in = self._make_record(included=True)
        r_out = self._make_record(included=False)
        corpus = self._make_corpus([r_in, r_out])
        assert len(corpus.included_records) == 1
        assert corpus.included_records[0].record_id == r_in.record_id

    def test_protocol_papers_filters_correctly(self) -> None:
        """protocol_papers returns only included records where is_protocol_paper() is True."""
        params_full = ProtocolParameters(modality="tDCS", sessions_total=20)
        params_partial = ProtocolParameters(modality="TMS")

        r_protocol = self._make_record(included=True, protocol_params=params_full)
        r_no_sessions = self._make_record(included=True, protocol_params=params_partial)
        r_excluded = self._make_record(included=False, protocol_params=params_full)

        corpus = self._make_corpus([r_protocol, r_no_sessions, r_excluded])
        pp = corpus.protocol_papers
        assert len(pp) == 1
        assert pp[0].record_id == r_protocol.record_id

    def test_by_modality_filters_correctly(self) -> None:
        """by_modality() returns only included records with matching primary_modality."""
        r_tdcs = self._make_record(included=True, modality="tDCS")
        r_tms = self._make_record(included=True, modality="TMS")
        r_excluded_tdcs = self._make_record(included=False, modality="tDCS")

        corpus = self._make_corpus([r_tdcs, r_tms, r_excluded_tdcs])
        result = corpus.by_modality("tDCS")
        assert len(result) == 1
        assert result[0].record_id == r_tdcs.record_id

    def test_by_modality_case_insensitive(self) -> None:
        """by_modality() is case-insensitive."""
        r = self._make_record(included=True, modality="tDCS")
        corpus = self._make_corpus([r])
        assert len(corpus.by_modality("TDCS")) == 1
        assert len(corpus.by_modality("tdcs")) == 1

    def test_to_summary_dict_has_required_keys(self) -> None:
        """to_summary_dict() includes all required aggregate keys."""
        corpus = self._make_corpus([])
        summary = corpus.to_summary_dict()
        required_keys = {
            "condition_slug", "condition_name", "modalities_covered",
            "total_papers_fetched", "total_included", "total_excluded",
            "protocol_papers_count", "sources_breakdown", "evidence_grade_breakdown",
            "rob_breakdown", "build_date", "query_config_version", "pipeline_version",
        }
        assert required_keys.issubset(summary.keys())

    def test_to_summary_dict_excludes_records_list(self) -> None:
        """to_summary_dict() must NOT include the full records list."""
        r = self._make_record()
        corpus = self._make_corpus([r])
        summary = corpus.to_summary_dict()
        assert "records" not in summary


# ===========================================================================
# TestGradeEvidence
# ===========================================================================

class TestGradeEvidence:
    """Tests for the grade_evidence() helper function."""

    def test_grade_a_for_meta_analysis_high_confidence(self) -> None:
        """meta_analysis study design + high confidence extraction → Grade A."""
        pico = PICOExtract(extraction_confidence="high", relevance_score=5)
        assert grade_evidence("meta_analysis", pico) == "A"

    def test_grade_a_for_systematic_review_high_confidence(self) -> None:
        """systematic_review + high confidence → Grade A."""
        pico = PICOExtract(extraction_confidence="high", relevance_score=4)
        assert grade_evidence("systematic_review", pico) == "A"

    def test_grade_b_for_meta_analysis_medium_confidence(self) -> None:
        """meta_analysis + medium confidence → Grade B (not A)."""
        pico = PICOExtract(extraction_confidence="medium", relevance_score=4)
        assert grade_evidence("meta_analysis", pico) == "B"

    def test_grade_b_for_rct_medium_confidence(self) -> None:
        """RCT study design + medium confidence → Grade B."""
        pico = PICOExtract(extraction_confidence="medium", relevance_score=4)
        assert grade_evidence("RCT", pico) == "B"

    def test_grade_b_for_rct_high_confidence(self) -> None:
        """RCT study design + high confidence → Grade B."""
        pico = PICOExtract(extraction_confidence="high", relevance_score=5)
        assert grade_evidence("RCT", pico) == "B"

    def test_grade_c_for_cohort(self) -> None:
        """Cohort study design → Grade C."""
        pico = PICOExtract(relevance_score=4)
        assert grade_evidence("cohort", pico) == "C"

    def test_grade_c_for_review(self) -> None:
        """Narrative review → Grade C."""
        pico = PICOExtract(relevance_score=4)
        assert grade_evidence("review", pico) == "C"

    def test_grade_d_for_pilot(self) -> None:
        """Pilot study → Grade D."""
        pico = PICOExtract(relevance_score=4)
        assert grade_evidence("pilot", pico) == "D"

    def test_grade_d_for_case_series(self) -> None:
        """Case series → Grade D."""
        pico = PICOExtract(relevance_score=4)
        assert grade_evidence("case_series", pico) == "D"

    def test_expert_opinion_for_low_relevance(self) -> None:
        """relevance_score <= 2 always yields expert_opinion regardless of design."""
        pico = PICOExtract(extraction_confidence="high", relevance_score=2)
        assert grade_evidence("RCT", pico) == "expert_opinion"

    def test_expert_opinion_when_no_study_design(self) -> None:
        """Unknown/None study design with no recognised label → expert_opinion."""
        pico = PICOExtract(relevance_score=4)
        assert grade_evidence(None, pico) == "expert_opinion"

    def test_returns_none_when_both_inputs_none(self) -> None:
        """Both inputs None → returns None (not a string)."""
        assert grade_evidence(None, None) is None


# ===========================================================================
# TestConditionConfigs
# ===========================================================================

class TestConditionConfigs:
    """Tests that CONDITION_CONFIGS covers all 15 Sozo conditions correctly."""

    def test_all_15_conditions_present(self) -> None:
        """CONDITION_CONFIGS must cover all conditions (15 core + any added conditions)."""
        assert len(CONDITION_CONFIGS) == len(ALL_CONDITION_SLUGS)

    def test_all_slugs_have_config(self) -> None:
        """Every slug in ALL_CONDITION_SLUGS must be a key in CONDITION_CONFIGS."""
        for slug in ALL_CONDITION_SLUGS:
            assert slug in CONDITION_CONFIGS, f"Missing config for slug: {slug}"

    def test_condition_config_has_queries(self) -> None:
        """Every config must have at least one openalex_query and one s2_query."""
        for slug, cfg in CONDITION_CONFIGS.items():
            assert len(cfg.openalex_queries) >= 1, f"{slug}: no openalex_queries"
            assert len(cfg.s2_queries) >= 1, f"{slug}: no s2_queries"

    def test_depression_config_has_correct_modalities(self) -> None:
        """Depression config must list tDCS as one of its primary modalities."""
        cfg = CONDITION_CONFIGS["depression"]
        assert "tDCS" in cfg.primary_modalities

    def test_all_configs_have_priority_papers(self) -> None:
        """Every condition config must list at least one priority DOI or PMID."""
        for slug, cfg in CONDITION_CONFIGS.items():
            has_priority = len(cfg.priority_dois) >= 1 or len(cfg.priority_pmids) >= 1
            assert has_priority, f"{slug}: no priority_dois or priority_pmids defined"

    def test_all_condition_slugs_count(self) -> None:
        """ALL_CONDITION_SLUGS must have at least 15 slugs and match CONDITION_CONFIGS."""
        assert len(ALL_CONDITION_SLUGS) >= 15
        assert len(ALL_CONDITION_SLUGS) == len(CONDITION_CONFIGS)

    def test_pipeline_version_is_string(self) -> None:
        """PIPELINE_VERSION is a non-empty string."""
        assert isinstance(PIPELINE_VERSION, str)
        assert len(PIPELINE_VERSION) > 0


# ===========================================================================
# TestDeduplication (standalone test)
# ===========================================================================

def test_deduplication_removes_duplicate_doi(tmp_path: Path, sample_papers: list[PaperRaw]) -> None:
    """Duplicate DOIs from different sources should yield one record."""
    from sozo_generator.evidence.phase8.evidence_ingest import EvidenceIngestor

    ingestor = EvidenceIngestor(output_dir=tmp_path, dry_run=True, skip_llm=True)

    # papers[0] and papers[4] share the same DOI
    with patch.object(ingestor, "_fetch_openalex", return_value=[sample_papers[0]]), \
         patch.object(ingestor, "_fetch_s2", return_value=[sample_papers[4]]), \
         patch.object(ingestor, "_fetch_priority_papers", return_value=[]):
        corpus = ingestor.ingest_condition("depression")

    assert corpus.total_papers_fetched == 1
    assert corpus.total_included == 1


# ===========================================================================
# TestPICOExtractorSchemaValidation
# ===========================================================================

class TestPICOExtractorSchemaValidation:
    """Tests for PICOExtractor LLM response parsing, with mocked LLM calls."""

    def _make_extractor(self, anthropic_api_key: str = "sk-ant-fake") -> PICOExtractor:
        return PICOExtractor(
            anthropic_api_key=anthropic_api_key,
            openai_api_key="sk-fake",
        )

    def _make_paper(self) -> PaperRaw:
        return PaperRaw(
            source="openalex",
            source_id="W001",
            title="tDCS for MDD RCT",
            abstract="Active tDCS reduced HAM-D in MDD.",
        )

    def test_pico_extractor_parses_valid_json(self) -> None:
        """A valid LLM JSON response is parsed into PICOExtract objects without error."""
        extractor = self._make_extractor()
        paper = self._make_paper()

        # Patch _extract_single_batch (the method that calls the LLM and returns
        # parsed dicts) so no real API call is made.
        with patch.object(extractor, "_extract_single_batch",
                          return_value=json.loads(MOCK_LLM_RESPONSE)):
            results = extractor.extract_batch(
                papers=[paper],
                condition_slug="depression",
                condition_name="Major Depressive Disorder",
                primary_modalities=["tDCS", "TMS"],
            )

        assert len(results) == 1
        pico, params = results[0]
        assert isinstance(pico, PICOExtract)
        assert pico.population == "Adults with MDD"
        assert pico.relevance_score == 5
        assert pico.extraction_confidence == "high"
        assert isinstance(params, ProtocolParameters)
        assert params.modality == "tDCS"
        assert params.sessions_total == 20

    def test_pico_extractor_handles_malformed_json(self) -> None:
        """A malformed LLM response returns an empty list and does not raise."""
        extractor = self._make_extractor()
        paper = self._make_paper()

        # _extract_single_batch returns [] when the LLM response cannot be parsed;
        # extract_batch then yields (None, None) per paper rather than crashing.
        with patch.object(extractor, "_extract_single_batch", return_value=[]):
            results = extractor.extract_batch(
                papers=[paper],
                condition_slug="depression",
                condition_name="Major Depressive Disorder",
                primary_modalities=["tDCS"],
            )

        assert len(results) == 1
        assert results[0] == (None, None)

    def test_pico_extractor_marks_irrelevant_below_threshold(self) -> None:
        """A response with relevance_score=1 causes the paper to be marked irrelevant."""
        low_relevance_response = json.dumps([{
            "paper_index": 0,
            "pico": {
                "population": None, "population_n": None,
                "intervention": None, "comparator": None,
                "outcomes_primary": None, "outcomes_secondary": None,
                "result_summary": "This paper has no clinical relevance.",
                "effect_size": None, "p_value": None, "follow_up_weeks": None,
                "conclusion": "Not relevant.", "relevance_score": 1,
                "irrelevant": True,
                "irrelevance_reason": "Basic neuroscience, no neuromodulation.",
                "extraction_confidence": "high",
            },
            "protocol_params": None,
        }])

        extractor = self._make_extractor()
        paper = self._make_paper()

        with patch.object(extractor, "_extract_single_batch",
                          return_value=json.loads(low_relevance_response)):
            results = extractor.extract_batch(
                papers=[paper],
                condition_slug="depression",
                condition_name="Major Depressive Disorder",
                primary_modalities=["tDCS"],
            )

        assert len(results) == 1
        pico, params = results[0]
        assert pico.irrelevant is True
        assert pico.relevance_score == 1
        assert params is None

    def test_pico_extractor_no_api_key_uses_openai_fallback(self) -> None:
        """When anthropic_api_key is empty, the extractor falls back to OpenAI."""
        extractor = self._make_extractor(anthropic_api_key="")
        paper = self._make_paper()

        with patch.object(extractor, "_call_openai", return_value=MOCK_LLM_RESPONSE) as mock_oai, \
             patch.object(extractor, "_call_anthropic", side_effect=AssertionError("should not call anthropic")):
            results = extractor.extract_batch(
                papers=[paper],
                condition_slug="depression",
                condition_name="Major Depressive Disorder",
                primary_modalities=["tDCS"],
            )

        mock_oai.assert_called_once()
        assert len(results) == 1


# ===========================================================================
# TestSavingAndLoading
# ===========================================================================

def test_corpus_saves_and_loads(tmp_path: Path, sample_papers: list[PaperRaw]) -> None:
    """Saved corpus can be loaded and round-trips cleanly."""
    from sozo_generator.evidence.phase8.evidence_ingest import EvidenceIngestor

    ingestor = EvidenceIngestor(output_dir=tmp_path, skip_llm=True, dry_run=True)

    with patch.object(ingestor, "_fetch_openalex", return_value=[sample_papers[0]]), \
         patch.object(ingestor, "_fetch_s2", return_value=[]), \
         patch.object(ingestor, "_fetch_priority_papers", return_value=[]):
        corpus = ingestor.ingest_condition("depression")

    # Both output files must exist
    assert (tmp_path / "depression.json").exists()
    assert (tmp_path / "depression_summary.json").exists()

    # Load cached corpus — should not re-fetch
    cached = ingestor._load_cached_corpus("depression")
    assert cached is not None
    assert cached.condition_slug == "depression"
    assert cached.total_papers_fetched == corpus.total_papers_fetched
