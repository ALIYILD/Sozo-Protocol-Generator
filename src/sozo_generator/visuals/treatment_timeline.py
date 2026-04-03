"""
SOZO Multimodal Session Gantt Chart — Treatment Timeline Generator.

Produces a horizontal Gantt-style timeline showing the temporal sequence
of a single SOZO multimodal treatment session, following the S-O-Z-O
paradigm:

    S — Stabilize:   taVNS / CES (10-15 min)
    O — Optimize:    tDCS (15-20 min)
    Z — Zone Target: TPS ROI + holocranial (20-30 min)
    O — Outcome:     taVNS/CES + rehab tasks (30-45 min)

Visual features:
- Horizontal Gantt bars for each treatment phase
- Phase-specific color coding
- Device and description annotations
- Time axis (0-90 min)
- SOZO branding footer
"""
from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

logger = logging.getLogger(__name__)

# SOZO brand colors
NAVY = "#0D2137"
TEAL = "#1A7A8A"
SOZO_BROWN = "#996600"
SOZO_BLUE = "#2E75B6"
SOZO_DARK_BLUE = "#1B3A5C"

# Phase colors
COLOR_S = "#27AE60"   # Stabilize — green
COLOR_O1 = "#2E75B6"  # Optimize — blue
COLOR_Z = "#E07B39"   # Zone Target — orange
COLOR_O2 = "#8E44AD"  # Outcome — purple

# Default SOZO session phases
DEFAULT_PHASES = [
    {
        "label": "S \u2014 Stabilize",
        "device": "taVNS / CES",
        "start_min": 0,
        "duration_min": 15,
        "color": COLOR_S,
        "description": "Downshift sympathetic tone,\nreduce cortical noise",
    },
    {
        "label": "O \u2014 Optimize",
        "device": "tDCS",
        "start_min": 15,
        "duration_min": 20,
        "color": COLOR_O1,
        "description": "Prime target networks\nfor stimulation",
    },
    {
        "label": "Z \u2014 Zone Target",
        "device": "TPS ROI + holocranial",
        "start_min": 35,
        "duration_min": 25,
        "color": COLOR_Z,
        "description": "Deep network modulation\nat target ROI",
    },
    {
        "label": "O \u2014 Outcome",
        "device": "taVNS/CES + rehab tasks",
        "start_min": 60,
        "duration_min": 30,
        "color": COLOR_O2,
        "description": "Post-stimulation\nneuroplasticity window",
    },
]


def generate_treatment_timeline(
    title: str = "SOZO Multimodal Session Protocol",
    condition_name: str = "",
    phases: list[dict] | None = None,
    output_path: str | None = None,
    figsize: tuple[int, int] = (14, 5),
    dpi: int = 200,
) -> bytes:
    """
    Generate a horizontal Gantt-style treatment timeline.

    Parameters
    ----------
    title : str
        Main chart title.
    condition_name : str
        Condition name for subtitle.
    phases : list[dict] | None
        List of phase dicts with keys: label, device, start_min,
        duration_min, color, description.  Defaults to the standard
        SOZO S-O-Z-O sequence.
    output_path : str | None
        If given, save PNG to this path.
    figsize : tuple
        Figure size in inches.
    dpi : int
        Output resolution.

    Returns
    -------
    bytes
        PNG image as bytes.
    """
    if phases is None:
        phases = DEFAULT_PHASES

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#FAFAFA")

    n_phases = len(phases)
    bar_height = 0.6
    y_positions = list(range(n_phases - 1, -1, -1))  # top-to-bottom

    # Compute time range
    max_time = max(p["start_min"] + p["duration_min"] for p in phases)
    time_end = int(np.ceil(max_time / 10) * 10)  # round up to nearest 10

    for idx, phase in enumerate(phases):
        y = y_positions[idx]
        start = phase["start_min"]
        duration = phase["duration_min"]
        color = phase.get("color", SOZO_BLUE)

        # Draw Gantt bar
        bar = ax.barh(
            y, duration, left=start, height=bar_height,
            color=color, edgecolor="white", linewidth=1.5,
            zorder=3, alpha=0.92,
        )

        # Phase label inside bar (white text)
        mid_x = start + duration / 2
        ax.text(
            mid_x, y, phase["label"],
            ha="center", va="center",
            fontsize=10, fontweight="bold", color="white",
            zorder=4,
        )

        # Device name below bar (small text)
        ax.text(
            mid_x, y - bar_height / 2 - 0.12,
            phase.get("device", ""),
            ha="center", va="top",
            fontsize=7.5, color=color, fontweight="bold",
            zorder=4,
        )

        # Description to the right of the bar
        desc = phase.get("description", "")
        if desc:
            ax.text(
                start + duration + 1.0, y,
                desc,
                ha="left", va="center",
                fontsize=7.5, color=NAVY, style="italic",
                zorder=4,
            )

    # Time axis
    ax.set_xlim(-2, time_end + 35)
    ax.set_ylim(-0.8, n_phases - 0.3)
    ax.set_xlabel("Time (minutes)", fontsize=10, color=NAVY, fontweight="bold")
    ax.set_xticks(range(0, time_end + 1, 10))
    ax.tick_params(axis="x", labelsize=9, colors=NAVY)

    # Remove y-axis ticks (labels are inside bars)
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#CCCCCC")

    # Light vertical grid lines
    for t in range(0, time_end + 1, 10):
        ax.axvline(t, color="#E0E0E0", linewidth=0.5, zorder=1)

    # Title and subtitle
    subtitle = f"Condition: {condition_name}" if condition_name else ""
    full_title = title
    if subtitle:
        full_title += f"\n{subtitle}"
    ax.set_title(full_title, fontsize=13, fontweight="bold", color=SOZO_DARK_BLUE, pad=15)

    # SOZO branding footer
    fig.text(
        0.98, 0.02, "SOZO Brain Center",
        ha="right", fontsize=7, color="#AABBCC", style="italic",
    )

    plt.tight_layout(pad=1.2)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    img_bytes = buf.read()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(img_bytes)
        logger.info("Treatment timeline saved: %s", output_path)

    return img_bytes


