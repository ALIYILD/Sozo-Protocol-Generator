"""
Unified research pipeline — orchestrates the full PRISMA-style evidence
workflow from search through grounding.

Pipeline stages:
1. Multi-source search (PubMed + Crossref + Semantic Scholar)
2. Fuzzy deduplication (PMID + DOI + title similarity)
3. Screening (keyword heuristics, optional LLM)
4. Parameter extraction (regex-based structured extraction)
5. Evidence scoring (multi-dimensional quality + relevance)
6. Citation grounding (claim-level trace to evidence)

All decisions are tracked in the PipelineTracker for PRISMA compliance.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..core.enums import ClaimCategory
from ..core.settings import get_settings
from ..schemas.evidence import ArticleMetadata
from ..schemas.condition import ConditionSchema

from .multi_source_search import MultiSourceSearch, MultiSourceResult
from .fuzzy_dedup import fuzzy_deduplicate, FuzzyDedupResult
from .screening import ScreeningService, BatchScreeningResult
from .parameter_extractor import ParameterExtractor, ExtractionResult, StimulationParameters
from .evidence_scorer import EvidenceScorer, EvidenceScore
from .citation_grounding import CitationGroundingService, GroundedSection
from .pipeline_tracker import (
    PipelineTracker, PipelineStage, PipelineDecision, PRISMAFlowCounts,
)
from .query_planner import QueryPlanner, QueryPlan

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Complete result of the research pipeline for one condition."""

    condition_slug: str = ""
    condition_name: str = ""
    started_at: str = ""
    completed_at: str = ""

    # Stage results
    search_result: Optional[MultiSourceResult] = None
    dedup_result: Optional[FuzzyDedupResult] = None
    screening_result: Optional[BatchScreeningResult] = None
    extractions: list[ExtractionResult] = field(default_factory=list)
    evidence_scores: list[EvidenceScore] = field(default_factory=list)

    # Processed data
    included_articles: list[ArticleMetadata] = field(default_factory=list)
    evidence_pool: list[tuple] = field(default_factory=list)  # (article, params, score)

    # PRISMA
    prisma_counts: Optional[PRISMAFlowCounts] = None
    pipeline_log_path: Optional[str] = None

    # Stats
    total_identified: int = 0
    total_after_dedup: int = 0
    total_after_screening: int = 0
    total_extracted: int = 0
    total_scored: int = 0
    errors: list[str] = field(default_factory=list)


