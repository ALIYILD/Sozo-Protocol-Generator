"""
sozo_generator.evidence.phase8
==============================
Phase 8 evidence ingestion pipeline.

Fetches papers from OpenAlex, Semantic Scholar, and PubMed for each of the 15
Sozo neuromodulation conditions, runs LLM-based PICO + protocol-parameter
extraction, and saves a typed ConditionCorpus JSON per condition.

Quick start
-----------
    from sozo_generator.evidence.phase8 import EvidenceIngestor

    ingestor = EvidenceIngestor(dry_run=True)
    corpus = ingestor.ingest_condition("depression")
    print(corpus.to_summary_dict())

CLI
---
    python -m sozo_generator.evidence.phase8.evidence_ingest --dry-run --conditions depression,anxiety
"""
from .models import (
    PaperRaw,
    PICOExtract,
    ProtocolParameters,
    EvidenceRecord,
    ConditionCorpus,
)
from .config import (
    ConditionQueryConfig,
    CONDITION_CONFIGS,
    ALL_CONDITION_SLUGS,
    DEFAULT_MAX_PAPERS,
    DEFAULT_MIN_YEAR,
    PIPELINE_VERSION,
)
from .models import ConsensusFinding
from .consensus_client import ConsensusClient
from .batch_pico_extract import batch_pico_extract
from .consensus_ingest import run_pipeline as run_consensus_pipeline

# Optional deps: EvidenceIngestor (requires pyalex) and PICOExtractor
# (requires anthropic/openai) may not be importable in all environments.
try:
    from .evidence_ingest import EvidenceIngestor
except ImportError:
    EvidenceIngestor = None  # type: ignore[assignment,misc]

try:
    from .pico_extractor import PICOExtractor, grade_evidence
except ImportError:
    PICOExtractor = None  # type: ignore[assignment,misc]
    grade_evidence = None  # type: ignore[assignment]

__all__ = [
    # Models
    "PaperRaw", "PICOExtract", "ProtocolParameters", "EvidenceRecord",
    "ConditionCorpus", "ConsensusFinding",
    # Config
    "ConditionQueryConfig", "CONDITION_CONFIGS", "ALL_CONDITION_SLUGS",
    "DEFAULT_MAX_PAPERS", "DEFAULT_MIN_YEAR", "PIPELINE_VERSION",
    # Consensus pipeline (Phase 8 primary)
    "ConsensusClient", "batch_pico_extract", "run_consensus_pipeline",
    # Optional (OpenAlex / legacy)
    "EvidenceIngestor", "PICOExtractor", "grade_evidence",
]