def generate_timeline_for_condition(
    condition, output_dir: str | Path
) -> Optional[Path]:
    """
    Build a condition-specific SOZO session timeline from a ConditionSchema.

    Maps the condition's stimulation_targets to the appropriate SOZO phases:
    - tDCS targets go into the Optimize phase (device text)
    - TPS targets go into the Zone Target phase (device text)
    - taVNS/CES remain in Stabilize and Outcome phases

    Parameters
    ----------
    condition : ConditionSchema
        The condition schema with stimulation_targets.
    output_dir : str | Path
        Directory for the output PNG.

    Returns
    -------
    Optional[Path]
        Path to the generated PNG, or None on failure.
    """
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / f"{condition.slug}_treatment_timeline.png"

        # Start from default phases (deep copy)
        import copy
        phases = copy.deepcopy(DEFAULT_PHASES)

        # Map condition targets to phase devices
        tdcs_targets = []
        tps_targets = []
        tavns_targets = []

        for target in getattr(condition, "stimulation_targets", []):
            modality_val = target.modality.value if hasattr(target.modality, "value") else str(target.modality)
            modality_lower = modality_val.lower()

            lat = getattr(target, "laterality", "")
            abbrev = getattr(target, "target_abbreviation", target.target_region)
            electrode_hint = ""
            if "left" in lat.lower():
                electrode_hint = f"L-{abbrev}"
            elif "right" in lat.lower():
                electrode_hint = f"R-{abbrev}"
            else:
                electrode_hint = abbrev

            if "tdcs" in modality_lower:
                tdcs_targets.append(f"tDCS: {electrode_hint}")
            elif "tps" in modality_lower:
                tps_targets.append(f"TPS: {electrode_hint}")
            elif "tavns" in modality_lower or "ces" in modality_lower:
                tavns_targets.append(modality_val)

        # Update Optimize phase (index 1) with tDCS targets
        if tdcs_targets:
            phases[1]["device"] = " | ".join(tdcs_targets[:2])

        # Update Zone Target phase (index 2) with TPS targets
        if tps_targets:
            phases[2]["device"] = " + ".join(tps_targets[:2]) + " + holocranial"

        # Update Stabilize/Outcome with taVNS specifics if present
        if tavns_targets:
            phases[0]["device"] = " / ".join(set(tavns_targets))
            phases[3]["device"] = " / ".join(set(tavns_targets)) + " + rehab tasks"

        generate_treatment_timeline(
            title="SOZO Multimodal Session Protocol",
            condition_name=condition.display_name,
            phases=phases,
            output_path=str(out_path),
        )

        logger.info("Condition timeline generated: %s", out_path)
        return out_path

    except Exception as exc:
        logger.warning(
            "generate_timeline_for_condition failed: %s", exc, exc_info=True
        )
        return None
