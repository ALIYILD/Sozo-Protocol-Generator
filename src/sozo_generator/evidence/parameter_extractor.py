"""
Neuromodulation parameter extractor — extracts structured stimulation
parameters from paper abstracts and titles.

Uses regex-based extraction with fallback to LLM extraction (when available).
Extracted parameters feed into evidence scoring and protocol grounding.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from pydantic import BaseModel, Field

from ..schemas.evidence import ArticleMetadata

logger = logging.getLogger(__name__)


# ── Extraction schema ──────────────────────────────────────────────────


class StimulationParameters(BaseModel):
    """Structured stimulation parameters extracted from a paper."""

    # Modality
    modality: Optional[str] = None  # tDCS, tACS, TMS, rTMS, etc.

    # Target
    brain_target: Optional[str] = None  # DLPFC, M1, SMA, etc.
    laterality: Optional[str] = None  # left, right, bilateral

    # Dosage
    intensity_ma: Optional[float] = None  # in mA
    intensity_v_per_m: Optional[float] = None  # in V/m (for TPS)
    frequency_hz: Optional[float] = None  # in Hz (for tACS, TMS)
    duration_minutes: Optional[float] = None

    # Sessions
    sessions_total: Optional[int] = None
    sessions_per_week: Optional[int] = None
    treatment_weeks: Optional[int] = None

    # Electrode/coil config
    electrode_montage: Optional[str] = None  # e.g. "F3-Fp2", "C3-supraorbital"
    electrode_size_cm2: Optional[float] = None
    coil_type: Optional[str] = None  # figure-8, H-coil, etc.

    # TMS-specific
    pulses_per_session: Optional[int] = None
    motor_threshold_pct: Optional[int] = None  # % of motor threshold
    trains_per_session: Optional[int] = None
    inter_train_interval_s: Optional[float] = None

    # Outcomes
    primary_outcome_measure: Optional[str] = None
    effect_size_d: Optional[float] = None
    sample_size: Optional[int] = None
    p_value: Optional[float] = None

    # Extraction metadata
    extraction_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    fields_extracted: int = 0
    extraction_method: str = "regex"  # regex, llm, manual


@dataclass
class ExtractionResult:
    """Result of parameter extraction for one article."""

    article_pmid: Optional[str] = None
    article_doi: Optional[str] = None
    article_title: str = ""
    parameters: Optional[StimulationParameters] = None
    raw_text_used: str = ""
    extraction_notes: list[str] = field(default_factory=list)


# ── Regex patterns ─────────────────────────────────────────────────────

# Modality detection
_MODALITY_PATTERNS = {
    "tDCS": re.compile(r"\b(?:tDCS|transcranial\s+direct\s+current\s+stimulation)\b", re.I),
    "tACS": re.compile(r"\b(?:tACS|transcranial\s+alternating\s+current\s+stimulation)\b", re.I),
    "rTMS": re.compile(r"\b(?:rTMS|repetitive\s+transcranial\s+magnetic\s+stimulation)\b", re.I),
    "TMS": re.compile(r"\b(?:TMS|transcranial\s+magnetic\s+stimulation)\b", re.I),
    "iTBS": re.compile(r"\b(?:iTBS|intermittent\s+theta[\s-]*burst\s+stimulation)\b", re.I),
    "cTBS": re.compile(r"\b(?:cTBS|continuous\s+theta[\s-]*burst\s+stimulation)\b", re.I),
    "TPS": re.compile(r"\b(?:TPS|transcranial\s+pulse\s+stimulation)\b", re.I),
    "taVNS": re.compile(r"\b(?:taVNS|transcutaneous\s+auricular\s+vagus\s+nerve\s+stimulation)\b", re.I),
    "CES": re.compile(r"\b(?:CES|cranial\s+electrotherapy\s+stimulation)\b", re.I),
    "tFUS": re.compile(r"\b(?:tFUS|transcranial\s+focused\s+ultrasound)\b", re.I),
    "DBS": re.compile(r"\b(?:DBS|deep\s+brain\s+stimulation)\b", re.I),
    "tRNS": re.compile(r"\b(?:tRNS|transcranial\s+random\s+noise\s+stimulation)\b", re.I),
}

# Brain targets
_TARGET_PATTERNS = {
    "DLPFC": re.compile(r"\b(?:DLPFC|dorsolateral\s+prefrontal\s+cortex)\b", re.I),
    "M1": re.compile(r"\b(?:M1|primary\s+motor\s+cortex)\b", re.I),
    "SMA": re.compile(r"\b(?:SMA|supplementary\s+motor\s+area)\b", re.I),
    "DMPFC": re.compile(r"\b(?:DMPFC|dorsomedial\s+prefrontal\s+cortex)\b", re.I),
    "OFC": re.compile(r"\b(?:OFC|orbitofrontal\s+cortex)\b", re.I),
    "V1": re.compile(r"\b(?:V1|primary\s+visual\s+cortex)\b", re.I),
    "STG": re.compile(r"\b(?:STG|superior\s+temporal\s+gyrus)\b", re.I),
    "PPC": re.compile(r"\b(?:PPC|posterior\s+parietal\s+cortex)\b", re.I),
    "cerebellum": re.compile(r"\bcerebellum\b", re.I),
    "F3": re.compile(r"\bF3\b"),
    "F4": re.compile(r"\bF4\b"),
}

# Laterality
_LATERALITY_RE = re.compile(
    r"\b(left|right|bilateral)\b\s*(?:DLPFC|hemisphere|cortex|M1|SMA|PFC)",
    re.I,
)

# Numeric parameters
_INTENSITY_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:mA|milliamp)", re.I)
_FREQUENCY_RE = re.compile(r"(\d+(?:\.\d+)?)\s*Hz", re.I)
_DURATION_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:min(?:ute)?s?|minutes?\b)", re.I,
)
_SESSIONS_TOTAL_RE = re.compile(r"(\d+)\s*sessions?\b", re.I)
_SESSIONS_WEEK_RE = re.compile(
    r"(\d+)\s*(?:sessions?\s+per\s+week|times?\s+(?:per|a)\s+week|days?\s+(?:per|a)\s+week|x\s*/\s*week)",
    re.I,
)
_WEEKS_RE = re.compile(r"(\d+)\s*weeks?\b", re.I)
_SAMPLE_SIZE_RE = re.compile(r"(?:n\s*=\s*|sample\s+(?:size\s+(?:of\s+)?)?|(\d+)\s+(?:participants?|patients?|subjects?)\b)", re.I)
_EFFECT_SIZE_RE = re.compile(r"(?:Cohen['\u2019]?s?\s+)?d\s*=\s*(\d+\.\d+)", re.I)
_P_VALUE_RE = re.compile(r"p\s*[<=]\s*(0?\.\d+)", re.I)
_MOTOR_THRESHOLD_RE = re.compile(r"(\d+)\s*%\s*(?:of\s+)?(?:resting\s+)?(?:motor\s+)?threshold", re.I)
_PULSES_RE = re.compile(r"(\d+)\s*pulses?\b", re.I)
_ELECTRODE_SIZE_RE = re.compile(r"(\d+)\s*cm\s*[²2x×]", re.I)

# Outcome measures (common neuromodulation scales)
_OUTCOME_MEASURES = [
    "HDRS", "HAM-D", "MADRS", "BDI", "PHQ-9",  # depression
    "VAS", "NRS",  # pain
    "MDS-UPDRS", "UPDRS",  # Parkinson's
    "ADAS-Cog", "MMSE", "MoCA",  # cognition
    "CGI", "GAF",  # general
    "PANSS",  # schizophrenia
    "THI",  # tinnitus
    "FMA",  # stroke
    "NIHSS",  # stroke
]
_OUTCOME_RE = re.compile(
    r"\b(" + "|".join(re.escape(m) for m in _OUTCOME_MEASURES) + r")\b",
    re.I,
)

# Montage detection
_MONTAGE_RE = re.compile(
    r"(?:anode|cathode|active|return|reference)\s+(?:over|at|on)\s+"
    r"([A-Z][a-z]*\d?|F[3-8p]|C[3-4z]|P[3-4z]|O[1-2z]|T[3-8]|Fp[12])",
    re.I,
)


class ParameterExtractor:
    """Extracts neuromodulation parameters from article abstracts."""

    def extract(self, article: ArticleMetadata) -> ExtractionResult:
        """Extract stimulation parameters from an article's title + abstract."""
        result = ExtractionResult(
            article_pmid=article.pmid,
            article_doi=article.doi,
            article_title=article.title,
        )

        text = f"{article.title} {article.abstract or ''}"
        result.raw_text_used = text[:2000]

        if len(text.strip()) < 30:
            result.extraction_notes.append("Insufficient text for extraction")
            return result

        params = StimulationParameters()
        fields_found = 0

        # Modality
        for mod_name, pattern in _MODALITY_PATTERNS.items():
            if pattern.search(text):
                params.modality = mod_name
                fields_found += 1
                break

        # Brain target
        for target_name, pattern in _TARGET_PATTERNS.items():
            if pattern.search(text):
                params.brain_target = target_name
                fields_found += 1
                break

        # Laterality
        lat_match = _LATERALITY_RE.search(text)
        if lat_match:
            params.laterality = lat_match.group(1).lower()
            fields_found += 1

        # Intensity
        int_match = _INTENSITY_RE.search(text)
        if int_match:
            params.intensity_ma = float(int_match.group(1))
            fields_found += 1

        # Frequency
        freq_match = _FREQUENCY_RE.search(text)
        if freq_match:
            params.frequency_hz = float(freq_match.group(1))
            fields_found += 1

        # Duration
        dur_match = _DURATION_RE.search(text)
        if dur_match:
            params.duration_minutes = float(dur_match.group(1))
            fields_found += 1

        # Sessions
        sess_match = _SESSIONS_TOTAL_RE.search(text)
        if sess_match:
            params.sessions_total = int(sess_match.group(1))
            fields_found += 1

        sess_week_match = _SESSIONS_WEEK_RE.search(text)
        if sess_week_match:
            params.sessions_per_week = int(sess_week_match.group(1))
            fields_found += 1

        weeks_match = _WEEKS_RE.search(text)
        if weeks_match:
            params.treatment_weeks = int(weeks_match.group(1))
            fields_found += 1

        # Motor threshold
        mt_match = _MOTOR_THRESHOLD_RE.search(text)
        if mt_match:
            params.motor_threshold_pct = int(mt_match.group(1))
            fields_found += 1

        # Pulses
        pulse_match = _PULSES_RE.search(text)
        if pulse_match:
            params.pulses_per_session = int(pulse_match.group(1))
            fields_found += 1

        # Electrode size
        elec_match = _ELECTRODE_SIZE_RE.search(text)
        if elec_match:
            params.electrode_size_cm2 = float(elec_match.group(1))
            fields_found += 1

        # Outcome measure
        outcome_match = _OUTCOME_RE.search(text)
        if outcome_match:
            params.primary_outcome_measure = outcome_match.group(1)
            fields_found += 1

        # Effect size
        es_match = _EFFECT_SIZE_RE.search(text)
        if es_match:
            params.effect_size_d = float(es_match.group(1))
            fields_found += 1

        # P-value
        p_match = _P_VALUE_RE.search(text)
        if p_match:
            params.p_value = float(p_match.group(1))
            fields_found += 1

        # Sample size
        ss_match = _SAMPLE_SIZE_RE.search(text)
        if ss_match:
            val = ss_match.group(1) or ss_match.group(0)
            digits = re.search(r"\d+", val)
            if digits:
                params.sample_size = int(digits.group())
                fields_found += 1

        # Montage
        montage_matches = _MONTAGE_RE.findall(text)
        if montage_matches:
            params.electrode_montage = "-".join(montage_matches[:2])
            fields_found += 1

        # Compute confidence
        params.fields_extracted = fields_found
        params.extraction_confidence = min(1.0, fields_found / 8.0)  # 8 fields = full confidence
        params.extraction_method = "regex"

        result.parameters = params

        if fields_found == 0:
            result.extraction_notes.append("No stimulation parameters found in text")
        else:
            result.extraction_notes.append(
                f"Extracted {fields_found} parameter fields (confidence: {params.extraction_confidence:.2f})"
            )

        return result

    def extract_batch(
        self, articles: list[ArticleMetadata],
    ) -> list[ExtractionResult]:
        """Extract parameters from a batch of articles."""
        results = [self.extract(article) for article in articles]
        extracted_count = sum(
            1 for r in results if r.parameters and r.parameters.fields_extracted > 0
        )
        logger.info(
            "Parameter extraction: %d/%d articles yielded parameters",
            extracted_count, len(articles),
        )
        return results
