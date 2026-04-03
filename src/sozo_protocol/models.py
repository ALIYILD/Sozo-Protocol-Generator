"""
Composable Protocol Engine — atomic steps assembled into treatment sequences.

Inspired by OMNI-BIC's StimulationFunctionDefinition pattern where waveforms
are built from atomic primitives (pulse, pause) composed into sequences.

For Sozo, protocol steps are modality-aware and evidence-linked:
  ProtocolStep (pulse | pause | ramp | monitoring)
    → ProtocolPhase (S | O | Z | O in SOZO sequence)
      → ProtocolSequence (full treatment session)
        → PersonalizedProtocol (patient-specific adaptation)
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ── Step Types ────────────────────────────────────────────────────────────


class StepType(str, Enum):
    PULSE = "pulse"
    PAUSE = "pause"
    RAMP = "ramp"
    MONITORING = "monitoring"  # impedance check, EEG baseline, etc.


class Modality(str, Enum):
    TDCS = "tdcs"
    TPS = "tps"
    TAVNS = "tavns"
    CES = "ces"
    EEG = "eeg"  # monitoring only
    NONE = "none"  # pause/wait steps


class SOZOPhase(str, Enum):
    """The S-O-Z-O multimodal session sequence."""
    STABILIZE = "S"   # taVNS/CES — downshift sympathetic tone
    OPTIMIZE = "O1"   # tDCS — prime target networks
    ZONE = "Z"        # TPS — deep network modulation
    OUTCOME = "O2"    # taVNS/CES + rehab — neuroplasticity window
    PRE = "pre"       # Pre-session (impedance, baseline)
    POST = "post"     # Post-session (outcome measures)


class Laterality(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    BILATERAL = "bilateral"
    MIDLINE = "midline"


# ── Protocol Step (atomic unit) ──────────────────────────────────────────


class ProtocolStep(BaseModel):
    """One atomic step in a treatment protocol.

    Inspired by OMNI-BIC's StimulationFunctionDefinition — each step is
    either a stimulation pulse, a pause, a ramp, or a monitoring action.
    Steps are composed into phases and sequences.
    """
    step_id: str = Field(default_factory=lambda: _uid("step-"))
    step_type: StepType
    modality: Modality = Modality.NONE
    label: str = ""

    # Electrode placement (EEG 10-20 / 10-10 positions)
    electrodes_source: list[str] = Field(default_factory=list)  # anode / TPS target
    electrodes_sink: list[str] = Field(default_factory=list)    # cathode / return
    laterality: Laterality = Laterality.BILATERAL

    # Stimulation parameters (modality-specific)
    intensity_ma: Optional[float] = None      # tDCS current (mA)
    intensity_mj: Optional[float] = None      # TPS energy density (mJ/mm²)
    frequency_hz: Optional[float] = None      # Pulse frequency
    pulse_width_us: Optional[int] = None      # Pulse width (microseconds)
    pulse_count: Optional[int] = None         # Total pulses per step
    duration_ms: int = 0                       # Step duration (milliseconds)
    duration_min: Optional[float] = None       # Convenience: duration in minutes

    # Repetition
    repetitions: int = 1
    inter_rep_pause_ms: int = 0

    # Safety
    max_impedance_kohm: float = 10.0          # Impedance threshold
    ramp_up_ms: int = 0                        # Ramp-up time
    ramp_down_ms: int = 0                      # Ramp-down time

    # Evidence / governance
    evidence_level: str = "medium"
    off_label: bool = True
    requires_consent: bool = True
    rationale: str = ""

    # Extended parameters (modality-specific overflow)
    extra_params: dict[str, Any] = Field(default_factory=dict)

    @field_validator("duration_min", mode="before")
    @classmethod
    def _convert_min_to_ms(cls, v, info):
        return v

    @property
    def duration_total_ms(self) -> int:
        """Total duration including repetitions."""
        if self.duration_min and not self.duration_ms:
            base = int(self.duration_min * 60 * 1000)
        else:
            base = self.duration_ms
        return (base + self.inter_rep_pause_ms) * self.repetitions


# ── Protocol Phase (SOZO sequence phase) ─────────────────────────────────


class ProtocolPhase(BaseModel):
    """One phase of the SOZO multimodal session (S, O, Z, or O)."""
    phase_id: str = Field(default_factory=lambda: _uid("phase-"))
    sozo_phase: SOZOPhase
    label: str = ""
    steps: list[ProtocolStep] = Field(default_factory=list)
    target_duration_min: Optional[float] = None

    @property
    def total_duration_ms(self) -> int:
        return sum(s.duration_total_ms for s in self.steps)

    @property
    def modalities_used(self) -> list[str]:
        return list(set(s.modality.value for s in self.steps if s.modality != Modality.NONE))


# ── Protocol Sequence (full session) ─────────────────────────────────────


class ProtocolSequence(BaseModel):
    """A complete treatment session protocol — composed of SOZO phases.

    This is the top-level protocol object that defines what happens
    during one clinical session.
    """
    sequence_id: str = Field(default_factory=lambda: _uid("seq-"))
    name: str = ""
    condition_slug: str = ""
    tier: str = "fellow"
    version: str = "1.0"

    # Phases in session order
    phases: list[ProtocolPhase] = Field(default_factory=list)

    # Session metadata
    session_number: Optional[int] = None
    total_sessions: Optional[int] = None
    frequency: str = ""  # "3x/week", "daily", etc.

    # Evidence
    evidence_level: str = "medium"
    evidence_pmids: list[str] = Field(default_factory=list)
    off_label: bool = True

    # Governance
    requires_doctor_authorization: bool = True
    requires_informed_consent: bool = True

    @property
    def total_duration_ms(self) -> int:
        return sum(p.total_duration_ms for p in self.phases)

    @property
    def total_duration_min(self) -> float:
        return self.total_duration_ms / 60000.0

    @property
    def all_modalities(self) -> list[str]:
        mods = set()
        for p in self.phases:
            mods.update(p.modalities_used)
        return sorted(mods)

    @property
    def all_steps(self) -> list[ProtocolStep]:
        return [s for p in self.phases for s in p.steps]


# ── Personalized Protocol ────────────────────────────────────────────────


class FilterCoefficients(BaseModel):
    """Digital filter coefficients for closed-loop / EEG-driven adaptation.

    Inspired by OMNI-BIC's distributedStimEnableRequest which passes
    IIR filter B/A coefficients for real-time signal processing.
    """
    b: list[float] = Field(default_factory=list)  # Numerator
    a: list[float] = Field(default_factory=list)  # Denominator
    filter_type: str = "bandpass"  # bandpass, lowpass, highpass, notch
    frequency_band: str = ""  # "beta", "alpha", "theta", "gamma"


class PersonalizedProtocol(BaseModel):
    """A patient-specific adaptation of a base protocol.

    Adds EEG-derived filter coefficients, target phase, trigger thresholds,
    and per-patient parameter overrides on top of a standard sequence.
    """
    personalization_id: str = Field(default_factory=lambda: _uid("pers-"))
    base_sequence_id: str = ""
    patient_id: str = ""
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    # EEG-derived parameters
    eeg_filter: Optional[FilterCoefficients] = None
    target_frequency_band: str = ""  # "beta", "alpha"
    target_phase_degrees: Optional[float] = None
    trigger_threshold: Optional[float] = None
    sensing_channel: Optional[int] = None

    # Patient-specific overrides
    intensity_adjustment_pct: float = 0.0  # e.g. -20% for sensitive patients
    duration_adjustment_pct: float = 0.0
    excluded_electrodes: list[str] = Field(default_factory=list)  # contraindicated positions
    adapted_parameters: dict[str, Any] = Field(default_factory=dict)

    # Assessment-driven
    baseline_scores: dict[str, float] = Field(default_factory=dict)
    phenotype_slug: str = ""
    severity_level: str = ""

    # Governance
    clinician_id: str = ""
    approval_status: str = "pending"  # pending, approved, rejected
