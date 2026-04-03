"""
Phase 8 Evidence Ingestion — Batch PICO Extraction
====================================================
Sends paper abstracts + Consensus findings to an LLM (Anthropic Claude
or OpenAI GPT) and extracts structured PICO + neuromodulation protocol
parameters for each paper.

Design goals
------------
- Strict JSON output enforced by a schema-constrained system prompt.
- Handles partial failures: a single bad extraction does not block the batch.
- Retries on LLM rate-limit and transient errors.
- Filters irrelevant papers before sending (saves API cost).
- Logs every extraction for audit.

Providers
---------
Set ``ANTHROPIC_API_KEY`` (preferred) **or** ``OPENAI_API_KEY``
(fallback) as environment variables, or pass them explicitly.

Usage
-----
::

    from sozo_generator.evidence.phase8.batch_pico_extract import batch_pico_extract
    from sozo_generator.evidence.phase8.models import EvidenceRecord

    records: list[EvidenceRecord] = [...]
    enriched = batch_pico_extract(records, condition_slug="depression")
    for r in enriched:
        print(r.pico, r.protocol_params)
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Optional, Sequence

from pydantic import ValidationError

from .models import EvidenceRecord, PICOExtract, ProtocolParameters

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
_OPENAI_MODEL: str = "gpt-4o-mini"
_MAX_ABSTRACT_CHARS: int = 3_000   # truncate abstracts to control token cost
_RETRY_ATTEMPTS: int = 3
_RETRY_BACKOFF_BASE: float = 5.0   # seconds

# Relevance filter: skip papers whose title/abstract contain none of these terms
_RELEVANCE_KEYWORDS: frozenset[str] = frozenset(
    [
        "tDCS", "tdcs", "TMS", "rTMS", "iTBS", "TBS",
        "transcranial", "neuromodulation", "neurostimulation",
        "stimulation", "vagus", "photobiomodulation", "PBM",
        "neurofeedback", "brain stimulation", "electromagnetic",
        "PEMF", "CES", "Alpha-Stim", "taVNS", "tVNS",
        "transcranial pulse", "TPS", "NEUROLITH",
        "non-invasive", "noninvasive",
    ]
)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are a clinical research analyst extracting structured PICO and protocol data from neuromodulation papers.

For each paper, return a single JSON object matching the schema below.
Respond ONLY with valid JSON — no markdown, no preamble, no explanation.

REQUIRED SCHEMA:
{
  "population": "<string: patient group, diagnosis, age range>",
  "intervention": "<string: modality, target, parameters summary>",
  "comparator": "<string: sham / active control / waitlist / null if not found>",
  "primary_outcome": "<string: primary outcome measure and result>",
  "secondary_outcomes": ["<string>", ...],
  "outcome_direction": "<one of: positive, negative, null, mixed, not_reported>",
  "sample_size": <integer or null>,
  "study_design": "<one of: RCT, meta_analysis, systematic_review, cohort, pilot, case_series, review, other>",
  "modality": "<one of: tDCS, TMS, taVNS, CES, PBM, PEMF, NFB, TPS, multimodal, other, null>",
  "target_region": "<string: brain region targeted, e.g. left DLPFC, M1, SMA — null if not found>",
  "laterality": "<one of: left, right, bilateral, null>",
  "frequency_hz": <number or null>,
  "intensity": <number or null>,
  "intensity_unit": "<one of: pct_rmt, mA, mW_cm2, gauss, other, null>",
  "pulse_width_us": <number or null>,
  "sessions_total": <integer or null>,
  "sessions_per_week": <number or null>,
  "session_duration_min": <number or null>,
  "weeks_total": <number or null>,
  "is_relevant": <true or false>,
  "irrelevance_reason": "<string if is_relevant=false, else null>",
  "extraction_confidence": "<one of: high, medium, low>",
  "extraction_notes": "<brief notes on ambiguities or missing data, or null>"
}

Rules:
- Set is_relevant=false and fill irrelevance_reason if the paper does NOT describe a neuromodulation intervention in humans.
- Use null for any field the paper does not report.
- Do not hallucinate values — only extract what is stated in the abstract.
- extraction_confidence should be "high" when most fields are extractable, "low" when abstract is missing or sparse.
"""

# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def batch_pico_extract(
    records: Sequence[EvidenceRecord],
    condition_slug: str,
    anthropic_api_key: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    batch_size: int = 10,
    skip_irrelevance_filter: bool = False,
) -> list[EvidenceRecord]:
    """
    Enrich a list of :class:`EvidenceRecord` objects with LLM-extracted
    PICO + protocol parameters.

    The function mutates a **copy** of each record and returns the enriched
    list.  The original list is not modified.

    Parameters
    ----------
    records:
        Records to enrich.  Records that already have ``pico`` set are skipped.
    condition_slug:
        Condition identifier (e.g. ``"depression"``).  Logged for audit.
    anthropic_api_key:
        Anthropic API key.  Falls back to ``ANTHROPIC_API_KEY`` env var.
    openai_api_key:
        OpenAI API key.  Falls back to ``OPENAI_API_KEY`` env var.
    batch_size:
        How many papers to process per LLM call.  Lower values reduce latency
        and the cost of a single failure.  Recommended: 5–10.
    skip_irrelevance_filter:
        When True, disable the keyword pre-filter and send all papers to the LLM.

    Returns
    -------
    list[EvidenceRecord]
        Enriched records (same length as input; failed extractions leave
        ``pico=None`` and ``protocol_params=None``).
    """
    ant_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    oai_key = openai_api_key or os.environ.get("OPENAI_API_KEY", "")

    provider = _select_provider(ant_key, oai_key)
    if provider is None:
        logger.warning(
            "batch_pico_extract: no LLM API key configured — "
            "returning records without PICO enrichment."
        )
        return list(records)

    enriched: list[EvidenceRecord] = []
    pending: list[EvidenceRecord] = []
    skipped_pico_already: int = 0
    skipped_irrelevant: int = 0

    for rec in records:
        if rec.pico is not None:
            enriched.append(rec)
            skipped_pico_already += 1
            continue
        if not skip_irrelevance_filter and not _is_likely_relevant(rec):
            rec_copy = rec.model_copy(
                update={"included": False, "exclusion_reason": "pre-filter: no neuromodulation keywords"}
            )
            enriched.append(rec_copy)
            skipped_irrelevant += 1
            continue
        pending.append(rec)

    logger.info(
        "[%s] PICO extraction: %d pending, %d already done, %d pre-filtered",
        condition_slug,
        len(pending),
        skipped_pico_already,
        skipped_irrelevant,
    )

    # Process in batches
    for batch_start in range(0, len(pending), batch_size):
        batch = pending[batch_start : batch_start + batch_size]
        enriched_batch = _extract_batch(
            batch,
            condition_slug=condition_slug,
            provider=provider,
            ant_key=ant_key,
            oai_key=oai_key,
        )
        enriched.extend(enriched_batch)
        logger.info(
            "[%s] Batch %d–%d done (%d/%d total pending)",
            condition_slug,
            batch_start + 1,
            batch_start + len(batch),
            min(batch_start + batch_size, len(pending)),
            len(pending),
        )

    return enriched


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------


def _extract_batch(
    records: list[EvidenceRecord],
    condition_slug: str,
    provider: str,
    ant_key: str,
    oai_key: str,
) -> list[EvidenceRecord]:
    """Extract PICO for a single batch; returns enriched records."""
    prompts = [_build_paper_prompt(rec) for rec in records]
    results: list[Optional[dict]] = []

    for i, (rec, prompt) in enumerate(zip(records, prompts)):
        raw_json = _call_llm_with_retry(
            prompt=prompt,
            provider=provider,
            ant_key=ant_key,
            oai_key=oai_key,
            record_label=f"{condition_slug}[{i}] {rec.paper.title[:60]}",
        )
        results.append(raw_json)

    return [_apply_extraction(rec, result) for rec, result in zip(records, results)]


def _build_paper_prompt(rec: EvidenceRecord) -> str:
    """Construct the user-turn prompt for a single paper."""
    abstract = (rec.paper.abstract or "")[:_MAX_ABSTRACT_CHARS]
    claim = ""
    if rec.consensus_finding and rec.consensus_finding.claim:
        claim = f"\nConsensus claim: {rec.consensus_finding.claim}"

    return (
        f"Title: {rec.paper.title}\n"
        f"Authors: {', '.join(rec.paper.authors[:3])}{'...' if len(rec.paper.authors) > 3 else ''}\n"
        f"Year: {rec.paper.year or 'unknown'}\n"
        f"Journal: {rec.paper.journal or 'unknown'}\n"
        f"Study design hint: {rec.paper.study_design or 'unknown'}\n"
        f"{claim}\n"
        f"Abstract:\n{abstract or '[no abstract available]'}\n"
        f"\nExtract PICO and protocol parameters as JSON."
    )


