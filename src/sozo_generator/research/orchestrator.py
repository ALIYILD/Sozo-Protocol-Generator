"""
Research Orchestrator — section-level evidence gathering from multiple sources.

Gathers evidence for each section of a template-driven document using:
1. Internal condition data (ConditionSchema) — highest priority
2. PubMed / literature search — clinical evidence
3. Content library (harvested from existing documents) — proven content
4. Evidence profiles (curated YAML) — pre-verified evidence

The orchestrator does NOT fabricate evidence. It retrieves, ranks, and
summarizes real sources for the section writer to use.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from ..template_profiles.models import (
    ResearchBundle,
    ResearchSource,
    TemplateSectionSpec,
)

logger = logging.getLogger(__name__)

# ── Section → search query templates ──────────────────────────────────────

_SECTION_QUERY_TEMPLATES = {
    "overview": [
        "{condition} clinical overview neuromodulation",
        "{condition} epidemiology prevalence treatment",
    ],
    "pathophysiology": [
        "{condition} pathophysiology neural mechanism",
        "{condition} brain circuit dysfunction",
    ],
    "brain_structure": [
        "{condition} brain regions affected neuroimaging",
        "{condition} structural changes MRI",
    ],
    "network": [
        "{condition} functional brain network fMRI connectivity",
        "{condition} default mode network salience network",
    ],
    "phenotype": [
        "{condition} clinical subtypes phenotype classification",
    ],
    "protocol": [
        "{condition} transcranial direct current stimulation tDCS",
        "{condition} neuromodulation stimulation protocol parameters",
    ],
    "tps": [
        "{condition} transcranial pulse stimulation ultrasound neuromodulation",
    ],
    "tdcs": [
        "{condition} tDCS electrode montage clinical trial",
    ],
    "safety": [
        "{condition} neuromodulation safety adverse effects contraindications",
    ],
    "assessment": [
        "{condition} clinical assessment scales outcome measures",
    ],
    "responder": [
        "{condition} treatment response criteria neuromodulation",
    ],
    "inclusion": [
        "{condition} clinical trial inclusion exclusion criteria neuromodulation",
    ],
}


class ResearchOrchestrator:
    """Orchestrates multi-source evidence gathering for template-driven generation.

    Usage:
        orchestrator = ResearchOrchestrator()
        bundle = orchestrator.research_section(
            condition_slug="depression",
            condition_name="Major Depressive Disorder",
            section_spec=template_section,
        )
    """

    def __init__(
        self,
        use_pubmed: bool = True,
        use_content_library: bool = True,
        use_evidence_profiles: bool = True,
    ):
        self.use_pubmed = use_pubmed
        self.use_content_library = use_content_library
        self.use_evidence_profiles = use_evidence_profiles

    def research_section(
        self,
        condition_slug: str,
        condition_name: str,
        section_spec: TemplateSectionSpec,
        max_sources: int = 10,
    ) -> ResearchBundle:
        """Gather evidence for a single template section.

        Returns a ResearchBundle with sources ranked by relevance and quality.
        """
        bundle = ResearchBundle(
            condition_slug=condition_slug,
            section_id=section_spec.section_id,
        )

        # 1. Internal condition data
        internal = self._get_internal_evidence(condition_slug, section_spec)
        bundle.sources.extend(internal)

        # 2. Evidence profiles (pre-curated)
        if self.use_evidence_profiles:
            profile_sources = self._get_evidence_profile_sources(condition_slug, section_spec)
            bundle.sources.extend(profile_sources)

        # 3. Content library (harvested content)
        if self.use_content_library:
            library_sources = self._get_content_library_sources(condition_slug, section_spec)
            bundle.sources.extend(library_sources)

        # 4. PubMed search
        if self.use_pubmed and section_spec.requires_evidence:
            queries = self._build_queries(condition_name, section_spec)
            bundle.query_set = queries
            pubmed_sources = self._search_pubmed(queries, max_results=max_sources)
            bundle.sources.extend(pubmed_sources)

        # Deduplicate by PMID
        bundle.sources = self._deduplicate(bundle.sources)

        # Sort by relevance
        bundle.sources.sort(key=lambda s: -s.relevance_score)
        bundle.sources = bundle.sources[:max_sources]

        # Build summary
        bundle.evidence_summary = self._summarize(bundle)
        bundle.confidence = self._assess_confidence(bundle)

        logger.debug(
            f"Research for {condition_slug}/{section_spec.section_id}: "
            f"{len(bundle.sources)} sources, confidence={bundle.confidence}"
        )
        return bundle

    def research_all_sections(
        self,
        condition_slug: str,
        condition_name: str,
        sections: list[TemplateSectionSpec],
    ) -> dict[str, ResearchBundle]:
        """Research all sections of a template."""
        bundles = {}
        for section in sections:
            bundle = self.research_section(
                condition_slug, condition_name, section
            )
            bundles[section.section_id] = bundle
        return bundles

    def _get_internal_evidence(
        self, condition_slug: str, section: TemplateSectionSpec
    ) -> list[ResearchSource]:
        """Get evidence from internal ConditionSchema."""
        sources = []
        try:
            from ..conditions.registry import get_registry
            registry = get_registry()
            if not registry.exists(condition_slug):
                return sources

            schema = registry.get(condition_slug)

            # Extract PMIDs from references
            for ref in schema.references:
                pmid = ref.get("pmid", "")
                if pmid and not str(pmid).startswith("placeholder"):
                    sources.append(ResearchSource(
                        source_type="internal",
                        title=ref.get("title", ""),
                        authors=ref.get("authors", ""),
                        year=ref.get("year"),
                        pmid=str(pmid),
                        relevance_score=0.9,
                        evidence_level=ref.get("evidence_level", "medium"),
                    ))

            # Extract PMIDs from assessment tools
            for tool in schema.assessment_tools:
                if tool.evidence_pmid:
                    sources.append(ResearchSource(
                        source_type="internal",
                        title=f"{tool.name} ({tool.abbreviation})",
                        pmid=tool.evidence_pmid,
                        relevance_score=0.8,
                    ))

        except Exception as e:
            logger.debug(f"Internal evidence retrieval failed: {e}")

        return sources

    def _get_evidence_profile_sources(
        self, condition_slug: str, section: TemplateSectionSpec
    ) -> list[ResearchSource]:
        """Get sources from pre-curated evidence profiles."""
        sources = []
        try:
            from ..core.data_loader import load_protocol_data
            data = load_protocol_data(condition_slug)
            if not data:
                return sources

            # Protocol data contains clinical parameters grounded in evidence
            # Mark these as high-relevance internal sources
            if "tps" in section.section_id or "protocol" in section.section_id:
                for p in data.get("tps", [])[:3]:
                    sources.append(ResearchSource(
                        source_type="internal",
                        title=f"TPS {p.get('code', '')}: {p.get('symptom', '')}",
                        key_finding=p.get("rationale", ""),
                        relevance_score=0.85,
                        evidence_level=p.get("evidence", "emerging").lower(),
                    ))

        except Exception as e:
            logger.debug(f"Evidence profile retrieval failed: {e}")

        return sources

    def _get_content_library_sources(
        self, condition_slug: str, section: TemplateSectionSpec
    ) -> list[ResearchSource]:
        """Get relevant content from the harvested content library."""
        sources = []
        try:
            from ..template.learning.content_harvester import ContentLibrary
            library_path = Path("data/learned/content_library.json")
            if not library_path.exists():
                return sources

            library = ContentLibrary.model_validate_json(library_path.read_text())

            # Search for matching sections
            for key, section_list in library.sections.items():
                if section.section_id in key or section.normalized_title.lower() in key:
                    for harvested in section_list[:2]:
                        if harvested.word_count > 20:
                            sources.append(ResearchSource(
                                source_type="internal",
                                title=f"Harvested: {harvested.title}",
                                abstract=harvested.content[:500],
                                key_finding=f"From {harvested.source_condition} {harvested.source_doc_type}",
                                relevance_score=0.7,
                            ))

        except Exception as e:
            logger.debug(f"Content library retrieval failed: {e}")

        return sources

    def _search_pubmed(self, queries: list[str], max_results: int) -> list[ResearchSource]:
        """Search PubMed for evidence articles."""
        sources = []
        try:
            from ..evidence.pubmed_client import PubMedClient
            client = PubMedClient()

            for query in queries[:3]:  # Limit queries
                try:
                    articles = client.search(query, max_results=max_results)
                    for article in articles:
                        sources.append(ResearchSource(
                            source_type="pubmed",
                            title=article.title,
                            authors=", ".join(article.authors[:3]),
                            year=article.year,
                            pmid=article.pmid,
                            doi=article.doi,
                            abstract=article.abstract or "",
                            relevance_score=0.6,
                            evidence_level=article.evidence_level.value,
                        ))
                except Exception as e:
                    logger.debug(f"PubMed query failed: {e}")

        except ImportError:
            logger.debug("PubMed client not available")

        return sources

    def _build_queries(
        self, condition_name: str, section: TemplateSectionSpec
    ) -> list[str]:
        """Build search queries for a section."""
        queries = []

        # Match section to query templates
        section_lower = section.section_id.lower()
        for key, templates in _SECTION_QUERY_TEMPLATES.items():
            if key in section_lower:
                for t in templates:
                    queries.append(t.format(condition=condition_name))

        # Fallback generic query
        if not queries:
            queries.append(f"{condition_name} {section.normalized_title} neuromodulation")

        return queries

    def _deduplicate(self, sources: list[ResearchSource]) -> list[ResearchSource]:
        """Remove duplicate sources by PMID."""
        seen_pmids = set()
        unique = []
        for s in sources:
            if s.pmid:
                if s.pmid in seen_pmids:
                    continue
                seen_pmids.add(s.pmid)
            unique.append(s)
        return unique

    def _summarize(self, bundle: ResearchBundle) -> str:
        """Build a brief evidence summary for the section writer."""
        if not bundle.sources:
            return "No evidence sources found for this section."

        pmid_count = sum(1 for s in bundle.sources if s.pmid)
        internal_count = sum(1 for s in bundle.sources if s.source_type == "internal")
        pubmed_count = sum(1 for s in bundle.sources if s.source_type == "pubmed")

        parts = [f"{len(bundle.sources)} sources available"]
        if pmid_count:
            parts.append(f"{pmid_count} with PMIDs")
        if internal_count:
            parts.append(f"{internal_count} from internal data")
        if pubmed_count:
            parts.append(f"{pubmed_count} from PubMed")

        # Add key findings
        findings = [s.key_finding for s in bundle.sources if s.key_finding][:3]
        if findings:
            parts.append("Key findings: " + "; ".join(findings))

        return ". ".join(parts) + "."

    def _assess_confidence(self, bundle: ResearchBundle) -> str:
        """Assess overall evidence confidence for a section."""
        if not bundle.sources:
            return "insufficient"

        high_quality = sum(
            1 for s in bundle.sources
            if s.evidence_level in ("highest", "high")
        )
        with_pmid = sum(1 for s in bundle.sources if s.pmid)

        if high_quality >= 3 and with_pmid >= 3:
            return "high"
        if with_pmid >= 2:
            return "medium"
        if bundle.sources:
            return "low"
        return "insufficient"
