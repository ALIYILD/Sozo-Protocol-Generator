"""
Phase 8 Evidence Ingestion — Consensus Pipeline Orchestrator
=============================================================
Entry point for the Phase 8 evidence ingestion pipeline.

Pipeline stages
---------------
1. **Consensus retrieval** — query Consensus API for each condition using
   ``consensus_queries`` from :mod:`config`.
2. **S2 abstract enrichment** — fetch full abstracts for papers missing
   them via Semantic Scholar.
3. **Deduplication** — merge by DOI; papers seen from multiple queries
   keep the first occurrence.
4. **Priority paper injection** — unconditionally add landmark papers
   from ``priority_dois`` / ``priority_pmids``.
5. **PICO extraction** — batch LLM extraction of PICO + protocol params.
6. **Corpus serialisation** — write per-condition ``ConditionCorpus``
   JSON to ``data/evidence/phase8/<condition_slug>/corpus.json``.
7. **Audit log** — append a structured log line to
   ``data/evidence/phase8/ingest_log.jsonl``.

Quick start
-----------
::

    # Full run (all 15 conditions):
    python -m sozo_generator.evidence.phase8.consensus_ingest

    # Dry-run (5 papers per condition, no network, no LLM):
    python -m sozo_generator.evidence.phase8.consensus_ingest --dry-run

    # Single condition:
    python -m sozo_generator.evidence.phase8.consensus_ingest --condition depression

    # Max papers per condition (default 50):
    python -m sozo_generator.evidence.phase8.consensus_ingest --max-papers 20

Environment variables
---------------------
CONSENSUS_API_KEY     — Consensus API key (required for live run)
ANTHROPIC_API_KEY     — Preferred LLM for PICO extraction
OPENAI_API_KEY        — Fallback LLM for PICO extraction
S2_API_KEY            — Optional; improves S2 rate limits
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .batch_pico_extract import batch_pico_extract
from .config import ALL_CONDITION_SLUGS, CONDITION_CONFIGS, ConditionQueryConfig
from .consensus_client import ConsensusClient
from .models import (
    ConditionCorpus,
    ConsensusFinding,
    EvidenceRecord,
    PaperRaw,
)

# S2 client is used for abstract enrichment (optional dep)
try:
    from .s2_client import SemanticScholarClient
    _S2_AVAILABLE = True
except ImportError:
    _S2_AVAILABLE = False

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_OUTPUT_BASE = Path("data/evidence/phase8")
_AUDIT_LOG = _OUTPUT_BASE / "ingest_log.jsonl"
_DRY_RUN_PAPERS_PER_CONDITION = 5
_DEFAULT_MAX_PAPERS = 50
_DEFAULT_BATCH_SIZE = 8     # PICO extraction batch size
_STUDY_TYPES_RCT_META = ["RCT", "Meta-Analysis", "Systematic Review", "Controlled Trial"]


# ---------------------------------------------------------------------------
# Pipeline entry point
# ---------------------------------------------------------------------------


def run_pipeline(
    condition_slugs: Optional[list[str]] = None,
    dry_run: bool = False,
    max_papers: int = _DEFAULT_MAX_PAPERS,
    pico_batch_size: int = _DEFAULT_BATCH_SIZE,
    skip_pico: bool = False,
    consensus_api_key: Optional[str] = None,
    s2_api_key: Optional[str] = None,
    anthropic_api_key: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> dict[str, ConditionCorpus]:
    """
    Run the full Phase 8 ingestion pipeline.

    Parameters
    ----------
    condition_slugs:
        Conditions to process.  Defaults to all 15.
    dry_run:
        Fetch at most ``_DRY_RUN_PAPERS_PER_CONDITION`` papers per condition,
        skip PICO extraction, and write output to
        ``<output_dir>/dry_run/``.
    max_papers:
        Maximum papers to retrieve from Consensus per condition.
    pico_batch_size:
        LLM extraction batch size.
    skip_pico:
        Skip PICO extraction entirely (fast retrieval-only run).
    output_dir:
        Override the default ``data/evidence/phase8/`` output directory.

    Returns
    -------
    dict[str, ConditionCorpus]
        Mapping of condition slug → ConditionCorpus.
    """
    slugs = condition_slugs or ALL_CONDITION_SLUGS
    out_base = output_dir or _OUTPUT_BASE
    if dry_run:
        out_base = out_base / "dry_run"

    out_base.mkdir(parents=True, exist_ok=True)
    _AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

    c_client = ConsensusClient(
        api_key=consensus_api_key,
        dry_run=dry_run,
    )
    s2_client: Optional[SemanticScholarClient] = None
    if _S2_AVAILABLE and not dry_run:
        try:
            s2_client = SemanticScholarClient(api_key=s2_api_key)
        except Exception as exc:  # noqa: BLE001
            logger.warning("S2 client init failed: %s — S2 enrichment disabled", exc)

    corpora: dict[str, ConditionCorpus] = {}
    start_ts = time.monotonic()

    for slug in slugs:
        if slug not in CONDITION_CONFIGS:
            logger.error("Unknown condition slug %r — skipping", slug)
            continue

        cfg = CONDITION_CONFIGS[slug]
        logger.info("=" * 60)
        logger.info("Processing condition: %s (%s)", slug, cfg.condition_name)

        try:
            corpus = _process_condition(
                cfg=cfg,
                c_client=c_client,
                s2_client=s2_client,
                dry_run=dry_run,
                max_papers=max_papers,
                pico_batch_size=pico_batch_size,
                skip_pico=skip_pico,
                anthropic_api_key=anthropic_api_key,
                openai_api_key=openai_api_key,
            )
            corpora[slug] = corpus

            # Write per-condition corpus
            condition_dir = out_base / slug
            condition_dir.mkdir(parents=True, exist_ok=True)
            corpus_path = condition_dir / "corpus.json"
            corpus_path.write_text(
                corpus.model_dump_json(indent=2),
                encoding="utf-8",
            )
            logger.info(
                "[%s] Corpus written → %s (%d included / %d total records)",
                slug,
                corpus_path,
                len(corpus.included_records),
                len(corpus.records),
            )

            _append_audit_log(
                slug=slug,
                corpus=corpus,
                dry_run=dry_run,
                success=True,
            )

        except Exception as exc:  # noqa: BLE001
            logger.exception("Pipeline failed for condition %r: %s", slug, exc)
            _append_audit_log(
                slug=slug,
                corpus=None,
                dry_run=dry_run,
                success=False,
                error=str(exc),
            )

    elapsed = time.monotonic() - start_ts
    logger.info("=" * 60)
    logger.info(
        "Phase 8 pipeline complete: %d/%d conditions, %.1fs elapsed",
        len(corpora),
        len(slugs),
        elapsed,
    )
    return corpora


# ---------------------------------------------------------------------------
# Per-condition processing
# ---------------------------------------------------------------------------


def _process_condition(
    cfg: ConditionQueryConfig,
    c_client: ConsensusClient,
    s2_client: Optional[SemanticScholarClient],
    dry_run: bool,
    max_papers: int,
    pico_batch_size: int,
    skip_pico: bool,
    anthropic_api_key: Optional[str],
    openai_api_key: Optional[str],
) -> ConditionCorpus:
    slug = cfg.condition_slug
    effective_max = _DRY_RUN_PAPERS_PER_CONDITION if dry_run else max_papers

    # ── Stage 1: Consensus retrieval ─────────────────────────────────────────
    findings = _run_consensus_queries(
        cfg=cfg,
        c_client=c_client,
        max_per_query=max(effective_max // max(len(cfg.consensus_queries), 1), 5),
        study_types=_STUDY_TYPES_RCT_META,
    )
    logger.info("[%s] Consensus: %d findings retrieved", slug, len(findings))

    # ── Stage 2: Convert findings → EvidenceRecord ──────────────────────────
    records = _findings_to_records(findings, cfg)
    logger.info("[%s] Converted to %d EvidenceRecord(s)", slug, len(records))

    # ── Stage 3: S2 abstract enrichment ─────────────────────────────────────
    if s2_client is not None and not dry_run:
        records = _enrich_abstracts_s2(records, s2_client, slug)

    # ── Stage 4: Priority paper injection ───────────────────────────────────
    if not dry_run:
        records = _inject_priority_papers(records, cfg, s2_client, slug)

    # ── Stage 5: PICO extraction ─────────────────────────────────────────────
    if not skip_pico and not dry_run:
        records = batch_pico_extract(
            records,
            condition_slug=slug,
            anthropic_api_key=anthropic_api_key,
            openai_api_key=openai_api_key,
            batch_size=pico_batch_size,
        )
        pico_count = sum(1 for r in records if r.pico is not None)
        logger.info("[%s] PICO extracted for %d/%d records", slug, pico_count, len(records))

    # ── Stage 6: Assemble corpus ─────────────────────────────────────────────
    return ConditionCorpus(
        condition_slug=slug,
        condition_name=cfg.condition_name,
        records=records,
        query_strings=cfg.consensus_queries,
        sources_used=["consensus"] + (["semantic_scholar"] if s2_client else []),
        pipeline_version="phase8_v1",
    )


# ---------------------------------------------------------------------------
# Consensus query execution
# ---------------------------------------------------------------------------


def _run_consensus_queries(
    cfg: ConditionQueryConfig,
    c_client: ConsensusClient,
    max_per_query: int,
    study_types: list[str],
) -> list[ConsensusFinding]:
    """Run all consensus_queries for a condition and deduplicate by DOI."""
    seen: set[str] = set()
    all_findings: list[ConsensusFinding] = []

    for query in cfg.consensus_queries:
        findings = c_client.search(
            query=query,
            study_types=study_types,
            human_only=True,
            year_min=cfg.min_year,
            max_results=max_per_query,
        )
        for f in findings:
            key = _dedup_key(f.doi, f.pmid, f.consensus_paper_id)
            if key not in seen:
                seen.add(key)
                all_findings.append(f)

    return all_findings


# ---------------------------------------------------------------------------
# Record conversion
# ---------------------------------------------------------------------------


def _findings_to_records(
    findings: list[ConsensusFinding],
    cfg: ConditionQueryConfig,
) -> list[EvidenceRecord]:
    """Convert ConsensusFinding objects to EvidenceRecord objects."""
    records: list[EvidenceRecord] = []
    for f in findings:
        paper = PaperRaw(
            source="consensus",
            source_id=f.consensus_paper_id,
            doi=f.doi,
            pmid=f.pmid,
            title=f.title or f.claim[:80] or "Unknown",
            authors=f.authors,
            year=f.year,
            journal=f.journal,
            abstract=None,   # fetched in Stage 3
            open_access=False,
            study_design=_normalise_study_design(f.study_type),
            condition_tags=[cfg.condition_slug],
            modality_tags=cfg.primary_modalities,
        )
        record = EvidenceRecord(
            condition_slug=cfg.condition_slug,
            paper=paper,
            consensus_finding=f,
            primary_modality=_guess_modality(f.study_type, cfg.primary_modalities),
        )
        records.append(record)
    return records


# ---------------------------------------------------------------------------
# S2 abstract enrichment
# ---------------------------------------------------------------------------


def _enrich_abstracts_s2(
    records: list[EvidenceRecord],
    s2_client: SemanticScholarClient,
    slug: str,
) -> list[EvidenceRecord]:
    """Fetch abstracts from Semantic Scholar for records missing them."""
    enriched: list[EvidenceRecord] = []
    needs_abstract = [r for r in records if not r.paper.abstract]
    already_have = [r for r in records if r.paper.abstract]

    logger.info("[%s] S2 abstract enrichment: %d records need abstracts", slug, len(needs_abstract))

    for rec in needs_abstract:
        doi = rec.paper.doi
        pmid = rec.paper.pmid
        s2_paper: Optional[PaperRaw] = None

        try:
            if doi:
                results = s2_client.fetch_by_doi(doi)
                s2_paper = results[0] if results else None
            elif pmid:
                results = s2_client.fetch_by_pmid(pmid)
                s2_paper = results[0] if results else None
        except Exception as exc:  # noqa: BLE001
            logger.debug("[%s] S2 lookup failed for %r: %s", slug, rec.paper.title[:50], exc)

        if s2_paper and s2_paper.abstract:
            updated_paper = rec.paper.model_copy(
                update={
                    "abstract": s2_paper.abstract,
                    "s2_tldr": s2_paper.s2_tldr,
                    "s2_citation_count": s2_paper.s2_citation_count,
                    "s2_influential_citations": s2_paper.s2_influential_citations,
                    "open_access": s2_paper.open_access,
                    "oa_url": s2_paper.oa_url,
                }
            )
            enriched.append(rec.model_copy(update={"paper": updated_paper}))
        else:
            enriched.append(rec)

    return already_have + enriched


# ---------------------------------------------------------------------------
# Priority paper injection
# ---------------------------------------------------------------------------


def _inject_priority_papers(
    records: list[EvidenceRecord],
    cfg: ConditionQueryConfig,
    s2_client: Optional[SemanticScholarClient],
    slug: str,
) -> list[EvidenceRecord]:
    """
    Ensure landmark papers are present in the corpus regardless of
    whether they appeared in the Consensus results.
    """
    existing_dois = {(r.paper.doi or "").lower() for r in records}
    existing_pmids = {(r.paper.pmid or "") for r in records}
    injected = 0

    for doi in cfg.priority_dois:
        doi_norm = doi.lower().strip()
        if doi_norm in existing_dois:
            continue
        paper = _fetch_paper_s2_doi(doi, s2_client, slug)
        if paper:
            records.append(_paper_to_record(paper, cfg))
            injected += 1

    for pmid in cfg.priority_pmids:
        if pmid in existing_pmids:
            continue
        paper = _fetch_paper_s2_pmid(pmid, s2_client, slug)
        if paper:
            records.append(_paper_to_record(paper, cfg))
            injected += 1

    if injected:
        logger.info("[%s] Injected %d priority paper(s)", slug, injected)
    return records


def _fetch_paper_s2_doi(
    doi: str,
    s2_client: Optional[SemanticScholarClient],
    slug: str,
) -> Optional[PaperRaw]:
    if not s2_client:
        return None
    try:
        results = s2_client.fetch_by_doi(doi)
        return results[0] if results else None
    except Exception as exc:  # noqa: BLE001
        logger.debug("[%s] S2 DOI fetch failed for %r: %s", slug, doi, exc)
        return None


def _fetch_paper_s2_pmid(
    pmid: str,
    s2_client: Optional[SemanticScholarClient],
    slug: str,
) -> Optional[PaperRaw]:
    if not s2_client:
        return None
    try:
        results = s2_client.fetch_by_pmid(pmid)
        return results[0] if results else None
    except Exception as exc:  # noqa: BLE001
        logger.debug("[%s] S2 PMID fetch failed for %r: %s", slug, pmid, exc)
        return None


def _paper_to_record(paper: PaperRaw, cfg: ConditionQueryConfig) -> EvidenceRecord:
    return EvidenceRecord(
        condition_slug=cfg.condition_slug,
        paper=paper,
        primary_modality=cfg.primary_modalities[0] if cfg.primary_modalities else None,
    )


# ---------------------------------------------------------------------------
# Audit logging
# ---------------------------------------------------------------------------


def _append_audit_log(
    slug: str,
    corpus: Optional[ConditionCorpus],
    dry_run: bool,
    success: bool,
    error: Optional[str] = None,
) -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "condition_slug": slug,
        "dry_run": dry_run,
        "success": success,
        "total_records": len(corpus.records) if corpus else 0,
        "included_records": len(corpus.included_records) if corpus else 0,
        "pico_extracted": sum(1 for r in corpus.records if r.pico is not None) if corpus else 0,
        "error": error,
    }
    try:
        with _AUDIT_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except OSError as exc:
        logger.warning("Audit log write failed: %s", exc)


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------


def _dedup_key(
    doi: Optional[str],
    pmid: Optional[str],
    fallback_id: str,
) -> str:
    if doi:
        return f"doi:{doi.lower().strip()}"
    if pmid:
        return f"pmid:{pmid}"
    return f"cid:{fallback_id}"


def _normalise_study_design(study_type: Optional[str]) -> Optional[str]:
    if not study_type:
        return None
    st = study_type.lower().strip()
    mapping = {
        "rct": "RCT",
        "randomized controlled trial": "RCT",
        "controlled trial": "RCT",
        "meta-analysis": "meta_analysis",
        "meta analysis": "meta_analysis",
        "systematic review": "systematic_review",
        "cohort": "cohort",
        "cohort study": "cohort",
        "pilot": "pilot",
        "pilot study": "pilot",
        "case series": "case_series",
        "case report": "case_series",
        "review": "review",
    }
    return mapping.get(st, "other")


def _guess_modality(
    study_type: Optional[str],
    primary_modalities: list[str],
) -> Optional[str]:
    return primary_modalities[0] if primary_modalities else None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="consensus_ingest",
        description="Phase 8: Consensus API evidence ingestion pipeline",
    )
    p.add_argument(
        "--condition",
        metavar="SLUG",
        action="append",
        dest="conditions",
        help="Condition slug(s) to process (repeatable; default: all 15)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help=f"Fetch at most {_DRY_RUN_PAPERS_PER_CONDITION} papers, skip PICO, write to dry_run/",
    )
    p.add_argument(
        "--max-papers",
        type=int,
        default=_DEFAULT_MAX_PAPERS,
        metavar="N",
        help=f"Max Consensus results per condition (default: {_DEFAULT_MAX_PAPERS})",
    )
    p.add_argument(
        "--skip-pico",
        action="store_true",
        help="Skip LLM PICO extraction (retrieval + dedup only)",
    )
    p.add_argument(
        "--batch-size",
        type=int,
        default=_DEFAULT_BATCH_SIZE,
        metavar="N",
        help=f"PICO extraction LLM batch size (default: {_DEFAULT_BATCH_SIZE})",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="Output directory (default: data/evidence/phase8/)",
    )
    p.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return p


def main(argv: Optional[list[str]] = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        stream=sys.stderr,
    )

    corpora = run_pipeline(
        condition_slugs=args.conditions,
        dry_run=args.dry_run,
        max_papers=args.max_papers,
        pico_batch_size=args.batch_size,
        skip_pico=args.skip_pico,
        output_dir=args.output_dir,
    )
    print(
        f"\nDone. {len(corpora)} condition(s) processed. "
        f"Output: {args.output_dir or _OUTPUT_BASE}"
    )


if __name__ == "__main__":
    main()