def _apply_extraction(
    rec: EvidenceRecord,
    raw: Optional[dict],
) -> EvidenceRecord:
    """Merge an extraction result dict into a record copy."""
    if raw is None:
        return rec

    try:
        pico = PICOExtract(
            population=raw.get("population"),
            intervention=raw.get("intervention"),
            comparator=raw.get("comparator"),
            primary_outcome=raw.get("primary_outcome"),
            secondary_outcomes=raw.get("secondary_outcomes") or [],
            outcome_direction=raw.get("outcome_direction"),  # type: ignore[arg-type]
            sample_size=raw.get("sample_size"),
            study_design=raw.get("study_design"),
            extraction_confidence=raw.get("extraction_confidence"),  # type: ignore[arg-type]
            extraction_notes=raw.get("extraction_notes"),
        )
    except (ValidationError, TypeError) as exc:
        logger.warning("PICO validation failed for %r: %s", rec.paper.title[:60], exc)
        return rec

    protocol_params: Optional[ProtocolParameters] = None
    if raw.get("modality"):
        try:
            protocol_params = ProtocolParameters(
                modality=raw.get("modality"),
                target_region=raw.get("target_region"),
                laterality=raw.get("laterality"),
                frequency_hz=raw.get("frequency_hz"),
                intensity=raw.get("intensity"),
                intensity_unit=raw.get("intensity_unit"),
                pulse_width_us=raw.get("pulse_width_us"),
                sessions_total=raw.get("sessions_total"),
                sessions_per_week=raw.get("sessions_per_week"),
                session_duration_min=raw.get("session_duration_min"),
                weeks_total=raw.get("weeks_total"),
            )
        except (ValidationError, TypeError) as exc:
            logger.warning(
                "ProtocolParameters validation failed for %r: %s",
                rec.paper.title[:60],
                exc,
            )

    is_relevant = bool(raw.get("is_relevant", True))
    exclusion_reason = raw.get("irrelevance_reason") if not is_relevant else None

    return rec.model_copy(
        update={
            "pico": pico,
            "protocol_params": protocol_params,
            "included": is_relevant,
            "exclusion_reason": exclusion_reason,
        }
    )


# ---------------------------------------------------------------------------
# LLM call helpers
# ---------------------------------------------------------------------------


def _call_llm_with_retry(
    prompt: str,
    provider: str,
    ant_key: str,
    oai_key: str,
    record_label: str = "",
) -> Optional[dict]:
    """Call the LLM and return parsed JSON dict, or None on failure."""
    for attempt in range(1, _RETRY_ATTEMPTS + 1):
        try:
            raw_text = _call_llm(prompt, provider, ant_key, oai_key)
            return _parse_json_response(raw_text)
        except Exception as exc:  # noqa: BLE001
            wait = _RETRY_BACKOFF_BASE * attempt
            logger.warning(
                "LLM extraction attempt %d/%d failed for %r: %s — retrying in %.1fs",
                attempt,
                _RETRY_ATTEMPTS,
                record_label,
                exc,
                wait,
            )
            time.sleep(wait)

    logger.error("LLM extraction: all %d attempts failed for %r", _RETRY_ATTEMPTS, record_label)
    return None


def _call_llm(prompt: str, provider: str, ant_key: str, oai_key: str) -> str:
    """Dispatch to the appropriate LLM provider."""
    if provider == "anthropic":
        return _call_anthropic(prompt, ant_key)
    return _call_openai(prompt, oai_key)


def _call_anthropic(prompt: str, api_key: str) -> str:
    """Call Anthropic Messages API."""
    try:
        import anthropic  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "anthropic package is required.  Install with: pip install anthropic"
        ) from exc

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=_ANTHROPIC_MODEL,
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _call_openai(prompt: str, api_key: str) -> str:
    """Call OpenAI Chat Completions API."""
    try:
        from openai import OpenAI  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "openai package is required.  Install with: pip install openai"
        ) from exc

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=_OPENAI_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1024,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content or ""


def _parse_json_response(text: str) -> Optional[dict]:
    """Parse JSON from LLM response, stripping markdown fences if present."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # Strip opening and closing ``` fences
        inner = "\n".join(
            l for l in lines if not l.strip().startswith("```")
        )
        text = inner.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        logger.warning("JSON parse failed: %s — raw text: %r", exc, text[:200])
        return None


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def _select_provider(ant_key: str, oai_key: str) -> Optional[str]:
    """Return 'anthropic' or 'openai' based on key availability."""
    if ant_key:
        return "anthropic"
    if oai_key:
        return "openai"
    return None


def _is_likely_relevant(rec: EvidenceRecord) -> bool:
    """Return True if the record is likely neuromodulation-relevant."""
    text = " ".join(
        filter(
            None,
            [rec.paper.title, rec.paper.abstract, rec.paper.s2_tldr],
        )
    )
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in _RELEVANCE_KEYWORDS)
