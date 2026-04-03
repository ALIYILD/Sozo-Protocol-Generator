"""
Tests for the PRISMA-style research/evidence pipeline.

Tests cover:
- Fuzzy deduplication (PMID, DOI, title similarity)
- Screening service (keyword-based include/exclude)
- Parameter extraction (regex patterns)
- Evidence scoring (multi-dimensional)
- Citation grounding (claim-level)
- Pipeline tracker (PRISMA audit trail)
- PRISMA diagram generation
"""
import pytest
from sozo_generator.schemas.evidence import ArticleMetadata
from sozo_generator.core.enums import EvidenceType, EvidenceLevel


# ── Fixtures ───────────────────────────────────────────────────────────


def _make_article(
    pmid=None, doi=None, title="Test Article", abstract=None,
    evidence_type=EvidenceType.RCT, evidence_level=EvidenceLevel.HIGH,
    year=2024, authors=None, journal="Brain Stimulation",
    modalities=None, condition_slug=None, score=4,
):
    return ArticleMetadata(
        pmid=pmid,
        doi=doi,
        title=title,
        abstract=abstract,
        evidence_type=evidence_type,
        evidence_level=evidence_level,
        year=year,
        authors=authors or ["Smith AB", "Jones CD"],
        journal=journal,
        modalities=modalities or [],
        condition_slug=condition_slug,
        score=score,
    )


# ── Fuzzy Deduplication ───────────────────────────────────────────────


class TestFuzzyDedup:
    def test_pmid_dedup(self):
        from sozo_generator.evidence.fuzzy_dedup import fuzzy_deduplicate

        articles = [
            _make_article(pmid="12345678", title="Transcranial direct current stimulation for depression"),
            _make_article(pmid="12345678", title="Transcranial direct current stimulation for depression (copy)"),
            _make_article(pmid="87654321", title="Repetitive TMS for chronic pain management in elderly"),
        ]
        result = fuzzy_deduplicate(articles)
        assert len(result.unique_articles) == 2
        assert result.duplicates_removed == 1
        assert result.method_counts["pmid"] == 1

    def test_doi_dedup(self):
        from sozo_generator.evidence.fuzzy_dedup import fuzzy_deduplicate

        articles = [
            _make_article(doi="10.1001/test.123", title="Transcranial direct current stimulation for depression"),
            _make_article(doi="10.1001/test.123", title="Transcranial direct current stimulation for depression from crossref"),
            _make_article(doi="10.1001/other.456", title="Repetitive TMS for chronic pain management in elderly"),
        ]
        result = fuzzy_deduplicate(articles)
        assert len(result.unique_articles) == 2
        assert result.method_counts["doi"] == 1

    def test_title_fuzzy_dedup(self):
        from sozo_generator.evidence.fuzzy_dedup import fuzzy_deduplicate

        articles = [
            _make_article(title="Transcranial direct current stimulation for depression: a systematic review"),
            _make_article(title="Transcranial direct current stimulation for depression a systematic review"),
        ]
        result = fuzzy_deduplicate(articles)
        assert len(result.unique_articles) == 1
        assert result.method_counts["title"] == 1

    def test_no_false_positives(self):
        from sozo_generator.evidence.fuzzy_dedup import fuzzy_deduplicate

        articles = [
            _make_article(title="tDCS for depression: a systematic review"),
            _make_article(title="rTMS for chronic pain: randomized controlled trial"),
        ]
        result = fuzzy_deduplicate(articles)
        assert len(result.unique_articles) == 2
        assert result.duplicates_removed == 0

    def test_metadata_merge_fills_gaps(self):
        from sozo_generator.evidence.fuzzy_dedup import fuzzy_deduplicate

        articles = [
            _make_article(pmid="12345678", title="Study A", abstract=None),
            _make_article(pmid="12345678", title="Study A", abstract="Has an abstract now."),
        ]
        result = fuzzy_deduplicate(articles)
        assert len(result.unique_articles) == 1
        assert result.unique_articles[0].abstract == "Has an abstract now."


