"""
Protocol Montage Panel Generator.

Creates a multi-panel figure showing all stimulation protocols for a condition.
Each sub-panel is a 10-10 EEG scalp map with the protocol's electrode placements.

Visual features:
- Grid layout (e.g. 2x4 for 8 tDCS protocols)
- Each panel: head outline + electrodes + protocol code + symptom label
- Color-coded anode/cathode/TPS
- Compact, printable A4 format
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

logger = logging.getLogger(__name__)

# Import shared electrode positions
from .qeeg_topomap import EEG_10_10, NAVY, TEAL, HEAD_FILL, DOT_GRAY
from .qeeg_topomap import ANODE_RED, CATHODE_BLUE, TPS_ORANGE

SOZO_BROWN = "#996600"


def _draw_mini_head(ax):
    """Draw a small head outline for panel use."""
    head = plt.Circle((0.5, 0.5), 0.42, color=HEAD_FILL, zorder=1)
    head_ring = plt.Circle((0.5, 0.5), 0.42, color=NAVY, fill=False, linewidth=1.5, zorder=5)
    ax.add_patch(head)
    ax.add_patch(head_ring)

    # Nose
    nose = mpatches.Polygon(
        [[0.48, 0.92], [0.52, 0.92], [0.50, 0.97]],
        closed=True, color=NAVY, zorder=6
    )
    ax.add_patch(nose)

    # Ears
    for ex in [0.06, 0.94]:
        ear = mpatches.FancyBboxPatch(
            (ex - 0.02, 0.45), 0.04, 0.10,
            boxstyle="round,pad=0.008",
            facecolor="#D4DEE4", edgecolor=NAVY,
            linewidth=0.8, zorder=2
        )
        ax.add_patch(ear)


def _draw_mini_electrodes(ax, anodes, cathodes, tps_targets):
    """Draw electrode positions on a mini panel."""
    cx, cy, r = 0.5, 0.5, 0.40
    highlight = set(anodes) | set(cathodes) | set(tps_targets)
    skip = {"T3", "T4", "T9", "T10", "F9", "F10", "FT9", "FT10", "TP9", "TP10"}
    drawn = set()

    key_electrodes = {
        "Fp1", "Fpz", "Fp2", "F7", "F3", "Fz", "F4", "F8",
        "T7", "C3", "Cz", "C4", "T8",
        "P3", "Pz", "P4",
        "O1", "Oz", "O2", "Cb1", "Cbz", "Cb2",
        "FC3", "FCz", "FC4", "CP3", "CPz", "CP4",
    }

    for ename, (nx, ny) in EEG_10_10.items():
        pos_key = (round(nx, 3), round(ny, 3))
        if pos_key in drawn or ename in skip:
            continue
        drawn.add(pos_key)

        ax_x = cx + nx * r
        ax_y = cy + ny * r

        if ename in anodes:
            color, dot_r = ANODE_RED, 0.035
        elif ename in cathodes:
            color, dot_r = CATHODE_BLUE, 0.035
        elif ename in tps_targets:
            color, dot_r = TPS_ORANGE, 0.035
        elif ename in key_electrodes:
            color, dot_r = DOT_GRAY, 0.012
        else:
            continue  # Skip non-key electrodes for cleaner panels

        dot = plt.Circle((ax_x, ax_y), dot_r, color=color,
                          ec="white" if ename in highlight else color,
                          linewidth=0.6, zorder=4 if ename in highlight else 3)
        ax.add_patch(dot)

        if ename in highlight:
            ax.text(ax_x, ax_y - dot_r - 0.02, ename,
                    ha="center", va="top", fontsize=5, fontweight="bold",
                    color=NAVY, zorder=7)


def generate_protocol_panel(
    title: str,
    condition_name: str,
    protocols: list[dict],
    output_path: str | Path | None = None,
    figsize: tuple | None = None,
    dpi: int = 200,
    cols: int = 4,
) -> bytes:
    """Generate a multi-panel protocol montage figure.

    Args:
        title: Figure title
        condition_name: Condition name
        protocols: List of dicts with keys:
            - code: str (e.g. "C1", "T1")
            - symptom: str (e.g. "Motor Bradykinesia")
            - anodes: list[str] (electrode names)
            - cathodes: list[str] (electrode names)
            - tps_targets: list[str] (electrode names)
            - params: str (optional parameter text)
        output_path: Save path
        figsize: Override figure size
        dpi: Resolution
        cols: Number of columns in grid

    Returns:
        PNG bytes
    """
    n = len(protocols)
    rows = max(1, (n + cols - 1) // cols)

    if figsize is None:
        figsize = (cols * 3.2, rows * 3.5 + 1.2)

    fig, axes = plt.subplots(rows, cols, figsize=figsize, facecolor="white")
    fig.suptitle(title, fontsize=14, fontweight="bold", color=NAVY, y=0.98)
    fig.text(0.5, 0.955, condition_name, ha="center", fontsize=11,
             color=TEAL, style="italic")

    # Flatten axes array
    if rows == 1 and cols == 1:
        axes_flat = [axes]
    elif rows == 1 or cols == 1:
        axes_flat = list(axes)
    else:
        axes_flat = [ax for row in axes for ax in row]

    for idx, ax in enumerate(axes_flat):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.axis("off")

        if idx >= n:
            continue

        p = protocols[idx]
        code = p.get("code", "")
        symptom = p.get("symptom", "")
        anodes = p.get("anodes", [])
        cathodes = p.get("cathodes", [])
        tps_targets = p.get("tps_targets", [])
        params = p.get("params", "")

        _draw_mini_head(ax)
        _draw_mini_electrodes(ax, anodes, cathodes, tps_targets)

        # Code label (top-left)
        ax.text(0.05, 0.97, code, ha="left", va="top",
                fontsize=10, fontweight="bold", color=SOZO_BROWN,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFF5E6",
                          edgecolor=SOZO_BROWN, alpha=0.9))

        # Symptom label (bottom)
        # Truncate long labels
        label = symptom if len(symptom) <= 30 else symptom[:28] + "..."
        ax.text(0.5, 0.02, label, ha="center", va="bottom",
                fontsize=6.5, color=NAVY, style="italic")

    # ── Legend ─────────────────────────────────────────────────────
    legend_items = [
        mpatches.Patch(color=ANODE_RED, label="Anode (+)"),
        mpatches.Patch(color=CATHODE_BLUE, label="Cathode (-)"),
        mpatches.Patch(color=TPS_ORANGE, label="TPS Target"),
    ]
    fig.legend(
        handles=legend_items,
        loc="lower center",
        ncol=3,
        fontsize=8.5,
        frameon=True,
        framealpha=0.95,
        edgecolor="#CCCCCC",
    )

    fig.text(0.98, 0.005, "SOZO Brain Center", ha="right",
             fontsize=6.5, color="#AABBCC", style="italic")

    plt.tight_layout(rect=[0, 0.04, 1, 0.94])

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    img_bytes = buf.read()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(img_bytes)
        logger.info(f"Protocol panel saved: {output_path}")

    return img_bytes


def generate_protocol_panel_for_condition(condition, output_dir: str | Path) -> list[Path]:
    """Generate protocol panels from a ConditionSchema.

    Creates separate panels for TPS and tDCS protocols.
    """
    from ..core.data_loader import load_protocol_data

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = []

    data = load_protocol_data(condition.slug)
    if not data:
        logger.debug(f"No protocol data for {condition.slug}")
        return generated

    # ── TPS panel ──────────────────────────────────────────────────
    tps_protocols = data.get("tps", [])
    if tps_protocols:
        protocols = []
        for p in tps_protocols:
            protocols.append({
                "code": p.get("code", ""),
                "symptom": p.get("symptom", ""),
                "tps_targets": p.get("targets", []),
                "anodes": [],
                "cathodes": [],
            })
        out = output_dir / f"{condition.slug}_tps_panel.png"
        generate_protocol_panel(
            title=f"TPS Protocols — {condition.display_name}",
            condition_name="Transcranial Pulse Stimulation (NEUROLITH)",
            protocols=protocols,
            output_path=str(out),
            cols=min(len(protocols), 5),
        )
        generated.append(out)

    # ── tDCS panel ─────────────────────────────────────────────────
    tdcs_protocols = data.get("tdcs", [])
    if tdcs_protocols:
        protocols = []
        for p in tdcs_protocols:
            protocols.append({
                "code": p.get("code", ""),
                "symptom": p.get("symptom", ""),
                "anodes": p.get("anodes", []),
                "cathodes": p.get("cathodes", []),
                "tps_targets": [],
            })
        out = output_dir / f"{condition.slug}_tdcs_panel.png"
        generate_protocol_panel(
            title=f"tDCS Protocols — {condition.display_name}",
            condition_name="HDCkit & PlatoScience tDCS",
            protocols=protocols,
            output_path=str(out),
            cols=4,
        )
        generated.append(out)

    return generated
