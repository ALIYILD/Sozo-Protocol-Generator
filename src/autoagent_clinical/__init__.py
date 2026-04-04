"""
AutoAgent-Clinical — internal benchmark lab for SOZO document-generation QA.

Not a live clinical runtime. Use to evaluate fixtures, harness variants, and
validators before changes ship to production tooling.

Harness ``generation_service`` runs ``GenerationService`` and normalizes DOCX to
markdown for the same validator stack (opt-in benchmark file; see reports/README).
"""

from .registry import get_harness, list_harnesses, register_harness
from .runner import (
    compare_harnesses,
    load_all_benchmark_files,
    load_suite_from_path,
    run_suite,
)
from .schemas import BenchmarkSuite, FailureTaxonomy

__all__ = [
    "BenchmarkSuite",
    "FailureTaxonomy",
    "compare_harnesses",
    "get_harness",
    "list_harnesses",
    "load_all_benchmark_files",
    "load_suite_from_path",
    "register_harness",
    "run_suite",
]
