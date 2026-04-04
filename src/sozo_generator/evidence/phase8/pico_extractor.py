"""
Phase 8 Evidence Ingestion — PICO Extractor
============================================
Calls an LLM (Anthropic Claude primary, OpenAI GPT-4o fallback) to extract
structured PICO + protocol parameters from neuromodulation research abstracts.

Typical usage::

    from sozo_generator.evidence.phase8.pico_extractor import PICOExtractor

    extractor = PICOExtractor(
        anthropic_api_key="sk-ant-...",
        openai_api_key="sk-...",
    )
    results = extractor.extract_batch(
        papers=paper_list,
        condition_slug="depression",
        condition_name="Major Depressive Disorder",
        primary_modalities=["tDCS", "TMS"],
    )
    for pico, params in results:
        ...
"""

from __future__ import annotations

import json
import logging
import math
import re
import time
from typing import Literal, Optional

from .models import PaperRaw, PICOExtract, ProtocolParameters

try:
    import anthropic
except ImportError:  # pragma: no cover
    anthropic = None  # type: ignore[assignment]

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level helper
# ---------------------------------------------------------------------------

def grade_evidence(
    study_design: Optional[str],
    pico: Optional[PICOExtract],
) -> Optional[str]:
    """
    Assign a GRADE-style evidence grade based on study design and PICO quality.

    Grades are assigned as follows:

    - **A** — meta-analysis or systematic review with high-confidence extraction.
    - **B** — RCT with high or medium extraction confidence.
    - **C** — cohort or narrative review.
    - **D** — pilot study or case series.
    - **expert_opinion** — no recognised study design, or relevance_score <= 2.

    Parameters
    ----------
    study_design:
        Coarse study-design label (e.g. ``'RCT'``, ``'meta_analysis'``).
        Case-insensitive. ``None`` is treated as unknown.
    pico:
        The :class:`PICOExtract` produced for the paper.  ``None`` is treated
        as unavailable / low-quality extraction.

    Returns
    -------
    Optional[str]
        One of ``'A'``, ``'B'``, ``'C'``, ``'D'``, ``'expert_opinion'``,
        or ``None`` when both inputs are ``None``.
    """
    if study_design is None and pico is None:
        return None

    # Low relevance always → expert_opinion regardless of design
    if pico is not None and pico.relevance_score is not None:
        if pico.relevance_score <= 2:
            return "expert_opinion"

    # Normalise to underscores so both "meta-analysis" and "meta_analysis" match.
    design = (study_design or "").lower().strip().replace("-", "_")
    confidence = pico.extraction_confidence if pico else None

    if design in {"meta_analysis", "systematic_review"}:
        if confidence == "high":
            return "A"
        return "B"

    if design == "rct":
        if confidence in {"high", "medium"}:
            return "B"
        return "C"

    if design in {"cohort", "review"}:
        return "C"

    if design in {"pilot", "case_series"}:
        return "D"

    # Unknown or unrecognised design
    return "expert_opinion"


# ---------------------------------------------------------------------------
# PICOExtractor
# ---------------------------------------------------------------------------