class TestTitleSimilarity:
    def test_identical(self):
        from sozo_generator.evidence.fuzzy_dedup import title_similarity
        assert title_similarity("hello world", "hello world") == 1.0

    def test_similar(self):
        from sozo_generator.evidence.fuzzy_dedup import title_similarity
        sim = title_similarity(
            "tDCS for major depression: a review",
            "tDCS for major depression a review",
        )
        assert sim > 0.9

    def test_different(self):
        from sozo_generator.evidence.fuzzy_dedup import title_similarity
        sim = title_similarity(
            "tDCS for depression",
            "rTMS for chronic pain in elderly patients",
        )
        assert sim < 0.5


# ── Screening Service ──────────────────────────────────────────────────


class TestScreening:
    def test_include_neuromodulation_paper(self):
        from sozo_generator.evidence.screening import ScreeningService

        service = ScreeningService()
        article = _make_article(
            title="Transcranial direct current stimulation for depression",
            abstract="This RCT evaluated tDCS at 2 mA for 20 minutes over "
                     "left DLPFC. 30 sessions were delivered over 6 weeks. "
                     "Sham-controlled with electrode montage F3-Fp2.",
        )
        result = service.screen(article)
        assert result.decision == "include"
        assert len(result.inclusion_signals) >= 2

    def test_exclude_animal_study(self):
        from sozo_generator.evidence.screening import ScreeningService

        service = ScreeningService()
        article = _make_article(
            title="Effects of electrical stimulation in rat model of depression",
            abstract="We used a rat model to investigate hippocampal plasticity. "
                     "Animal model experiments with rodent subjects showed "
                     "changes in synaptic activity after cortical manipulation.",
        )
        result = service.screen(article)
        assert result.decision == "exclude"

    def test_uncertain_for_borderline(self):
        from sozo_generator.evidence.screening import ScreeningService

        service = ScreeningService()
        article = _make_article(
            title="Brain stimulation approaches for neurological disorders",
            abstract="General overview of approaches.",
        )
        result = service.screen(article)
        assert result.decision in ("uncertain", "include")


# ── Parameter Extraction ───────────────────────────────────────────────


class TestParameterExtraction:
    def test_extract_tdcs_parameters(self):
        from sozo_generator.evidence.parameter_extractor import ParameterExtractor

        extractor = ParameterExtractor()
        article = _make_article(
            title="tDCS for depression targeting left DLPFC",
            abstract="Anodal tDCS was applied at 2 mA for 20 minutes per session. "
                     "Participants received 15 sessions over 3 weeks (5 sessions per week). "
                     "The cathode was placed over right supraorbital area. "
                     "Depression severity was measured using HDRS. "
                     "Cohen's d = 0.82, p = 0.003.",
        )
        result = extractor.extract(article)
        params = result.parameters

        assert params is not None
        assert params.modality == "tDCS"
        assert params.brain_target == "DLPFC"
        assert params.intensity_ma == 2.0
        assert params.duration_minutes == 20.0
        assert params.sessions_total == 15
        assert params.sessions_per_week == 5
        assert params.primary_outcome_measure == "HDRS"
        assert params.effect_size_d == 0.82
        assert params.p_value == 0.003
        assert params.fields_extracted >= 8

    def test_extract_rtms_parameters(self):
        from sozo_generator.evidence.parameter_extractor import ParameterExtractor

        extractor = ParameterExtractor()
        article = _make_article(
            title="Repetitive transcranial magnetic stimulation for Parkinson's disease",
            abstract="rTMS was delivered at 10 Hz over left M1 at 120% of resting "
                     "motor threshold. Each session included 3000 pulses. "
                     "Outcomes were measured using MDS-UPDRS.",
        )
        result = extractor.extract(article)
        params = result.parameters

        assert params is not None
        assert params.modality == "rTMS"
        assert params.brain_target == "M1"
        assert params.frequency_hz == 10.0
        assert params.motor_threshold_pct == 120
        assert params.pulses_per_session == 3000

    def test_empty_abstract(self):
        from sozo_generator.evidence.parameter_extractor import ParameterExtractor

        extractor = ParameterExtractor()
        article = _make_article(title="Short title", abstract=None)
        result = extractor.extract(article)
        assert result.parameters is None or result.parameters.fields_extracted == 0


