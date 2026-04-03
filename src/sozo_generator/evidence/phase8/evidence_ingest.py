from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .models import PaperRaw, EvidenceRecord, ConditionCorpus, PICOExtract, ProtocolParameters
from .config import CONDITION_CONFIGS, ALL_CONDITION_SLUGS, ConditionQueryConfig, PIPELINE_VERSION
from .openalex_client import OpenAlexClient
from .s2_client import SemanticScholarClient
from .pico_extractor import PICOExtractor, grade_evidence
from ...core.settings import get_settings
from ..pubmed_client import PubMedClient
from ...schemas.evidence import ArticleMetadata

logger = logging.getLogger(__name__)


def article_metadata_to_paper_raw(
    article: ArticleMetadata,
    condition_slug: str,
    modality_tags: list[str],
) -> PaperRaw:
    """Convert existing ArticleMetadata to PaperRaw format."""
    return PaperRaw(
        source="pubmed",
        source_id=article.pmid or "",
        doi=article.doi,
        pmid=article.pmid,
        title=article.title,
        authors=article.authors,
        year=article.year,
        journal=article.journal,
        abstract=article.abstract,
        open_access=False,
        condition_tags=[condition_slug],
        modality_tags=modality_tags,
    )


class EvidenceIngestor:
    """
    Main Phase 8 orchestrator. Builds a ConditionCorpus for each condition
    by querying OpenAlex, Semantic Scholar, and PubMed, then enriching with
    LLM-extracted PICO and protocol parameters.

    Typical usage::

        ingestor = EvidenceIngestor(dry_run=True)
        results = ingestor.ingest_all(slugs=["tms_depression", "tms_ocd"])
        for slug, corpus in results.items():
            print(slug, corpus.total_included)
    """

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        dry_run: bool = False,
        dry_run_papers: int = 5,
        skip_llm: bool = False,
        force_refresh: bool = False,
        batch_size: int = 5,
        max_papers_per_source: int = 40,
    ) -> None:
        """
        Initialise the ingestor with clients and configuration.

        Args:
            output_dir: Directory to write JSON corpora. Defaults to
                ``settings.output_dir / "evidence" / "phase8"``.
            dry_run: When True, cap to ``dry_run_papers`` total per condition
                and only issue a single query per source.
            dry_run_papers: Maximum papers to process in dry-run mode.
            skip_llm: When True, skip PICO / ProtocolParameters extraction.
                Useful for quick structural tests that save API cost.
            force_refresh: When True, ignore any cached corpus on disk.
            batch_size: Number of papers sent to the LLM in a single request.
            max_papers_per_source: Upper bound on results requested from each
                external source per query.
        """
        self.dry_run = dry_run
        self.dry_run_papers = dry_run_papers
        self.skip_llm = skip_llm
        self.force_refresh = force_refresh
        self.batch_size = batch_size
        self.max_papers_per_source = max_papers_per_source

        settings = get_settings()

        self.output_dir: Path = output_dir or (
            Path(settings.output_dir) / "evidence" / "phase8"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.openalex_client = OpenAlexClient(email=settings.ncbi_email)
        self.s2_client = SemanticScholarClient()
        self.pubmed_client = PubMedClient(email=settings.ncbi_email)
        self.pico_extractor = PICOExtractor(
            anthropic_api_key=settings.anthropic_api_key,
            openai_api_key=settings.openai_api_key,
            batch_size=batch_size,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ingest_condition(self, slug: str) -> ConditionCorpus:
        """
        Build and persist a :class:`ConditionCorpus` for a single condition.

        Steps:
            1. Validate ``slug`` exists in ``CONDITION_CONFIGS``.
            2. Return a cached corpus unless ``force_refresh`` is set.
            3. Fetch papers from OpenAlex, Semantic Scholar, and PubMed.
            4. Deduplicate by DOI / title+year.
            5. Optionally run LLM PICO extraction.
            6. Build :class:`EvidenceRecord` objects and compute stats.
            7. Persist to ``output_dir`` and return the corpus.

        Args:
            slug: Condition slug (must exist in ``CONDITION_CONFIGS``).

        Returns:
            A fully populated :class:`ConditionCorpus`.

        Raises:
            ValueError: If ``slug`` is not registered in ``CONDITION_CONFIGS``.
        """
        if slug not in CONDITION_CONFIGS:
            raise ValueError(
                f"Unknown condition slug '{slug}'. "
                f"Available: {sorted(CONDITION_CONFIGS)}"
            )

        cfg: ConditionQueryConfig = CONDITION_CONFIGS[slug]

        if not self.force_refresh:
            cached = self._load_cached_corpus(slug)
            if cached is not None:
                return cached

        t_start = time.perf_counter()
        logger.info("Starting ingestion for %s (%s)", cfg.condition_slug, cfg.condition_name)

        # ---- fetch -------------------------------------------------------
        openalex_papers = self._fetch_openalex(cfg)
        s2_papers = self._fetch_s2(cfg)
        priority_papers = self._fetch_priority_papers(cfg)

        all_papers: list[PaperRaw] = openalex_papers + s2_papers + priority_papers
        logger.info(
            "%s: fetched %d raw papers (openalex=%d, s2=%d, priority=%d)",
            slug,
            len(all_papers),
            len(openalex_papers),
            len(s2_papers),
            len(priority_papers),
        )

        # ---- deduplicate -------------------------------------------------
        papers = self._deduplicate(all_papers)

        # ---- dry-run cap -------------------------------------------------
        if self.dry_run:
            papers = papers[: self.dry_run_papers]
            logger.info("dry_run=True — capped to %d papers", len(papers))

        n_fetched = len(papers)

        # ---- LLM extraction ----------------------------------------------
        extractions: list[tuple[Optional[PICOExtract], Optional[ProtocolParameters]]]
        if self.skip_llm or not papers:
            extractions = [(None, None)] * len(papers)
        else:
            modalities: list[str] = list(cfg.primary_modalities)
            extractions = self.pico_extractor.extract_batch(
                papers=papers,
                condition_slug=slug,
                condition_name=cfg.condition_name,
                modalities=modalities,
            )

        # ---- build records -----------------------------------------------
        records = self._build_evidence_records(
            papers=papers,
            condition_slug=slug,
            cfg=cfg,
            extractions=extractions,
        )

        n_included = sum(1 for r in records if r.included)

        # ---- build corpus ------------------------------------------------
        corpus = ConditionCorpus(
            condition_slug=slug,
            condition_name=cfg.condition_name,
            pipeline_version=PIPELINE_VERSION,
            generated_at=datetime.now(timezone.utc),
            records=records,
        )
        corpus = self._compute_corpus_stats(corpus)

        self._save_corpus(corpus)

        elapsed = time.perf_counter() - t_start
        logger.info(
            "%s: ingestion complete in %.1fs — fetched=%d, included=%d, "
            "protocol_papers=%d",
            slug,
            elapsed,
            n_fetched,
            n_included,
            sum(1 for r in records if r.protocol_params is not None),
        )
        return corpus

    def ingest_all(
        self,
        slugs: Optional[list[str]] = None,
        stop_on_error: bool = False,
    ) -> dict[str, ConditionCorpus]:
        """
        Ingest all (or a subset of) conditions.

        Args:
            slugs: List of condition slugs to process. Defaults to
                ``ALL_CONDITION_SLUGS``.
            stop_on_error: When True, re-raise the first exception encountered.
                When False (default), log the error and continue.

        Returns:
            Mapping of ``{slug: ConditionCorpus}`` for every successfully
            ingested condition.
        """
        target_slugs: list[str] = slugs if slugs is not None else list(ALL_CONDITION_SLUGS)
        total = len(target_slugs)
        results: dict[str, ConditionCorpus] = {}

        for slug in target_slugs:
            try:
                corpus = self.ingest_condition(slug)
                results[slug] = corpus
            except Exception as exc:  # noqa: BLE001
                if stop_on_error:
                    raise
                logger.error(
                    "Ingestion failed for '%s': %s",
                    slug,
                    exc,
                    exc_info=True,
                )

        logger.info(
            "Ingestion complete: %d/%d conditions successful",
            len(results),
            total,
        )
        return results

    # ------------------------------------------------------------------
    # Private fetch helpers
    # ------------------------------------------------------------------

    def _fetch_openalex(self, cfg: ConditionQueryConfig) -> list[PaperRaw]:
        """
        Execute OpenAlex queries for the given condition config.

        In dry-run mode only the first query is issued to minimise API load.

        Args:
            cfg: Condition query configuration.

        Returns:
            Accumulated list of :class:`PaperRaw` objects.
        """
        papers: list[PaperRaw] = []
        queries = cfg.openalex_queries or []

        for i, query in enumerate(queries):
            try:
                batch = self.openalex_client.search(
                    query=query,
                    max_results=self.max_papers_per_source,
                    min_year=cfg.min_year,
                    condition_tags=[cfg.condition_slug],
                    modality_tags=list(cfg.primary_modalities),
                )
                papers.extend(batch)
                logger.debug(
                    "OpenAlex query %d/%d for '%s': +%d papers",
                    i + 1,
                    len(queries),
                    cfg.condition_slug,
                    len(batch),
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "OpenAlex query failed for '%s' (query=%r): %s",
                    cfg.condition_slug,
                    query,
                    exc,
                )

            if self.dry_run:
                break

        return papers

    def _fetch_s2(self, cfg: ConditionQueryConfig) -> list[PaperRaw]:
        """
        Execute Semantic Scholar queries for the given condition config.

        In dry-run mode only the first query is issued.

        Args:
            cfg: Condition query configuration.

        Returns:
            Accumulated list of :class:`PaperRaw` objects.
        """
        papers: list[PaperRaw] = []
        queries = cfg.s2_queries or []

        for i, query in enumerate(queries):
            try:
                batch = self.s2_client.search(
                    query=query,
                    max_results=self.max_papers_per_source,
                    min_year=cfg.min_year,
                    condition_tags=[cfg.condition_slug],
                    modality_tags=list(cfg.primary_modalities),
                )
                papers.extend(batch)
                logger.debug(
                    "S2 query %d/%d for '%s': +%d papers",
                    i + 1,
                    len(queries),
                    cfg.condition_slug,
                    len(batch),
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Semantic Scholar query failed for '%s' (query=%r): %s",
                    cfg.condition_slug,
                    query,
                    exc,
                )

            if self.dry_run:
                break

        return papers

    def _fetch_priority_papers(self, cfg: ConditionQueryConfig) -> list[PaperRaw]:
        """
        Fetch high-priority papers by PMID and DOI.

        Papers retrieved here are always marked for inclusion and bypass the
        LLM relevance filter.

        Args:
            cfg: Condition query configuration.

        Returns:
            List of :class:`PaperRaw` objects for priority PMIDs and DOIs.
        """
        papers: list[PaperRaw] = []
        modality_tags: list[str] = list(cfg.primary_modalities)

        # ---- PubMed priority PMIDs --------------------------------------
        priority_pmids: list[str] = list(cfg.priority_pmids or [])
        if priority_pmids:
            try:
                articles: list[ArticleMetadata] = self.pubmed_client.fetch_by_pmids(
                    priority_pmids
                )
                for article in articles:
                    raw = article_metadata_to_paper_raw(
                        article=article,
                        condition_slug=cfg.condition_slug,
                        modality_tags=modality_tags,
                    )
                    raw = raw.model_copy(update={"is_priority": True})
                    papers.append(raw)
                logger.debug(
                    "Priority PMIDs for '%s': fetched %d/%d",
                    cfg.condition_slug,
                    len(articles),
                    len(priority_pmids),
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "PubMed priority fetch failed for '%s': %s",
                    cfg.condition_slug,
                    exc,
                )

        # ---- OpenAlex priority DOIs -------------------------------------
        priority_dois: list[str] = list(cfg.priority_dois or [])
        for doi in priority_dois:
            try:
                raw: Optional[PaperRaw] = self.openalex_client.fetch_by_doi(
                    doi=doi,
                    condition_tags=[cfg.condition_slug],
                    modality_tags=modality_tags,
                )
                if raw is not None:
                    raw = raw.model_copy(update={"is_priority": True})
                    papers.append(raw)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "OpenAlex DOI fetch failed for '%s' (doi=%s): %s",
                    cfg.condition_slug,
                    doi,
                    exc,
                )

        return papers

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------

    def _deduplicate(self, papers: list[PaperRaw]) -> list[PaperRaw]:
        """
        Remove duplicate papers using a two-tier key strategy.

        Primary key: normalised DOI (lowercase, stripped).
        Secondary key: ``(title[:80].lower().strip(), year)`` for papers
        without a DOI.

        The first occurrence of each key is kept.

        Args:
            papers: Raw list potentially containing duplicates.

        Returns:
            Deduplicated list preserving original ordering.
        """
        seen_dois: set[str] = set()
        seen_title_year: set[tuple[str, Optional[int]]] = set()
        unique: list[PaperRaw] = []
        n_removed = 0

        for paper in papers:
            doi_key: Optional[str] = (
                paper.doi.lower().strip() if paper.doi else None
            )

            if doi_key:
                if doi_key in seen_dois:
                    n_removed += 1
                    continue
                seen_dois.add(doi_key)
            else:
                title_norm = (paper.title or "").lower().strip()[:80]
                ty_key: tuple[str, Optional[int]] = (title_norm, paper.year)
                if ty_key in seen_title_year:
                    n_removed += 1
                    continue
                seen_title_year.add(ty_key)

            unique.append(paper)

        logger.info(
            "Deduplication: %d → %d papers (%d removed)",
            len(papers),
            len(unique),
            n_removed,
        )
        return unique

    # ------------------------------------------------------------------
    # Record building
    # ------------------------------------------------------------------

    def _build_evidence_records(
        self,
        papers: list[PaperRaw],
        condition_slug: str,
        cfg: ConditionQueryConfig,
        extractions: list[tuple[Optional[PICOExtract], Optional[ProtocolParameters]]],
    ) -> list[EvidenceRecord]:
        """
        Combine :class:`PaperRaw` objects with LLM extractions into
        :class:`EvidenceRecord` instances.

        Args:
            papers: Deduplicated papers to convert.
            condition_slug: Slug of the owning condition.
            cfg: Condition query configuration (used for tag fallbacks).
            extractions: Aligned list of ``(PICOExtract | None, ProtocolParameters | None)``
                tuples, one per paper.

        Returns:
            List of :class:`EvidenceRecord` objects ready for corpus assembly.
        """
        records: list[EvidenceRecord] = []

        for paper, (pico, protocol_params) in zip(papers, extractions):
            # ---- primary modality ----------------------------------------
            primary_modality: Optional[str]
            if protocol_params is not None and getattr(protocol_params, "modality", None):
                primary_modality = protocol_params.modality
            elif paper.modality_tags:
                primary_modality = paper.modality_tags[0]
            else:
                primary_modality = None

            # ---- evidence grade ------------------------------------------
            study_design: Optional[str] = getattr(paper, "study_design", None)
            evidence_grade: Optional[str] = grade_evidence(study_design, pico)

            # ---- inclusion / exclusion -----------------------------------
            included: bool = True
            exclusion_reason: Optional[str] = None

            if pico is not None and getattr(pico, "irrelevant", False):
                included = False
                exclusion_reason = getattr(pico, "irrelevance_reason", None)

            # Priority papers are never excluded via the LLM filter
            if getattr(paper, "is_priority", False):
                included = True
                exclusion_reason = None

            record = EvidenceRecord(
                condition_slug=condition_slug,
                paper=paper,
                pico=pico,
                protocol_params=protocol_params,
                primary_modality=primary_modality,
                evidence_grade=evidence_grade,
                included=included,
                exclusion_reason=exclusion_reason,
            )
            records.append(record)

        return records

    # ------------------------------------------------------------------
    # Stats & persistence
    # ------------------------------------------------------------------

    def _compute_corpus_stats(self, corpus: ConditionCorpus) -> ConditionCorpus:
        """
        Compute summary statistics and return an updated corpus.

        Uses ``model_copy(update={...})`` so the original is not mutated.

        Args:
            corpus: The corpus whose stats should be computed.

        Returns:
            A new :class:`ConditionCorpus` with populated stat fields.
        """
        records = corpus.records

        total_papers_fetched: int = len(records)
        included_records = [r for r in records if r.included]
        total_included: int = len(included_records)
        total_excluded: int = total_papers_fetched - total_included

        # ---- sources breakdown -------------------------------------------
        sources_breakdown: dict[str, int] = {}
        for record in records:
            src = record.paper.source or "unknown"
            sources_breakdown[src] = sources_breakdown.get(src, 0) + 1

        # ---- grade breakdown ---------------------------------------------
        evidence_grade_breakdown: dict[str, int] = {}
        for record in included_records:
            grade = record.evidence_grade or "ungraded"
            evidence_grade_breakdown[grade] = (
                evidence_grade_breakdown.get(grade, 0) + 1
            )

        # ---- modalities covered -----------------------------------------
        modalities_covered: list[str] = sorted(
            {
                record.primary_modality
                for record in included_records
                if record.primary_modality is not None
            }
        )

        return corpus.model_copy(
            update={
                "total_papers_fetched": total_papers_fetched,
                "total_included": total_included,
                "total_excluded": total_excluded,
                "sources_breakdown": sources_breakdown,
                "evidence_grade_breakdown": evidence_grade_breakdown,
                "modalities_covered": modalities_covered,
            }
        )

    def _save_corpus(self, corpus: ConditionCorpus) -> Path:
        """
        Serialise the corpus to disk as JSON.

        Two files are written:
        * ``{slug}.json`` — full corpus via ``model_dump_json``.
        * ``{slug}_summary.json`` — lightweight summary via ``to_summary_dict``.

        Args:
            corpus: The corpus to persist.

        Returns:
            Path to the primary JSON file.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / f"{corpus.condition_slug}.json"

        output_path.write_text(
            corpus.model_dump_json(indent=2),
            encoding="utf-8",
        )

        # ---- summary file -----------------------------------------------
        summary_path = self.output_dir / f"{corpus.condition_slug}_summary.json"
        summary_data: dict = corpus.to_summary_dict()
        summary_path.write_text(
            json.dumps(summary_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        logger.info(
            "Saved corpus: %s (%d records)",
            output_path,
            len(corpus.records),
        )
        return output_path

    def _load_cached_corpus(self, slug: str) -> Optional[ConditionCorpus]:
        """
        Attempt to load a previously persisted corpus from disk.

        Args:
            slug: Condition slug whose corpus file to look for.

        Returns:
            A validated :class:`ConditionCorpus` or ``None`` if the file does
            not exist or fails validation.
        """
        corpus_path = self.output_dir / f"{slug}.json"
        if not corpus_path.exists():
            return None

        try:
            corpus = ConditionCorpus.model_validate_json(
                corpus_path.read_text(encoding="utf-8")
            )
            logger.info("Loaded cached corpus for %s", slug)
            return corpus
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to load cached corpus for '%s' (%s): %s — re-fetching.",
                slug,
                corpus_path,
                exc,
            )
            return None


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """
    CLI entry point for the Phase 8 evidence ingestion pipeline.

    Usage::

        python -m sozo_generator.evidence.phase8.evidence_ingest [options]

    Options:
        --conditions  Comma-separated slugs (default: all)
        --dry-run     Cap at 5 papers per source, useful for testing
        --skip-llm    Skip PICO extraction
        --force       Ignore cached corpora and re-fetch
        --output-dir  Override output directory
        --log-level   DEBUG / INFO / WARNING (default: INFO)
    """
    import argparse

    parser = argparse.ArgumentParser(description="Sozo Phase 8 Evidence Ingestion")
    parser.add_argument(
        "--conditions",
        type=str,
        default=None,
        help="Comma-separated condition slugs (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Cap at 5 papers per source",
    )
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip LLM PICO extraction",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore cached corpora and re-fetch",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Override output directory",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        help="Logging level: DEBUG / INFO / WARNING (default: INFO)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    slugs: Optional[list[str]] = (
        [s.strip() for s in args.conditions.split(",")]
        if args.conditions
        else None
    )
    output_dir: Optional[Path] = (
        Path(args.output_dir) if args.output_dir else None
    )

    ingestor = EvidenceIngestor(
        output_dir=output_dir,
        dry_run=args.dry_run,
        skip_llm=args.skip_llm,
        force_refresh=args.force,
    )
    results = ingestor.ingest_all(slugs=slugs)

    print(f"\n✓ Ingestion complete: {len(results)} conditions processed")
    for slug, corpus in results.items():
        print(
            f"  {slug}: {corpus.total_included} included "
            f"/ {corpus.total_papers_fetched} fetched"
        )


if __name__ == "__main__":
    main()