class PICOExtractor:
    """
    Extract structured PICO + protocol parameters from paper abstracts via LLM.

    Anthropic Claude is tried first; OpenAI GPT-4o is used as a fallback if
    Anthropic is unavailable or raises an error.  Both can be disabled by
    omitting the corresponding API key.

    Papers are processed in batches (default: 5 per LLM call) to keep prompt
    sizes manageable and to reduce total API round-trips.

    Parameters
    ----------
    anthropic_api_key:
        Anthropic API key.  If ``None``, Anthropic is skipped.
    openai_api_key:
        OpenAI API key.  If ``None``, OpenAI is skipped.
    batch_size:
        Number of papers to include in a single LLM prompt.
    max_retries:
        Maximum number of retry attempts for a failing LLM call.
    retry_delay_s:
        Base delay in seconds for exponential backoff between retries.
    min_relevance_score:
        Papers whose ``relevance_score`` is below this threshold are marked
        ``irrelevant=True`` after extraction.  Default is ``2`` (exclude
        score-1 papers only).
    model_anthropic:
        Anthropic model identifier.
    model_openai:
        OpenAI model identifier.
    """

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        batch_size: int = 5,
        max_retries: int = 3,
        retry_delay_s: float = 2.0,
        min_relevance_score: int = 2,
        model_anthropic: str = "claude-sonnet-4-6",
        model_openai: str = "gpt-4o",
    ) -> None:
        self._anthropic_api_key = anthropic_api_key
        self._openai_api_key = openai_api_key
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.retry_delay_s = retry_delay_s
        self.min_relevance_score = min_relevance_score
        self.model_anthropic = model_anthropic
        self.model_openai = model_openai

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_batch(
        self,
        papers: list[PaperRaw],
        condition_slug: str,
        condition_name: str,
        primary_modalities: list[str],
    ) -> list[tuple[Optional[PICOExtract], Optional[ProtocolParameters]]]:
        """
        Run PICO + protocol extraction for all papers.

        The list is split into sub-batches of at most ``batch_size`` papers.
        Each sub-batch is sent to the LLM with automatic retry and fallback.
        Results are validated with Pydantic; individual failures do not abort
        the overall run.

        Parameters
        ----------
        papers:
            List of raw paper records to process.
        condition_slug:
            Machine-readable condition identifier (e.g. ``'depression'``).
        condition_name:
            Human-readable condition name (e.g. ``'Major Depressive Disorder'``).
        primary_modalities:
            Modality labels that are the focus of this search run
            (e.g. ``['tDCS', 'TMS']``).

        Returns
        -------
        list[tuple[Optional[PICOExtract], Optional[ProtocolParameters]]]
            One tuple per input paper, in the same order.  Both elements
            of a tuple can be ``None`` when extraction fails for that paper.
        """
        total = len(papers)
        results: list[tuple[Optional[PICOExtract], Optional[ProtocolParameters]]] = []

        for batch_start in range(0, total, self.batch_size):
            batch_end = min(batch_start + self.batch_size, total)
            batch = papers[batch_start:batch_end]

            logger.info(
                "Extracting PICO for papers %d-%d of %d (condition: %s)",
                batch_start + 1,
                batch_end,
                total,
                condition_slug,
            )

            raw_dicts: list[dict] = []
            attempt = 0
            last_exc: Optional[Exception] = None

            while attempt < self.max_retries:
                try:
                    raw_dicts = self._extract_single_batch(
                        papers_batch=batch,
                        condition_slug=condition_slug,
                        condition_name=condition_name,
                        primary_modalities=primary_modalities,
                    )
                    break  # success
                except Exception as exc:
                    last_exc = exc
                    delay = self.retry_delay_s * math.pow(2, attempt)
                    logger.error(
                        "LLM batch extraction failed (attempt %d/%d) for papers %d-%d: %s — "
                        "retrying in %.1fs",
                        attempt + 1,
                        self.max_retries,
                        batch_start + 1,
                        batch_end,
                        exc,
                        delay,
                    )
                    time.sleep(delay)
                    attempt += 1

            if not raw_dicts and last_exc is not None:
                logger.error(
                    "All %d retries exhausted for papers %d-%d; returning (None, None) for "
                    "each paper in this batch.",
                    self.max_retries,
                    batch_start + 1,
                    batch_end,
                )
                results.extend([(None, None)] * len(batch))
                continue

            # Build a lookup dict: paper_index → raw dict
            index_to_raw: dict[int, dict] = {}
            for raw in raw_dicts:
                try:
                    idx = int(raw.get("paper_index", -1))
                    if idx >= 0:
                        index_to_raw[idx] = raw
                except (TypeError, ValueError):
                    pass

            for local_idx, paper in enumerate(batch):
                global_idx = batch_start + local_idx
                logger.debug("Processing paper: %s", paper.title)

                raw = index_to_raw.get(local_idx)
                if raw is None:
                    logger.error(
                        "No extraction result for paper index %d ('%s'); returning (None, None).",
                        local_idx,
                        paper.title,
                    )
                    results.append((None, None))
                    continue

                pico = self._parse_pico(raw, global_idx, paper.title)
                params = self._parse_protocol_params(raw, global_idx, paper.title)

                # Apply minimum relevance filter
                if (
                    pico is not None
                    and pico.relevance_score is not None
                    and pico.relevance_score < self.min_relevance_score
                ):
                    pico.irrelevant = True
                    if not pico.irrelevance_reason:
                        pico.irrelevance_reason = (
                            f"relevance_score {pico.relevance_score} "
                            f"below threshold {self.min_relevance_score}"
                        )

                results.append((pico, params))

        return results

    # ------------------------------------------------------------------
    # Internal — batch orchestration
    # ------------------------------------------------------------------

    def _extract_single_batch(
        self,
        papers_batch: list[PaperRaw],
        condition_slug: str,
        condition_name: str,
        primary_modalities: list[str],
    ) -> list[dict]:
        """
        Call the LLM for one batch of up to ``batch_size`` papers.

        Tries Anthropic first, then OpenAI as a fallback.  Raises if both
        providers fail or neither is configured.

        Parameters
        ----------
        papers_batch:
            The sub-list of papers to extract from.
        condition_slug:
            Machine-readable condition identifier (unused in prompt but kept
            for future logging).
        condition_name:
            Human-readable condition name forwarded to the prompt.
        primary_modalities:
            Modality labels forwarded to the prompt.

        Returns
        -------
        list[dict]
            Parsed list of extraction dicts (one per paper in the batch).
        """
        prompt = self._build_prompt(
            papers_batch=papers_batch,
            condition_name=condition_name,
            primary_modalities=primary_modalities,
        )

        response_text: Optional[str] = None
        anthropic_error: Optional[Exception] = None

        # --- Anthropic (primary) ---
        if self._anthropic_api_key and anthropic is not None:
            try:
                response_text = self._call_anthropic(prompt)
            except Exception as exc:
                anthropic_error = exc
                logger.error(
                    "Anthropic call failed: %s — falling back to OpenAI.", exc
                )

        # --- OpenAI (fallback) ---
        if response_text is None:
            if self._openai_api_key and openai is not None:
                response_text = self._call_openai(prompt)
            else:
                if anthropic_error:
                    raise anthropic_error
                raise RuntimeError(
                    "No LLM provider is configured (both anthropic_api_key and "
                    "openai_api_key are absent or libraries not installed)."
                )

        return self._parse_llm_response(response_text, n_papers=len(papers_batch))

    # ------------------------------------------------------------------
    # Internal — LLM calls
    # ------------------------------------------------------------------

    def _call_anthropic(self, prompt: str) -> str:
        """
        Call the Anthropic Messages API and return the raw text response.

        Parameters
        ----------
        prompt:
            The full user-turn prompt text.

        Returns
        -------
        str
            Raw text content of the first response block.

        Raises
        ------
        anthropic.RateLimitError
            Re-raised so the retry loop in :meth:`extract_batch` can back off.
        anthropic.APIError
            Re-raised for the same reason.
        RuntimeError
            If the ``anthropic`` package is not installed.
        """
        if anthropic is None:
            raise RuntimeError(
                "The 'anthropic' package is not installed.  "
                "Run: pip install anthropic"
            )

        client = anthropic.Anthropic(api_key=self._anthropic_api_key)
        try:
            response = client.messages.create(
                model=self.model_anthropic,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
        except anthropic.RateLimitError:
            raise
        except anthropic.APIError:
            raise

        return response.content[0].text

    def _call_openai(self, prompt: str) -> str:
        """
        Call the OpenAI Chat Completions API and return the raw text response.

        The ``json_object`` response format is requested to nudge the model
        toward valid JSON output; the returned string is the raw message
        content (not yet parsed).

        Parameters
        ----------
        prompt:
            The full user-turn prompt text.

        Returns
        -------
        str
            Raw text content of the first choice message.

        Raises
        ------
        RuntimeError
            If the ``openai`` package is not installed.
        openai.OpenAIError
            Propagated directly for caller handling.
        """
        if openai is None:
            raise RuntimeError(
                "The 'openai' package is not installed.  "
                "Run: pip install openai"
            )

        client = openai.OpenAI(api_key=self._openai_api_key)
        response = client.chat.completions.create(
            model=self.model_openai,
            max_tokens=4096,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    # ------------------------------------------------------------------
    # Internal — prompt builder
    # ------------------------------------------------------------------

    def _build_prompt(
        self,
        papers_batch: list[PaperRaw],
        condition_name: str,
        primary_modalities: list[str],
    ) -> str:
        """
        Build the structured extraction prompt for a batch of papers.

        The prompt instructs the LLM to extract PICO fields and protocol
        parameters for each paper and return a JSON array—one object per
        paper, indexed to match the input order.

        Parameters
        ----------
        papers_batch:
            Sub-list of papers to include in this prompt.
        condition_name:
            Human-readable condition name (e.g. ``'Major Depressive Disorder'``).
        primary_modalities:
            Modality labels to orient the extraction
            (e.g. ``['tDCS', 'TMS']``).

        Returns
        -------
        str
            The complete prompt string ready to send to the LLM.
        """
        modalities_str = ", ".join(primary_modalities) if primary_modalities else "neuromodulation"

        paper_blocks: list[str] = []
        for idx, paper in enumerate(papers_batch):
            abstract_text = paper.abstract or paper.s2_tldr or ""
            lines = [
                f"--- Paper {idx} ---",
                f"Title: {paper.title}",
                f"Year: {paper.year or 'unknown'}",
                f"Journal: {paper.journal or 'unknown'}",
            ]
            if abstract_text:
                lines.append(f"Abstract: {abstract_text}")
            else:
                lines.append("Abstract: [NOT AVAILABLE]")
            paper_blocks.append("\n".join(lines))

        papers_section = "\n\n".join(paper_blocks)

        prompt = f"""You are a clinical research analyst specialising in neuromodulation. \
Your task is to extract structured data from research paper abstracts.

CONDITION: {condition_name}
PRIMARY MODALITIES OF INTEREST: {modalities_str}

You will be given {len(papers_batch)} paper(s). For each paper, extract PICO (Population, \
Intervention, Comparator, Outcomes) fields and neuromodulation protocol parameters from the \
abstract text.

PAPERS:

{papers_section}

INSTRUCTIONS:

1. Return a JSON array with exactly {len(papers_batch)} object(s), one per paper, in the same \
order as the input. Each object must have the key "paper_index" (0-based integer matching the \
paper's position above).

2. For "relevance_score", use this scale:
   1 = Not about neuromodulation at all (basic sciences, animal-only, completely off-topic)
   2 = Background or review without any protocol data
   3 = Relevant to neuromodulation but no specific parameters reported
   4 = Relevant, some protocol parameters present
   5 = Directly provides protocol parameters for {condition_name}

3. Set "irrelevant": true ONLY if relevance_score = 1 (basic science, animal only, \
completely off-topic). Otherwise set "irrelevant": false.

4. In "protocol_params", set individual fields to null if the paper does not report that \
specific parameter. Set the entire "protocol_params" value to null (not an empty object) if the \
paper does not describe a stimulation protocol at all.

5. If no abstract and no tldr is available for a paper (abstract shown as [NOT AVAILABLE]), \
set "irrelevant": true and "irrelevance_reason": "no_abstract".

6. "extraction_confidence" must be one of: "high", "medium", or "low".

7. Return ONLY a valid JSON array. No markdown, no code fences, no explanation text. The \
response must begin with "[" and end with "]".

REQUIRED OUTPUT SCHEMA (one element per paper):

[
  {{
    "paper_index": 0,
    "pico": {{
      "population": "string or null",
      "population_n": integer_or_null,
      "intervention": "string or null",
      "comparator": "string or null",
      "outcomes_primary": "string or null",
      "outcomes_secondary": "string or null",
      "result_summary": "string or null",
      "effect_size": "string or null",
      "p_value": "string or null",
      "follow_up_weeks": integer_or_null,
      "conclusion": "string or null",
      "relevance_score": 1_to_5_integer,
      "irrelevant": true_or_false,
      "irrelevance_reason": "string or null",
      "extraction_confidence": "high" | "medium" | "low"
    }},
    "protocol_params": {{
      "modality": "string or null",
      "target_region": "string or null",
      "frequency_hz": number_or_null,
      "intensity": "string or null",
      "intensity_value": number_or_null,
      "intensity_unit": "pct_rmt" | "mA" | "mW_cm2" | "gauss" | "other" | null,
      "pulse_type": "string or null",
      "pulses_per_session": integer_or_null,
      "sessions_total": integer_or_null,
      "sessions_per_week": integer_or_null,
      "session_duration_min": integer_or_null,
      "electrode_montage": "string or null",
      "anode_position": "string or null",
      "cathode_position": "string or null",
      "coil_type": "string or null",
      "wavelength_nm": number_or_null,
      "energy_density_j_cm2": number_or_null,
      "response_rate_pct": number_or_null,
      "remission_rate_pct": number_or_null,
      "primary_outcome_measure": "string or null"
    }}
  }}
]

Remember: "protocol_params" should be null (not an empty object) when the paper does not \
describe a stimulation protocol."""

        return prompt

    # ------------------------------------------------------------------
    # Internal — response parsing
    # ------------------------------------------------------------------

    def _parse_llm_response(self, response_text: str, n_papers: int) -> list[dict]:
        """
        Parse a JSON array from the raw LLM response text.

        Attempts two strategies before giving up:

        1. Direct ``json.loads`` on the stripped response.
        2. Regex extraction of the first ``[...]`` block in the text.

        Parameters
        ----------
        response_text:
            Raw string returned by the LLM.
        n_papers:
            Expected number of paper results (used only for logging).

        Returns
        -------
        list[dict]
            Parsed list of extraction dicts.  Returns an empty list on failure.
        """
        text = response_text.strip()

        # Strategy 1: direct parse
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return parsed
            # Some models wrap arrays in an object, e.g. {"results": [...]}
            if isinstance(parsed, dict):
                for value in parsed.values():
                    if isinstance(value, list):
                        logger.debug(
                            "LLM returned a JSON object; extracted nested array "
                            "(%d items).",
                            len(value),
                        )
                        return value
            logger.error(
                "LLM response parsed as JSON but is not an array (type: %s).",
                type(parsed).__name__,
            )
            return []
        except json.JSONDecodeError:
            pass

        # Strategy 2: regex extraction of first [...] block
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
                if isinstance(parsed, list):
                    logger.debug(
                        "Extracted JSON array via regex (%d items for %d expected papers).",
                        len(parsed),
                        n_papers,
                    )
                    return parsed
            except json.JSONDecodeError as exc:
                logger.error(
                    "Regex-extracted JSON array failed to parse: %s", exc
                )

        logger.error(
            "Failed to parse LLM response as a JSON array for %d papers. "
            "Raw response (first 500 chars): %s",
            n_papers,
            text[:500],
        )
        return []

    # ------------------------------------------------------------------
    # Internal — Pydantic coercion helpers
    # ------------------------------------------------------------------

    def _parse_pico(
        self,
        raw: dict,
        paper_index: int,
        paper_title: str,
    ) -> Optional[PICOExtract]:
        """
        Validate and coerce the ``'pico'`` sub-dict from an extraction result.

        Parameters
        ----------
        raw:
            The full per-paper dict returned by the LLM.
        paper_index:
            Global paper index (for logging context).
        paper_title:
            Paper title (for logging context).

        Returns
        -------
        Optional[PICOExtract]
            Validated model, or ``None`` on Pydantic validation failure.
        """
        pico_raw = raw.get("pico")
        if pico_raw is None:
            logger.error(
                "Paper %d ('%s'): LLM result missing 'pico' key; returning None.",
                paper_index,
                paper_title,
            )
            return None

        try:
            return PICOExtract.model_validate(pico_raw)
        except Exception as exc:
            logger.error(
                "Paper %d ('%s'): PICOExtract validation error: %s",
                paper_index,
                paper_title,
                exc,
            )
            return None

    def _parse_protocol_params(
        self,
        raw: dict,
        paper_index: int,
        paper_title: str,
    ) -> Optional[ProtocolParameters]:
        """
        Validate and coerce the ``'protocol_params'`` sub-dict from an
        extraction result.

        Parameters
        ----------
        raw:
            The full per-paper dict returned by the LLM.
        paper_index:
            Global paper index (for logging context).
        paper_title:
            Paper title (for logging context).

        Returns
        -------
        Optional[ProtocolParameters]
            Validated model, or ``None`` when the LLM indicated no protocol
            was described or on Pydantic validation failure.
        """
        params_raw = raw.get("protocol_params")
        if params_raw is None:
            # Legitimate: paper does not describe a protocol
            return None

        try:
            return ProtocolParameters.model_validate(params_raw)
        except Exception as exc:
            logger.error(
                "Paper %d ('%s'): ProtocolParameters validation error: %s",
                paper_index,
                paper_title,
                exc,
            )
            return None