# ── Evidence Scoring ───────────────────────────────────────────────────


class TestEvidenceScoring:
    def test_rct_scores_higher_than_case_report(self):
        from sozo_generator.evidence.evidence_scorer import EvidenceScorer

        scorer = EvidenceScorer()
        rct = _make_article(
            evidence_type=EvidenceType.RCT,
            evidence_level=EvidenceLevel.HIGH,
        )
        case = _make_article(
            evidence_type=EvidenceType.CASE_REPORT,
            evidence_level=EvidenceLevel.VERY_LOW,
        )
        rct_quality = scorer.score_quality(rct)
        case_quality = scorer.score_quality(case)

        assert rct_quality.composite_score > case_quality.composite_score
        assert rct_quality.design_score > case_quality.design_score

    def test_meta_analysis_gets_grade_a(self):
        from sozo_generator.evidence.evidence_scorer import EvidenceScorer

        scorer = EvidenceScorer()
        meta = _make_article(
            evidence_type=EvidenceType.META_ANALYSIS,
            evidence_level=EvidenceLevel.HIGHEST,
            abstract="This meta-analysis of 15 double-blind randomized controlled "
                     "trials with sham control demonstrates...",
        )
        quality = scorer.score_quality(meta)
        assert quality.evidence_grade in ("A", "B")

    def test_relevance_scoring(self):
        from sozo_generator.evidence.evidence_scorer import EvidenceScorer
        from sozo_generator.evidence.parameter_extractor import StimulationParameters

        scorer = EvidenceScorer()
        article = _make_article(
            condition_slug="depression",
            year=2024,
        )
        extraction = StimulationParameters(
            modality="tDCS",
            brain_target="DLPFC",
        )
        relevance = scorer.score_relevance(
            article, extraction,
            target_modality="tDCS",
            target_condition="depression",
            target_brain_region="DLPFC",
        )
        assert relevance.composite_score > 50  # high relevance
        assert relevance.parameter_match > 0.5


# ── Pipeline Tracker ───────────────────────────────────────────────────


class TestPipelineTracker:
    def test_log_events(self):
        from sozo_generator.evidence.pipeline_tracker import (
            PipelineTracker, PipelineStage, PipelineDecision,
        )

        tracker = PipelineTracker()
        tracker.log_identification("PMID:12345678", "pubmed")
        tracker.log_identification("DOI:10.1001/test", "crossref")
        tracker.log_dedup("PMID:12345678", is_duplicate=False)
        tracker.log_dedup("DOI:10.1001/test", merged_into="PMID:12345678")
        tracker.log_screening(
            "PMID:12345678",
            PipelineDecision.INCLUDE,
            "Neuromodulation content with protocol details",
            confidence=0.85,
        )

        assert tracker.event_count == 5
        counts = tracker.get_prisma_counts()
        assert counts.records_identified == 2
        assert counts.duplicates_removed == 1
        assert counts.records_after_dedup == 1
        assert counts.records_screened == 1

    def test_study_trace(self):
        from sozo_generator.evidence.pipeline_tracker import (
            PipelineTracker, PipelineStage, PipelineDecision,
        )

        tracker = PipelineTracker()
        tracker.log_identification("PMID:12345678", "pubmed")
        tracker.log_dedup("PMID:12345678", is_duplicate=False)
        tracker.log_screening(
            "PMID:12345678", PipelineDecision.INCLUDE, "Relevant",
        )

        events = tracker.get_events_for_study("PMID:12345678")
        assert len(events) == 3
        stages = [e.stage for e in events]
        assert "identification" in stages
        assert "deduplication" in stages
        assert "screening" in stages


# ── PRISMA Diagram ─────────────────────────────────────────────────────


