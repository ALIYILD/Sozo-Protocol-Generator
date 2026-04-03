"""
evidence_search — multi-source search using the existing ResearchPipeline.

Type: Deterministic
Wraps: sozo_generator.evidence.research_pipeline.ResearchPipeline
"""
from __future__ import annotations

import logging

from ..audit.logger import audited_node
from ..state import SozoGraphState

logger = logging.getLogger(__name__)


@audited_node("evidence_search")
def evidence_search(state: SozoGraphState) -> dict:
    """Execute multi-source evidence search for the resolved condition."""
    decisions = []
    condition = state.get("condition", {})

    if not condition.get("condition_valid"):
        decisions.append("Skipping evidence search — condition not valid")
        return {
            "evidence": {
                "raw_article_count": 0,
                "evidence_sufficient": False,
                "evidence_gaps": ["Condition not resolved"],
            },
            "status": "evidence",
            "_decisions": decisions,
        }

    # Reconstruct ConditionSchema from serialized dict
    from sozo_generator.schemas.condition import ConditionSchema
    schema = ConditionSchema(**condition["schema_dict"])

    # Run the pipeline search + dedup + screen + extract + score
    from sozo_generator.evidence.research_pipeline import ResearchPipeline
    from sozo_generator.core.settings import get_settings

    settings = get_settings()
    pipeline = ResearchPipeline(
        use_pubmed=True,
        use_crossref=settings.use_crossref,
        use_semantic_scholar=settings.use_semantic_scholar,
        persist_dir=settings.pipeline_logs_dir,
    )

    # Determine target modality from condition's stimulation targets
    target_modality = None
    if schema.stimulation_targets:
        target_modality = schema.stimulation_targets[0].modality.value

    result = pipeline.run(
        condition=schema,
        target_modality=target_modality,
    )

    decisions.append(
        f"Search complete: {result.total_identified} identified → "
        f"{result.total_after_dedup} deduped → {result.total_after_screening} screened → "
        f"{result.total_extracted} extracted → {result.total_scored} scored"
    )

    # Serialize articles for state
    serialized_articles = []
    for article, ev_score in pipeline.get_top_evidence(n=50):
        serialized_articles.append({
            "pmid": article.pmid,
            "doi": article.doi,
            "title": article.title,
            "authors": article.authors,
            "journal": article.journal,
            "year": article.year,
            "abstract": article.abstract,
            "evidence_type": article.evidence_type.value,
            "evidence_level": article.evidence_level.value,
            "score": article.score,
            "evidence_grade": ev_score.final_grade if ev_score else "D",
            "quality_score": ev_score.quality.composite_score if ev_score and ev_score.quality else 0,
            "relevance_score": ev_score.relevance.composite_score if ev_score and ev_score.relevance else 0,
        })

    # Evidence sufficiency check
    grade_a_count = sum(1 for a in serialized_articles if a.get("evidence_grade") == "A")
    grade_b_count = sum(1 for a in serialized_articles if a.get("evidence_grade") == "B")
    evidence_sufficient = (grade_a_count + grade_b_count) >= 1

    decisions.append(
        f"Evidence grades: A={grade_a_count}, B={grade_b_count} → "
        f"sufficient={evidence_sufficient}"
    )

    prisma = result.prisma_counts.__dict__ if result.prisma_counts else {}

    return {
        "evidence": {
            "search_queries": [q.query_string for q in pipeline._query_planner.plan_condition(
                schema.slug, schema.display_name, schema.icd10,
            ).queries[:5]] if hasattr(pipeline, '_query_planner') else [],
            "source_counts": result.search_result.source_counts if result.search_result else {},
            "raw_article_count": result.total_identified,
            "unique_article_count": result.total_after_dedup,
            "screened_article_count": result.total_after_screening,
            "articles": serialized_articles,
            "evidence_summary": {
                "total_articles": len(serialized_articles),
                "grade_distribution": {
                    "A": grade_a_count,
                    "B": grade_b_count,
                    "C": sum(1 for a in serialized_articles if a.get("evidence_grade") == "C"),
                    "D": sum(1 for a in serialized_articles if a.get("evidence_grade") == "D"),
                },
            },
            "evidence_sufficient": evidence_sufficient,
            "evidence_gaps": result.errors or [],
            "prisma_counts": prisma,
            "pipeline_log_path": result.pipeline_log_path,
        },
        "status": "evidence",
        "_decisions": decisions,
    }
