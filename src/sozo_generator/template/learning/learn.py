"""
Master learning pipeline — ingests existing documents, extracts patterns,
saves the master profile, and can score new documents for consistency.

Usage:
    from sozo_generator.template.learning.learn import learn_from_existing, score_new_document
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from .document_ingester import (
    ingest_directory,
    ingest_document,
    save_fingerprints,
    load_fingerprints,
    DocumentFingerprint,
)
from .pattern_extractor import (
    PatternExtractor,
    MasterTemplateProfile,
    save_profile,
    load_profile,
)
from .consistency_scorer import ConsistencyScorer, ConsistencyReport

logger = logging.getLogger(__name__)

# Default paths
_DEFAULT_DOCS_DIR = Path("outputs/documents/")
_DEFAULT_DATA_DIR = Path("data/learned/")
_FINGERPRINTS_FILE = "document_fingerprints.json"
_PROFILE_FILE = "master_template_profile.json"


def learn_from_existing(
    documents_dir: Optional[Path] = None,
    output_dir: Optional[Path] = None,
) -> MasterTemplateProfile:
    """
    Full learning pipeline:
    1. Ingest all existing DOCX files
    2. Extract patterns
    3. Save fingerprints and master profile
    4. Return the profile
    """
    docs_dir = Path(documents_dir or _DEFAULT_DOCS_DIR)
    out_dir = Path(output_dir or _DEFAULT_DATA_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Ingest
    logger.info("Ingesting documents from %s...", docs_dir)
    fingerprints = ingest_directory(docs_dir)
    if not fingerprints:
        logger.warning("No documents found in %s", docs_dir)
        return MasterTemplateProfile()

    # Save fingerprints
    fp_path = out_dir / _FINGERPRINTS_FILE
    save_fingerprints(fingerprints, fp_path)

    # Step 2: Extract patterns
    logger.info("Extracting patterns from %d documents...", len(fingerprints))
    extractor = PatternExtractor(fingerprints)
    profile = extractor.extract_master_profile()

    # Step 3: Save profile
    profile_path = out_dir / _PROFILE_FILE
    save_profile(profile, profile_path)

    logger.info(
        "Learning complete: %d docs, %d doc-type patterns, %d boilerplate blocks, "
        "%d table patterns, %d section patterns",
        profile.total_documents_analyzed,
        len(profile.doc_type_patterns),
        len(profile.boilerplate_blocks),
        len(profile.table_patterns),
        len(profile.section_patterns),
    )
    return profile


def score_new_document(
    file_path: Path,
    profile: Optional[MasterTemplateProfile] = None,
    profile_path: Optional[Path] = None,
) -> ConsistencyReport:
    """Score a single document against the master profile."""
    if profile is None:
        pp = Path(profile_path or _DEFAULT_DATA_DIR / _PROFILE_FILE)
        if not pp.exists():
            raise FileNotFoundError(
                f"No master profile found at {pp}. Run learn_from_existing() first."
            )
        raw = load_profile(pp)
        profile = MasterTemplateProfile(**{
            k: v for k, v in raw.items()
            if k in MasterTemplateProfile.__dataclass_fields__
        })

    fp = ingest_document(file_path)
    scorer = ConsistencyScorer(profile)
    return scorer.score_document(fp)


def score_batch(
    documents_dir: Path,
    profile: Optional[MasterTemplateProfile] = None,
) -> list[ConsistencyReport]:
    """Score all documents in a directory against the master profile."""
    if profile is None:
        profile = learn_from_existing()

    fingerprints = ingest_directory(documents_dir)
    scorer = ConsistencyScorer(profile)
    return scorer.score_batch(fingerprints)