class TestPRISMADiagram:
    def test_generates_text_diagram(self):
        from sozo_generator.evidence.pipeline_tracker import (
            PipelineTracker, PipelineDecision,
        )
        from sozo_generator.evidence.prisma_diagram import PRISMADiagramGenerator

        tracker = PipelineTracker()
        # Simulate a small pipeline
        for i in range(10):
            tracker.log_identification(f"study-{i}", "pubmed")
        for i in range(8):
            tracker.log_dedup(f"study-{i}", is_duplicate=False)
        tracker.log_dedup("study-8", merged_into="study-0")
        tracker.log_dedup("study-9", merged_into="study-1")
        for i in range(6):
            tracker.log_screening(
                f"study-{i}", PipelineDecision.INCLUDE, "Relevant",
            )
        for i in range(6, 8):
            tracker.log_screening(
                f"study-{i}", PipelineDecision.EXCLUDE, "Not neuromodulation",
            )

        gen = PRISMADiagramGenerator()
        diagram = gen.generate(tracker, "depression", "Major Depressive Disorder")

        assert "PRISMA 2020" in diagram.text_diagram
        assert "IDENTIFICATION" in diagram.text_diagram
        assert "SCREENING" in diagram.text_diagram
        assert "INCLUDED" in diagram.text_diagram
        assert diagram.counts.records_identified == 10
        assert diagram.counts.duplicates_removed == 2

    def test_generates_mermaid(self):
        from sozo_generator.evidence.pipeline_tracker import PipelineTracker
        from sozo_generator.evidence.prisma_diagram import PRISMADiagramGenerator

        tracker = PipelineTracker()
        tracker.log_identification("study-1", "pubmed")

        gen = PRISMADiagramGenerator()
        diagram = gen.generate(tracker)

        assert "graph TD" in diagram.mermaid_diagram
        assert "Records identified" in diagram.mermaid_diagram


# ── Citation Grounding ─────────────────────────────────────────────────


class TestCitationGrounding:
    def test_grounds_claim_to_evidence(self):
        from sozo_generator.evidence.citation_grounding import CitationGroundingService
        from sozo_generator.evidence.evidence_scorer import EvidenceScore, QualityScore, RelevanceScore
        from sozo_generator.evidence.parameter_extractor import StimulationParameters

        service = CitationGroundingService()

        article = _make_article(
            pmid="12345678",
            title="tDCS at 2 mA over left DLPFC for depression",
            abstract="Anodal tDCS was applied at 2 mA for 20 minutes over left DLPFC. "
                     "The treatment significantly improved HDRS scores (p<0.01).",
        )
        params = StimulationParameters(
            modality="tDCS",
            brain_target="DLPFC",
            intensity_ma=2.0,
            duration_minutes=20.0,
        )
        score = EvidenceScore(
            study_identifier="12345678",
            quality=QualityScore(composite_score=75, evidence_grade="A"),
            relevance=RelevanceScore(composite_score=80),
            final_grade="A",
            final_score=78,
        )

        evidence_pool = [(article, params, score)]

        grounded = service.ground_section(
            section_id="stim_params",
            section_title="Stimulation Parameters",
            section_text="Apply 2 mA anodal tDCS over left DLPFC for 20 minutes per session.",
            evidence_pool=evidence_pool,
        )

        assert grounded.total_citations >= 1
        assert grounded.claims[0].citations[0].study_identifier == "12345678"
        assert grounded.claims[0].citations[0].evidence_grade == "A"

    def test_flags_unsupported_claims(self):
        from sozo_generator.evidence.citation_grounding import CitationGroundingService

        service = CitationGroundingService()

        grounded = service.ground_section(
            section_id="test",
            section_title="Test",
            section_text="Apply novel stimulation protocol at 5 mA.",
            evidence_pool=[],  # no evidence
        )

        assert grounded.claims[0].unsupported is True
        assert grounded.needs_review is True


# ── Multi-Source Search (unit, no network) ─────────────────────────────


class TestMultiSourceSearch:
    def test_cross_source_dedup(self):
        from sozo_generator.evidence.multi_source_search import MultiSourceSearch

        # Test the static dedup method directly
        articles = [
            _make_article(pmid="12345678", doi="10.1001/a", title="Study A"),
            _make_article(pmid=None, doi="10.1001/a", title="Study A from Crossref"),
            _make_article(pmid="12345678", doi=None, title="Study A from S2"),
            _make_article(pmid="99999999", doi="10.1001/b", title="Study B"),
        ]
        unique = MultiSourceSearch._deduplicate_cross_source(articles)
        assert len(unique) == 2
