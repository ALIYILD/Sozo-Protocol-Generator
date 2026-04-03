"""
Evidence layer — PRISMA-style research pipeline for neuromodulation protocols.

Core modules:
  - pubmed_client: PubMed search via NCBI Entrez
  - crossref_client: Crossref REST API search
  - semantic_scholar_client: Semantic Scholar Academic Graph API
  - multi_source_search: Unified multi-source search coordinator
  - fuzzy_dedup: Cross-source deduplication (PMID + DOI + title similarity)
  - screening: Keyword-based relevance screening
  - parameter_extractor: Structured stimulation parameter extraction
  - evidence_scorer: Multi-dimensional quality + relevance scoring
  - citation_grounding: Claim-level citation trace with provenance
  - pipeline_tracker: PRISMA audit trail for every decision
  - prisma_diagram: PRISMA 2020 flow diagram generator
  - research_pipeline: Full pipeline orchestrator

Legacy modules (still in use):
  - article_ranker: Simple ranking by evidence level + recency
  - confidence: Confidence label assignment
  - summarizer: Evidence dossier builder
  - contradiction: Direction-conflict detector
  - bundles: File-backed bundle storage
  - snapshots: Versioned evidence snapshots
  - cache: File-based query cache
"""
