"""Deterministic visual generation templates with standard parameters.

Provides frozen dataclass templates that define consistent styling for every
figure type produced by the Sozo visual generators. All generators should
reference the ``DEFAULT_*`` instances rather than hard-coding values.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from ..core.enums import NetworkKey


# ── SOZO standard network colours ──────────────────────────────────────

SOZO_NETWORK_COLORS: Dict[NetworkKey, str] = {
    NetworkKey.DMN: "#8E44AD",
    NetworkKey.CEN: "#2E75B6",
    NetworkKey.SN: "#E74C3C",
    NetworkKey.SMN: "#27AE60",
    NetworkKey.LIMBIC: "#F39C12",
    NetworkKey.ATTENTION: "#3498DB",
}
"""Canonical colour for each functional network in all Sozo visuals."""


# ── Template dataclasses ───────────────────────────────────────────────


@dataclass(frozen=True)
class BrainMapTemplate:
    """Standard parameters for brain target map figures.

    Attributes
    ----------
    figsize:
        Matplotlib figure size ``(width, height)`` in inches.
    dpi:
        Resolution in dots per inch.
    background_color:
        Hex colour for the figure background.
    target_color:
        Hex colour for stimulation target markers.
    region_font_size:
        Font size in points for brain-region labels.
    title_font_size:
        Font size in points for the figure title.
    """

    figsize: tuple[int, int] = (10, 8)
    dpi: int = 150
    background_color: str = "#FAFAFA"
    target_color: str = "#996600"
    region_font_size: int = 9
    title_font_size: int = 14


@dataclass(frozen=True)
class NetworkDiagramTemplate:
    """Standard parameters for network dysfunction diagrams.

    Attributes
    ----------
    figsize:
        Matplotlib figure size ``(width, height)`` in inches.
    dpi:
        Resolution in dots per inch.
    network_colors:
        Mapping of :class:`NetworkKey` to hex colour strings.
    hypo_alpha:
        Alpha (opacity) for hypo-active network nodes.
    normal_alpha:
        Alpha for normally-active network nodes.
    hyper_alpha:
        Alpha for hyper-active network nodes.
    edge_width:
        Default line width for inter-network edges.
    """

    figsize: tuple[int, int] = (12, 8)
    dpi: int = 150
    network_colors: Dict[NetworkKey, str] = field(default_factory=lambda: dict(SOZO_NETWORK_COLORS))
    hypo_alpha: float = 0.3
    normal_alpha: float = 0.6
    hyper_alpha: float = 1.0
    edge_width: float = 2.0


@dataclass(frozen=True)
class SymptomFlowTemplate:
    """Standard parameters for symptom-to-protocol flow diagrams.

    Attributes
    ----------
    figsize:
        Matplotlib figure size ``(width, height)`` in inches.
    dpi:
        Resolution in dots per inch.
    flow_direction:
        Layout direction (``"LR"`` = left-to-right, ``"TB"`` = top-to-bottom).
    symptom_color:
        Hex colour for symptom cluster nodes.
    network_color:
        Hex colour for network dysfunction nodes.
    target_color:
        Hex colour for stimulation target nodes.
    protocol_color:
        Hex colour for protocol / intervention nodes.
    """

    figsize: tuple[int, int] = (14, 10)
    dpi: int = 150
    flow_direction: str = "LR"
    symptom_color: str = "#E8D5B7"
    network_color: str = "#2E75B6"
    target_color: str = "#996600"
    protocol_color: str = "#4CAF50"


@dataclass(frozen=True)
class PatientJourneyTemplate:
    """Standard parameters for patient journey timeline figures.

    Attributes
    ----------
    figsize:
        Matplotlib figure size ``(width, height)`` in inches.
    dpi:
        Resolution in dots per inch.
    stage_count:
        Default number of journey stages to render.
    stage_color:
        Hex colour for stage markers.
    checkpoint_color:
        Hex colour for assessment checkpoint markers.
    responder_color:
        Hex colour for responder-pathway elements.
    non_responder_color:
        Hex colour for non-responder-pathway elements.
    """

    figsize: tuple[int, int] = (16, 6)
    dpi: int = 150
    stage_count: int = 8
    stage_color: str = "#2E75B6"
    checkpoint_color: str = "#FF9800"
    responder_color: str = "#4CAF50"
    non_responder_color: str = "#F44336"


# ── Default template instances ─────────────────────────────────────────

DEFAULT_BRAIN_MAP = BrainMapTemplate()
"""Default brain-map template used across all condition generators."""

DEFAULT_NETWORK_DIAGRAM = NetworkDiagramTemplate()
"""Default network-diagram template (includes SOZO standard colours)."""

DEFAULT_SYMPTOM_FLOW = SymptomFlowTemplate()
"""Default symptom-flow template with left-to-right layout."""

DEFAULT_PATIENT_JOURNEY = PatientJourneyTemplate()
"""Default patient-journey template with 8 stages."""
