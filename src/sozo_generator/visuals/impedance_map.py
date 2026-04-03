"""
Electrode Impedance Map Generator.

Produces a session QA visual showing the scalp with all 10-10 electrodes
color-coded by impedance contact quality. Used for monitoring electrode
placement and contact quality before/during stimulation sessions.

This is a TEMPLATE visual: it shows expected electrode status based on
the condition's stimulation targets, not live impedance measurements.

Visual features:
- Single head outline with all 10-10 electrode positions
- Color-coded dots: green (good), yellow (marginal), red (poor), gray (inactive)
- Impedance threshold legend
- Condition-aware default patterns (active targets green, neighbors marginal)
- SOZO clinical branding
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
import numpy as np

from .qeeg_topomap import (
    EEG_10_10,
    LABELLED_ELECTRODES,
    _draw_head,
    NAVY,
    TEAL,
    HEAD_FILL,
    DOT_GRAY,
)

logger = logging.getLogger(__name__)

# ── Impedance quality colors ─────────────────────────────────────────────────
GOOD_COLOR = "#27AE60"       # <5 kOhm
MARGINAL_COLOR = "#F1C40F"   # 5-10 kOhm
POOR_COLOR = "#E74C3C"       # >10 kOhm
INACTIVE_COLOR = "#B0BEC5"   # Not connected

STATUS_COLORS = {
    "good": GOOD_COLOR,
    "marginal": MARGINAL_COLOR,
    "poor": POOR_COLOR,
    "inactive": INACTIVE_COLOR,
}

# ── Electrode adjacency map ──────────────────────────────────────────────────
# Maps each electrode to its immediate spatial neighbors for auto-spreading
# "marginal" status around active electrodes.
_NEIGHBORS: dict[str, list[str]] = {
    "Fp1": ["AF3", "AF7", "Fpz", "F3"],
    "Fpz": ["Fp1", "Fp2", "AFz"],
    "Fp2": ["AF4", "AF8", "Fpz", "F4"],
    "AF7": ["Fp1", "F7", "F5", "AF3"],
    "AF3": ["Fp1", "AF7", "AFz", "F3", "F1"],
    "AFz": ["Fpz", "AF3", "AF4", "Fz"],
    "AF4": ["Fp2", "AF8", "AFz", "F4", "F2"],
    "AF8": ["Fp2", "F8", "F6", "AF4"],
    "F7": ["AF7", "F5", "FT7", "FC5"],
    "F5": ["AF7", "F7", "F3", "FC5", "FC3"],
    "F3": ["AF3", "F5", "F1", "FC3", "FC1"],
    "F1": ["AF3", "F3", "Fz", "FC1", "FCz"],
    "Fz": ["AFz", "F1", "F2", "FCz"],
    "F2": ["AFz", "Fz", "F4", "FCz", "FC2"],
    "F4": ["AF4", "F2", "F6", "FC2", "FC4"],
    "F6": ["AF8", "F4", "F8", "FC4", "FC6"],
    "F8": ["AF8", "F6", "FT8", "FC6"],
    "FT7": ["F7", "FC5", "T7", "C5"],
    "FC5": ["F7", "F5", "FT7", "FC3", "C5", "C3"],
    "FC3": ["F5", "F3", "FC5", "FC1", "C3", "C1"],
    "FC1": ["F3", "F1", "FC3", "FCz", "C1", "Cz"],
    "FCz": ["F1", "Fz", "F2", "FC1", "FC2", "Cz"],
    "FC2": ["Fz", "F2", "FCz", "FC4", "Cz", "C2"],
    "FC4": ["F2", "F4", "FC2", "FC6", "C2", "C4"],
    "FC6": ["F4", "F6", "FC4", "FT8", "C4", "C6"],
    "FT8": ["F8", "FC6", "T8", "C6"],
    "T7": ["FT7", "C5", "TP7", "CP5"],
    "C5": ["FT7", "T7", "FC5", "C3", "CP5", "CP3"],
    "C3": ["FC5", "FC3", "C5", "C1", "CP3", "CP1"],
    "C1": ["FC3", "FC1", "C3", "Cz", "CP1", "CPz"],
    "Cz": ["FC1", "FCz", "FC2", "C1", "C2", "CPz"],
    "C2": ["FCz", "FC2", "Cz", "C4", "CPz", "CP2"],
    "C4": ["FC2", "FC4", "C2", "C6", "CP2", "CP4"],
    "C6": ["FC4", "FC6", "C4", "T8", "CP4", "CP6"],
    "T8": ["FT8", "C6", "TP8", "CP6"],
    "TP7": ["T7", "CP5", "P7", "P5"],
    "CP5": ["T7", "C5", "TP7", "CP3", "P5", "P3"],
    "CP3": ["C5", "C3", "CP5", "CP1", "P3", "P1"],
    "CP1": ["C3", "C1", "CP3", "CPz", "P1", "Pz"],
    "CPz": ["C1", "Cz", "C2", "CP1", "CP2", "Pz"],
    "CP2": ["Cz", "C2", "CPz", "CP4", "Pz", "P2"],
    "CP4": ["C2", "C4", "CP2", "CP6", "P2", "P4"],
    "CP6": ["C4", "C6", "CP4", "TP8", "P4", "P6"],
    "TP8": ["T8", "C6", "CP6", "P8", "P6"],
    "P7": ["TP7", "P5", "PO7"],
    "P5": ["TP7", "CP5", "P7", "P3", "PO7", "PO3"],
    "P3": ["CP5", "CP3", "P5", "P1", "PO3"],
    "P1": ["CP3", "CP1", "P3", "Pz", "PO3", "POz"],
    "Pz": ["CP1", "CPz", "CP2", "P1", "P2", "POz"],
    "P2": ["CPz", "CP2", "Pz", "P4", "POz", "PO4"],
    "P4": ["CP2", "CP4", "P2", "P6", "PO4"],
    "P6": ["CP4", "CP6", "P4", "P8", "PO4", "PO8"],
    "P8": ["TP8", "CP6", "P6", "PO8"],
    "PO7": ["P7", "P5", "PO3", "O1"],
    "PO3": ["P5", "P3", "P1", "PO7", "POz", "O1"],
    "POz": ["P1", "Pz", "P2", "PO3", "PO4", "Oz"],
    "PO4": ["P2", "P4", "P6", "POz", "PO8", "O2"],
    "PO8": ["P6", "P8", "PO4", "O2"],
    "O1": ["PO7", "PO3", "Oz", "Cb1"],
    "Oz": ["PO3", "POz", "PO4", "O1", "O2", "Cbz"],
    "O2": ["POz", "PO4", "PO8", "Oz", "Cb2"],
    "Cb1": ["O1", "Cbz"],
    "Cbz": ["O1", "Oz", "O2", "Cb1", "Cb2"],
    "Cb2": ["O2", "Cbz"],
}

# ── Electrode map for condition target abbreviations ──────────────────────────
_TARGET_ELECTRODE_MAP = {
    "L-DLPFC": "F3", "R-DLPFC": "F4", "DLPFC": "F3",
    "L-M1": "C3", "R-M1": "C4", "M1": "C3",
    "SMA": "FCz", "CEREBELLUM": "Cbz", "CB": "Cbz",
    "ACC": "Fz", "MPFC": "Fz", "OFC": "Fp1",
    "PPC": "P3", "L-PPC": "P3", "R-PPC": "P4",
    "L-STG": "T7", "R-STG": "T8", "TPJ": "P3",
    "INSULA": "FC5", "A-INSULA": "FC5",
}


def _resolve_electrode_status(
    active_electrodes: list[str] | None,
    electrode_status: dict[str, str] | None,
) -> dict[str, str]:
    """Build a full electrode->status mapping.

    Priority:
    1. Explicit electrode_status overrides everything.
    2. active_electrodes get "good"; their neighbors get "marginal".
    3. Everything else is "inactive".
    """
    status: dict[str, str] = {}

    # Start with all inactive
    for ename in EEG_10_10:
        status[ename] = "inactive"

    # Apply active electrodes and neighbor spreading
    if active_electrodes:
        for ename in active_electrodes:
            if ename in EEG_10_10:
                status[ename] = "good"
                # Mark neighbors as marginal (unless already good)
                for neighbor in _NEIGHBORS.get(ename, []):
                    if neighbor in EEG_10_10 and status.get(neighbor) != "good":
                        status[neighbor] = "marginal"

    # Override with explicit status
    if electrode_status:
        for ename, st in electrode_status.items():
            if ename in EEG_10_10 and st in STATUS_COLORS:
                status[ename] = st

    return status


def generate_impedance_map(
    title: str = "Electrode Impedance Check \u2014 Session QA",
    condition_name: str = "",
    electrode_status: dict[str, str] | None = None,
    active_electrodes: list[str] | None = None,
    output_path: str | Path | None = None,
    figsize: tuple = (8, 9),
    dpi: int = 200,
) -> bytes:
    """Generate an electrode impedance map visual.

    Args:
        title: Main title for the figure.
        condition_name: Display name of the condition.
        electrode_status: Optional dict of electrode_name -> status string
                         ("good", "marginal", "poor", "inactive").
        active_electrodes: List of electrode names that should default to "good".
        output_path: Optional file path to save PNG.
        figsize: Figure size in inches.
        dpi: Resolution.

    Returns:
        PNG image bytes.
    """
    status_map = _resolve_electrode_status(active_electrodes, electrode_status)

    fig, ax = plt.subplots(figsize=figsize, facecolor="white")
    ax.set_aspect("equal")
    ax.axis("off")

    # Head drawing parameters
    cx, cy = 0.5, 0.46
    r = 0.34

    def to_ax(nx, ny):
        return cx + nx * r, cy + ny * r

    # ── Head outline ──────────────────────────────────────────────────
    _draw_head(ax, cx, cy, r)

    # ── Crosshair reference ───────────────────────────────────────────
    ax.plot([cx, cx], [cy - r, cy + r], color="#A0B4BF",
            lw=0.5, ls=":", zorder=3, alpha=0.5, transform=ax.transAxes)
    ax.plot([cx - r, cx + r], [cy, cy], color="#A0B4BF",
            lw=0.5, ls=":", zorder=3, alpha=0.5, transform=ax.transAxes)

    # ── Electrode dots ────────────────────────────────────────────────
    skip_aliases = {"T3", "T4", "T9", "T10", "T5", "T6", "F9", "F10",
                    "FT9", "FT10", "TP9", "TP10"}
    drawn_positions = set()

    for ename, (nx, ny) in EEG_10_10.items():
        pos_key = (round(nx, 3), round(ny, 3))
        if pos_key in drawn_positions:
            continue
        drawn_positions.add(pos_key)
        if ename in skip_aliases:
            continue

        ax_x, ax_y = to_ax(nx, ny)
        st = status_map.get(ename, "inactive")
        color = STATUS_COLORS.get(st, INACTIVE_COLOR)

        # Active electrodes get larger dots
        if st == "good":
            dot_r, zorder = 0.018, 8
            edge_color = "white"
            edge_width = 1.2
        elif st == "marginal":
            dot_r, zorder = 0.014, 7
            edge_color = "white"
            edge_width = 0.8
        elif st == "poor":
            dot_r, zorder = 0.016, 8
            edge_color = "white"
            edge_width = 1.0
        else:
            dot_r, zorder = 0.007, 5
            edge_color = DOT_GRAY
            edge_width = 0.4

        dot = plt.Circle(
            (ax_x, ax_y), dot_r, color=color,
            ec=edge_color, linewidth=edge_width, zorder=zorder,
            transform=ax.transAxes,
        )
        ax.add_patch(dot)

        # Labels for labelled electrodes
        if ename in LABELLED_ELECTRODES:
            is_active = st in ("good", "marginal", "poor")
            offset_y = dot_r + 0.010
            fs = 5.8 if is_active else 4.8
            fw = "bold" if st == "good" else "normal"
            fc = NAVY if is_active else "#8899AA"
            ax.text(ax_x, ax_y - offset_y, ename,
                    transform=ax.transAxes, ha="center", va="top",
                    fontsize=fs, fontweight=fw, color=fc, zorder=9)

    # ── Title block ───────────────────────────────────────────────────
    ax.text(0.5, 0.97, title, transform=ax.transAxes,
            ha="center", va="top", fontsize=13, fontweight="bold",
            color=NAVY, fontfamily="sans-serif")
    if condition_name:
        ax.text(0.5, 0.935, condition_name, transform=ax.transAxes,
                ha="center", va="top", fontsize=10, color=TEAL,
                fontfamily="sans-serif", style="italic")

    # ── Legend ────────────────────────────────────────────────────────
    legend_items = [
        mpatches.Patch(color=GOOD_COLOR, label="Good (<5 k\u03A9)"),
        mpatches.Patch(color=MARGINAL_COLOR, label="Marginal (5\u201310 k\u03A9)"),
        mpatches.Patch(color=POOR_COLOR, label="Poor (>10 k\u03A9)"),
        mpatches.Patch(color=INACTIVE_COLOR, label="Not connected"),
    ]
    leg = ax.legend(
        handles=legend_items,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.0),
        ncol=2,
        fontsize=8,
        frameon=True,
        framealpha=0.95,
        edgecolor="#CCCCCC",
        handlelength=1.5,
        handleheight=1.0,
        title="Impedance Quality",
        title_fontsize=9,
    )
    leg.get_frame().set_linewidth(0.6)

    # ── SOZO branding ─────────────────────────────────────────────────
    ax.text(0.98, 0.02, "SOZO Brain Center", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=6.5, color="#AABBCC",
            fontfamily="sans-serif", style="italic")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    plt.tight_layout(pad=0.5)

    # ── Output ────────────────────────────────────────────────────────
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    img_bytes = buf.read()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(img_bytes)
        logger.info(f"Impedance map saved: {output_path}")

    return img_bytes


def generate_impedance_for_condition(
    condition,
    output_dir: str | Path,
) -> Optional[Path]:
    """Generate an impedance map from a ConditionSchema object.

    Maps the condition's stimulation_targets to electrode positions,
    marks those as "good", their neighbors as "marginal", and the
    rest as "inactive".

    Args:
        condition: A ConditionSchema instance with slug, display_name,
                   and stimulation_targets.
        output_dir: Directory to write the output PNG.

    Returns:
        Path to the generated PNG, or None if generation fails.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract active electrodes from stimulation targets
    active_electrodes = []
    for target in condition.stimulation_targets:
        abbr = target.target_abbreviation.upper()
        electrode = _TARGET_ELECTRODE_MAP.get(abbr)
        if electrode:
            active_electrodes.append(electrode)

    # Deduplicate preserving order
    active_electrodes = list(dict.fromkeys(active_electrodes))

    out_path = output_dir / f"{condition.slug}_impedance_map.png"

    try:
        generate_impedance_map(
            title="Electrode Impedance Check \u2014 Session QA",
            condition_name=condition.display_name,
            active_electrodes=active_electrodes if active_electrodes else None,
            output_path=str(out_path),
        )
        return out_path
    except Exception as e:
        logger.error(f"Failed to generate impedance map for {condition.slug}: {e}")
        return None
