"""
EEG / QEEG data models for the Sozo Protocol Generator.

Provides typed Pydantic v2 models for:
- Spectral band power (absolute, relative, z-scored)
- Channel-level and recording-level EEG data
- Asymmetry indices, coherence, and connectivity matrices
- Source localization (sLORETA / eLORETA / beamformer)
- Extracted EEG features for protocol personalization
- QEEG normative comparison and channel deviations

All frequency ranges follow standard clinical EEG conventions.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# ── Enums ────────────────────────────────────────────────────────────────

class EEGBand(str, Enum):
    """Standard clinical EEG frequency bands."""
    DELTA = "delta"
    THETA = "theta"
    ALPHA = "alpha"
    BETA = "beta"
    HIGH_BETA = "high_beta"
    GAMMA = "gamma"


# ── Constants ────────────────────────────────────────────────────────────

EEG_BAND_RANGES: dict[EEGBand, tuple[float, float]] = {
    EEGBand.DELTA: (0.5, 4.0),
    EEGBand.THETA: (4.0, 8.0),
    EEGBand.ALPHA: (8.0, 13.0),
    EEGBand.BETA: (13.0, 30.0),
    EEGBand.HIGH_BETA: (30.0, 40.0),
    EEGBand.GAMMA: (40.0, 100.0),
}
"""Mapping of each EEG band to its (low_hz, high_hz) frequency range."""


STANDARD_10_20_CHANNELS: list[dict[str, str]] = [
    # Frontal
    {"name": "Fp1", "position_10_20": "Fp1", "hemisphere": "left"},
    {"name": "Fp2", "position_10_20": "Fp2", "hemisphere": "right"},
    {"name": "F3", "position_10_20": "F3", "hemisphere": "left"},
    {"name": "F4", "position_10_20": "F4", "hemisphere": "right"},
    {"name": "F7", "position_10_20": "F7", "hemisphere": "left"},
    {"name": "F8", "position_10_20": "F8", "hemisphere": "right"},
    {"name": "Fz", "position_10_20": "Fz", "hemisphere": "midline"},
    # Central
    {"name": "C3", "position_10_20": "C3", "hemisphere": "left"},
    {"name": "C4", "position_10_20": "C4", "hemisphere": "right"},
    {"name": "Cz", "position_10_20": "Cz", "hemisphere": "midline"},
    # Temporal
    {"name": "T3", "position_10_20": "T3", "hemisphere": "left"},
    {"name": "T4", "position_10_20": "T4", "hemisphere": "right"},
    {"name": "T5", "position_10_20": "T5", "hemisphere": "left"},
    {"name": "T6", "position_10_20": "T6", "hemisphere": "right"},
    # Parietal
    {"name": "P3", "position_10_20": "P3", "hemisphere": "left"},
    {"name": "P4", "position_10_20": "P4", "hemisphere": "right"},
    {"name": "Pz", "position_10_20": "Pz", "hemisphere": "midline"},
    # Occipital
    {"name": "O1", "position_10_20": "O1", "hemisphere": "left"},
    {"name": "O2", "position_10_20": "O2", "hemisphere": "right"},
]
"""All 19 standard 10-20 system electrode positions."""

_VALID_10_20_NAMES: frozenset[str] = frozenset(
    ch["name"] for ch in STANDARD_10_20_CHANNELS
)


# ── Channel & Band Power ────────────────────────────────────────────────

class EEGChannel(BaseModel):
    """A single EEG electrode in the international 10-20 system."""
    name: str = Field(..., description="Electrode label, e.g. 'Fp1', 'F3', 'Cz'")
    position_10_20: str = Field(..., description="Position in the 10-20 system")
    hemisphere: Literal["left", "right", "midline"]


class BandPower(BaseModel):
    """Spectral power measurement for a single frequency band."""
    band: EEGBand
    absolute_power: float = Field(..., description="Absolute power in microvolts squared (uV^2)")
    relative_power: float = Field(
        ..., ge=0.0, le=1.0,
        description="Relative power as fraction of total power (0-1)",
    )
    z_score: Optional[float] = Field(
        None,
        description="Z-score relative to normative database",
    )

    @field_validator("absolute_power")
    @classmethod
    def _abs_power_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Absolute power cannot be negative")
        return v


class ChannelData(BaseModel):
    """Complete spectral data for one EEG channel."""
    channel: EEGChannel
    band_powers: list[BandPower] = Field(
        default_factory=list,
        description="Power values for each frequency band",
    )
    peak_frequency: Optional[float] = Field(
        None, gt=0,
        description="Peak frequency in Hz for this channel",
    )


# ── Asymmetry ────────────────────────────────────────────────────────────

class AsymmetryIndex(BaseModel):
    """Inter-hemispheric asymmetry between a homologous electrode pair."""
    pair: str = Field(
        ...,
        description="Homologous pair label, e.g. 'F3-F4', 'P3-P4'",
    )
    band: EEGBand
    index_value: float = Field(
        ..., ge=-1.0, le=1.0,
        description="Asymmetry index: negative = left < right, positive = left > right",
    )
    z_score: Optional[float] = Field(
        None,
        description="Z-score relative to normative database",
    )
    clinical_significance: str = Field(
        "",
        description="Clinical interpretation, e.g. 'significant left frontal hypoactivation'",
    )


# ── Coherence & Connectivity ────────────────────────────────────────────

class CoherenceValue(BaseModel):
    """Coherence between two EEG channels in a given frequency band."""
    channel_pair: tuple[str, str] = Field(
        ...,
        description="Pair of channel names, e.g. ('F3', 'P3')",
    )
    band: EEGBand
    coherence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Magnitude-squared coherence (0-1)",
    )
    phase_lag_degrees: Optional[float] = Field(
        None,
        description="Phase lag in degrees between the two channels",
    )


class ConnectivityMatrix(BaseModel):
    """Full-head connectivity represented as coherence values per band."""
    bands: dict[EEGBand, list[CoherenceValue]] = Field(
        default_factory=dict,
        description="Coherence values grouped by frequency band",
    )


# ── Source Localization ──────────────────────────────────────────────────

class RegionActivity(BaseModel):
    """Estimated cortical activity for a single brain region."""
    region_name: str = Field(..., description="Anatomical region name, e.g. 'left DLPFC'")
    brodmann_area: Optional[int] = Field(
        None, ge=1, le=52,
        description="Brodmann area number (1-52)",
    )
    mni_coordinates: tuple[float, float, float] = Field(
        ...,
        description="MNI coordinates (x, y, z) in mm",
    )
    activation_level: float = Field(
        ...,
        description="Estimated activation level (arbitrary units, method-dependent)",
    )
    z_score: Optional[float] = Field(
        None,
        description="Z-score relative to normative database",
    )


class SourceLocalization(BaseModel):
    """Source-localized EEG activity from inverse solution methods."""
    method: Literal["sloreta", "eloreta", "beamformer"] = Field(
        ...,
        description="Inverse solution method used",
    )
    regions: list[RegionActivity] = Field(
        default_factory=list,
        description="Estimated regional activity",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the source localization was computed",
    )


# ── EEG Recording ───────────────────────────────────────────────────────

class EEGRecording(BaseModel):
    """Complete representation of a single EEG/QEEG recording session."""
    recording_id: str = Field(..., description="Unique recording identifier")
    patient_id: str = Field(..., description="Patient identifier")
    recorded_at: datetime = Field(
        ...,
        description="UTC timestamp of recording",
    )
    montage: str = Field(
        ...,
        description="Recording montage, e.g. 'linked_ears', 'average', 'laplacian'",
    )
    sampling_rate_hz: int = Field(
        ..., gt=0,
        description="Sampling rate in Hz",
    )

    # Channel data
    channels: list[ChannelData] = Field(
        default_factory=list,
        description="Per-channel spectral data",
    )

    # Derived measures
    asymmetry_indices: list[AsymmetryIndex] = Field(
        default_factory=list,
        description="Inter-hemispheric asymmetry indices",
    )
    peak_alpha_frequency: Optional[float] = Field(
        None, gt=0,
        description="Individual alpha frequency (IAF) in Hz",
    )

    # Connectivity
    connectivity: Optional[ConnectivityMatrix] = Field(
        None,
        description="Full connectivity matrix if computed",
    )

    # Source localization
    source_localization: Optional[SourceLocalization] = Field(
        None,
        description="Source localization results if computed",
    )

    # Quality
    artifacts_detected: list[str] = Field(
        default_factory=list,
        description="Types of artifacts detected, e.g. ['eye_blink', 'muscle', 'line_noise']",
    )
    quality_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="Overall data quality score (0 = unusable, 1 = excellent)",
    )

    # Processing
    processing_params: dict = Field(
        default_factory=dict,
        description="Processing pipeline parameters (filters, epoch length, etc.)",
    )
    source_file_path: Optional[str] = Field(
        None,
        description="Path to the original EEG data file",
    )


# ── Extracted Features ───────────────────────────────────────────────────

class EEGFeatures(BaseModel):
    """Summary features extracted from EEG data for protocol personalization.

    These features drive the EEG personalization node in the Sozo graph,
    informing montage selection, parameter tuning, and network targeting.
    """
    dominant_frequency: float = Field(
        ..., gt=0,
        description="Dominant frequency across all channels in Hz",
    )
    peak_alpha_frequency: float = Field(
        ..., gt=0,
        description="Individual alpha frequency (IAF) in Hz",
    )
    frontal_alpha_asymmetry: float = Field(
        ...,
        description="F4-F3 alpha asymmetry; negative = left hypoactivation",
    )
    theta_beta_ratio: float = Field(
        ..., ge=0,
        description="Theta/beta ratio (frontal); elevated in ADHD phenotypes",
    )
    network_dysfunction_map: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Mapping of NetworkKey value to severity level "
            "(e.g. {'dmn': 'severe', 'cen': 'moderate'})"
        ),
    )
    abnormal_regions: list[str] = Field(
        default_factory=list,
        description="Brain regions with statistically abnormal activity",
    )
    suggested_targets: list[str] = Field(
        default_factory=list,
        description="Recommended stimulation target regions based on EEG findings",
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Overall confidence in the extracted features (0-1)",
    )
    feature_explanation: str = Field(
        "",
        description="Natural language summary of key EEG findings for clinician review",
    )


# ── QEEG Normative Comparison ───────────────────────────────────────────

class ChannelDeviation(BaseModel):
    """Z-score deviation for a single channel/band relative to a normative database."""
    channel_name: str = Field(..., description="Electrode name, e.g. 'F3'")
    band: EEGBand
    z_score: float = Field(..., description="Z-score deviation from normative mean")
    direction: Literal["elevated", "reduced", "normal"] = Field(
        ...,
        description="Direction of deviation",
    )
    clinical_note: Optional[str] = Field(
        None,
        description="Optional clinical interpretation note",
    )

    @model_validator(mode="after")
    def _direction_matches_zscore(self) -> ChannelDeviation:
        """Warn-level consistency check: direction should match z-score sign."""
        if self.direction == "elevated" and self.z_score < -1.5:
            raise ValueError(
                f"Direction 'elevated' conflicts with z_score={self.z_score} "
                f"(expected positive z-score for elevated)"
            )
        if self.direction == "reduced" and self.z_score > 1.5:
            raise ValueError(
                f"Direction 'reduced' conflicts with z_score={self.z_score} "
                f"(expected negative z-score for reduced)"
            )
        return self


class QEEGNormativeComparison(BaseModel):
    """Comparison of a patient's QEEG data against a normative database."""
    database_name: str = Field(
        ...,
        description="Normative database used, e.g. 'NeuroGuide', 'qEEG-Pro', 'BrainDx'",
    )
    age_group: str = Field(
        ...,
        description="Age group or range used for comparison, e.g. '30-39', 'adult'",
    )
    eyes_condition: Literal["open", "closed"] = Field(
        ...,
        description="Recording condition: eyes open or eyes closed",
    )
    deviations: list[ChannelDeviation] = Field(
        default_factory=list,
        description="Per-channel band deviations from normative values",
    )

    def significant_deviations(self, threshold: float = 2.0) -> list[ChannelDeviation]:
        """Return deviations exceeding the given z-score threshold."""
        return [d for d in self.deviations if abs(d.z_score) >= threshold]

    def channels_by_direction(
        self, direction: Literal["elevated", "reduced", "normal"],
    ) -> list[ChannelDeviation]:
        """Filter deviations by direction."""
        return [d for d in self.deviations if d.direction == direction]