class ResearchPipeline:
    """Full PRISMA-style evidence pipeline for neuromodulation protocols.

    Usage:
        pipeline = ResearchPipeline()
        result = pipeline.run(condition_schema)

        # Or step-by-step:
        pipeline = ResearchPipeline()
        pipeline.search(condition_schema)
        pipeline.deduplicate()
        pipeline.screen()
        pipeline.extract()
        pipeline.score(target_modality="tDCS", target_condition="depression")
    """

    def __init__(
        self,
        use_pubmed: bool = True,
        use_crossref: bool = True,
        use_semantic_scholar: bool = True,
        max_results_per_source: int = 30,
        years_back: int = 10,
        force_refresh: bool = False,
        persist_dir: Optional[Path] = None,
    ):
        settings = get_settings()
        self._search = MultiSourceSearch(
            use_pubmed=use_pubmed,
            use_crossref=use_crossref,
            use_semantic_scholar=use_semantic_scholar,
            force_refresh=force_refresh,
        )
        self._extractor = ParameterExtractor()
        self._scorer = EvidenceScorer()
        self._grounder = CitationGroundingService()
        self._query_planner = QueryPlanner()

        self._max_results = max_results_per_source
        self._years_back = years_back

        self._tracker = PipelineTracker(
            persist_dir=persist_dir or settings.evidence_dir / "pipeline_logs",
        )

        # Internal state
        self._all_articles: list[ArticleMetadata] = []
        self._unique_articles: list[ArticleMetadata] = []
        self._screened_articles: list[ArticleMetadata] = []
        self._extractions: dict[str, ExtractionResult] = {}  # identifier → result
        self._scores: dict[str, EvidenceScore] = {}  # identifier → score

    @property
    def tracker(self) -> PipelineTracker:
        return self._tracker

    def run(
        self,
        condition: ConditionSchema,
        target_modality: Optional[str] = None,
        target_brain_region: Optional[str] = None,
    ) -> PipelineResult:
        """Run the full pipeline for a condition.

        Args:
            condition: The condition schema with metadata
            target_modality: Filter for specific modality (e.g. "tDCS")
            target_brain_region: Filter for brain target (e.g. "DLPFC")
        """
        result = PipelineResult(
            condition_slug=condition.slug,
            condition_name=condition.display_name,
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        try:
            # 1. Search
            self.search(condition)
            result.total_identified = len(self._all_articles)

            # 2. Deduplicate
            self.deduplicate()
            result.total_after_dedup = len(self._unique_articles)

            # 3. Screen
            self.screen(
                target_condition=condition.slug,
                target_modality=target_modality,
            )
            result.total_after_screening = len(self._screened_articles)

            # 4. Extract parameters
            self.extract()
            result.total_extracted = sum(
                1 for e in self._extractions.values()
                if e.parameters and e.parameters.fields_extracted > 0
            )

            # 5. Score evidence
            self.score(
                target_modality=target_modality,
                target_condition=condition.slug,
                target_brain_region=target_brain_region,
            )
            result.total_scored = len(self._scores)

            # Assemble results
            result.included_articles = list(self._screened_articles)
            result.extractions = list(self._extractions.values())
            result.evidence_scores = list(self._scores.values())

            # Build evidence pool for grounding
            result.evidence_pool = self._build_evidence_pool()

            # PRISMA counts
            result.prisma_counts = self._tracker.get_prisma_counts()

            # Persist pipeline log
            log_path = self._tracker.persist(condition.slug)
            if log_path:
                result.pipeline_log_path = str(log_path)

        except Exception as e:
            logger.error("Pipeline failed for %s: %s", condition.slug, e, exc_info=True)
            result.errors.append(str(e))

        result.completed_at = datetime.now(timezone.utc).isoformat()

        logger.info(
            "Pipeline complete for %s: %d identified → %d deduped → "
            "%d screened → %d extracted → %d scored",
            condition.slug,
            result.total_identified,
            result.total_after_dedup,
            result.total_after_screening,
            result.total_extracted,
            result.total_scored,
        )
        return result

    def search(self, condition: ConditionSchema) -> None:
        """Stage 1: Multi-source search using query planner."""
        # Build query plan
        networks = [np.network for np in condition.network_profiles]
        modalities_enum = [
            st.modality for st in condition.stimulation_targets
        ]
        symptoms = condition.core_symptoms[:5]

        plan = self._query_planner.plan_condition(
            condition_slug=condition.slug,
            display_name=condition.display_name,
            icd10=condition.icd10,
            networks=networks,
            modalities=modalities_enum,
            symptoms=symptoms,
        )

        # Execute searches across all sources
        self._all_articles = []
        for query_spec in plan.queries:
            search_result = self._search.search(
                query=query_spec.query_string,
                max_results_per_source=min(self._max_results, query_spec.max_results),
                years_back=query_spec.years_back or self._years_back,
            )

            # Tag articles with category and condition
            for article in search_result.articles:
                article.condition_slug = condition.slug
                article.claim_categories = [query_spec.category]

                # Log identification
                identifier = article.pmid or article.doi or article.title[:50]
                source = "multi" if len(search_result.source_counts) > 1 else (
                    list(search_result.source_counts.keys())[0]
                    if search_result.source_counts else "unknown"
                )
                self._tracker.log_identification(identifier, source)

            self._all_articles.extend(search_result.articles)

        logger.info(
            "Search complete: %d total articles from %d queries",
            len(self._all_articles), len(plan.queries),
        )

    def deduplicate(self) -> None:
        """Stage 2: Cross-source fuzzy deduplication."""
        dedup_result = fuzzy_deduplicate(
            self._all_articles,
            tracker=self._tracker,
        )
        self._unique_articles = dedup_result.unique_articles

    def screen(
        self,
        target_condition: Optional[str] = None,
        target_modality: Optional[str] = None,
    ) -> None:
        """Stage 3: Keyword-based screening."""
        screener = ScreeningService(
            target_condition=target_condition,
            target_modality=target_modality,
        )
        self._screened_articles = screener.get_included(
            self._unique_articles, tracker=self._tracker,
        )

    def extract(self) -> None:
        """Stage 4: Parameter extraction."""
        self._extractions = {}
        for article in self._screened_articles:
            identifier = article.pmid or article.doi or article.title[:50]
            extraction_result = self._extractor.extract(article)
            self._extractions[identifier] = extraction_result

            # Log extraction
            if extraction_result.parameters and extraction_result.parameters.fields_extracted > 0:
                self._tracker.log(
                    study_identifier=identifier,
                    stage=PipelineStage.EXTRACTION,
                    decision=PipelineDecision.EXTRACTED,
                    reason=f"{extraction_result.parameters.fields_extracted} fields extracted",
                    confidence=extraction_result.parameters.extraction_confidence,
                    decided_by="system:regex_extractor",
                )

    def score(
        self,
        target_modality: Optional[str] = None,
        target_condition: Optional[str] = None,
        target_brain_region: Optional[str] = None,
    ) -> None:
        """Stage 5: Multi-dimensional evidence scoring."""
        self._scores = {}
        for article in self._screened_articles:
            identifier = article.pmid or article.doi or article.title[:50]
            extraction = self._extractions.get(identifier)
            params = extraction.parameters if extraction else None

            ev_score = self._scorer.score_full(
                article=article,
                extraction=params,
                target_modality=target_modality,
                target_condition=target_condition,
                target_brain_region=target_brain_region,
            )
            self._scores[identifier] = ev_score

            # Log scoring
            self._tracker.log(
                study_identifier=identifier,
                stage=PipelineStage.SCORING,
                decision=PipelineDecision.SCORED,
                reason=f"Grade {ev_score.final_grade}, score {ev_score.final_score}",
                confidence=ev_score.final_score / 100.0,
                decided_by="system:evidence_scorer",
            )

    def ground_section(
        self,
        section_id: str,
        section_title: str,
        section_text: str,
        category: Optional[ClaimCategory] = None,
    ) -> GroundedSection:
        """Stage 6: Ground a protocol section's claims to evidence."""
        evidence_pool = self._build_evidence_pool()
        grounded = self._grounder.ground_section(
            section_id=section_id,
            section_title=section_title,
            section_text=section_text,
            evidence_pool=evidence_pool,
            category=category,
        )

        # Log grounding
        for claim in grounded.claims:
            for cit in claim.citations:
                self._tracker.log(
                    study_identifier=cit.study_identifier,
                    stage=PipelineStage.GROUNDING,
                    decision=PipelineDecision.GROUNDED,
                    reason=f"Cited for: {claim.claim_text[:60]}",
                    decided_by="system:citation_grounder",
                    metadata={
                        "citation_type": cit.citation_type,
                        "evidence_grade": cit.evidence_grade,
                        "section_id": section_id,
                    },
                )

        return grounded

    def _build_evidence_pool(
        self,
    ) -> list[tuple[ArticleMetadata, Optional[StimulationParameters], Optional[EvidenceScore]]]:
        """Build the evidence pool for citation grounding."""
        pool = []
        for article in self._screened_articles:
            identifier = article.pmid or article.doi or article.title[:50]
            extraction = self._extractions.get(identifier)
            params = extraction.parameters if extraction else None
            score = self._scores.get(identifier)
            pool.append((article, params, score))

        # Sort by score (best evidence first)
        pool.sort(
            key=lambda x: x[2].final_score if x[2] else 0,
            reverse=True,
        )
        return pool

    def get_top_evidence(
        self, n: int = 20, min_grade: str = "D",
    ) -> list[tuple[ArticleMetadata, Optional[EvidenceScore]]]:
        """Get top-N scored articles, optionally filtered by grade."""
        grade_order = {"A": 4, "B": 3, "C": 2, "D": 1}
        min_grade_val = grade_order.get(min_grade, 0)

        pool = []
        for article in self._screened_articles:
            identifier = article.pmid or article.doi or article.title[:50]
            score = self._scores.get(identifier)
            if score and grade_order.get(score.final_grade, 0) >= min_grade_val:
                pool.append((article, score))

        pool.sort(key=lambda x: x[1].final_score if x[1] else 0, reverse=True)
        return pool[:n]
