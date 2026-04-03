"""
QEEG 10-10 Topographic Brain Map Generator.

Produces high-quality topographic head maps showing electrode positions on the
international 10-10 EEG system, with interpolated heatmap overlays for
stimulation intensity, activation zones, or protocol targeting.

Visual features:
- 64+ electrode positions (full 10-10 system)
- Smooth interpolated color field (Gaussian RBF)
- Anatomical head outline with nose and ears
- Anode/cathode/TPS target highlighting
- Stimulation intensity gradient overlay
- Clean clinical styling matching SOZO branding
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
import matplotlib.colors as mcolors
import numpy as np
from scipy.interpolate import Rbf

logger = logging.getLogger(__name__)

# ── SOZO color palette ──────────────────────────────────────────────────────
NAVY = "#0D2137"
TEAL = "#1A7A8A"
HEAD_FILL = "#F0F5F7"
DOT_GRAY = "#B0BEC5"
ANODE_RED = "#C0392B"
CATHODE_BLUE = "#2E6DA4"
TPS_ORANGE = "#E07B39"
SOZO_BROWN = "#996600"
SOZO_BLUE = "#2E75B6"

# ── Full 10-10 EEG system coordinates ──────────────────────────────────────
# (x, y) normalised: 0,0 = vertex (Cz), radius 1.0 = head circumference
EEG_10_10 = {
    # Frontal pole
    "Fp1": (-0.31, 0.91), "Fpz": (0.0, 0.95), "Fp2": (0.31, 0.91),
    # Anterior-frontal
    "AF7": (-0.64, 0.75), "AF3": (-0.33, 0.81), "AFz": (0.0, 0.84),
    "AF4": (0.33, 0.81), "AF8": (0.64, 0.75),
    # Frontal
    "F9": (-0.95, 0.37), "F7": (-0.80, 0.53), "F5": (-0.62, 0.64),
    "F3": (-0.42, 0.75), "F1": (-0.20, 0.82), "Fz": (0.0, 0.86),
    "F2": (0.20, 0.82), "F4": (0.42, 0.75), "F6": (0.62, 0.64),
    "F8": (0.80, 0.53), "F10": (0.95, 0.37),
    # Fronto-temporal / Fronto-central
    "FT9": (-0.98, 0.17), "FT7": (-0.91, 0.27), "FC5": (-0.73, 0.42),
    "FC3": (-0.51, 0.58), "FC1": (-0.25, 0.72), "FCz": (0.0, 0.77),
    "FC2": (0.25, 0.72), "FC4": (0.51, 0.58), "FC6": (0.73, 0.42),
    "FT8": (0.91, 0.27), "FT10": (0.98, 0.17),
    # Central / Temporal
    "T9": (-1.02, 0.0), "T7": (-1.0, 0.0), "C5": (-0.78, 0.0),
    "C3": (-0.56, 0.0), "C1": (-0.27, 0.0), "Cz": (0.0, 0.0),
    "C2": (0.27, 0.0), "C4": (0.56, 0.0), "C6": (0.78, 0.0),
    "T8": (1.0, 0.0), "T10": (1.02, 0.0),
    # Legacy temporal names (aliases)
    "T3": (-1.0, 0.0), "T4": (1.0, 0.0),
    # Temporo-parietal / Centro-parietal
    "TP9": (-0.98, -0.17), "TP7": (-0.91, -0.27), "CP5": (-0.73, -0.42),
    "CP3": (-0.51, -0.58), "CP1": (-0.25, -0.72), "CPz": (0.0, -0.77),
    "CP2": (0.25, -0.72), "CP4": (0.51, -0.58), "CP6": (0.73, -0.42),
    "TP8": (0.91, -0.27), "TP10": (0.98, -0.17),
    # Parietal / Temporal (posterior)
    "T5": (-0.80, -0.53), "P7": (-0.80, -0.53), "P5": (-0.62, -0.64),
    "P3": (-0.42, -0.75), "P1": (-0.20, -0.82), "Pz": (0.0, -0.86),
    "P2": (0.20, -0.82), "P4": (0.42, -0.75), "P6": (0.62, -0.64),
    "P8": (0.80, -0.53), "T6": (0.80, -0.53),
    # Parieto-occipital
    "PO7": (-0.56, -0.78), "PO3": (-0.31, -0.87), "POz": (0.0, -0.91),
    "PO4": (0.31, -0.87), "PO8": (0.56, -0.78),
    # Occipital
    "O1": (-0.31, -0.94), "Oz": (0.0, -0.96), "O2": (0.31, -0.94),
    # Cerebellar (sub-occipital)
    "Cb1": (-0.20, -1.04), "Cbz": (0.0, -1.07), "Cb2": (0.20, -1.04),
}

# Canonical label set (shown with text)
LABELLED_ELECTRODES = {
    "Fp1", "Fpz", "Fp2", "AF3", "AFz", "AF4", "AF7", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "FT8",
    "T7", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "T8",
    "TP7", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "TP8",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO3", "POz", "PO4", "PO8",
    "O1", "Oz", "O2", "Cb1", "Cbz", "Cb2",
}


def _draw_head(ax, cx: float, cy: float, r: float):
    """Draw anatomical head outline with nose and ears."""
    # Head circle
    head = plt.Circle((cx, cy), r, color=HEAD_FILL, zorder=1,
                       transform=ax.transAxes)
    head_ring = plt.Circle((cx, cy), r, color=NAVY, fill=False,
                            linewidth=2.5, zorder=10, transform=ax.transAxes)
    ax.add_patch(head)
    ax.add_patch(head_ring)

    # Nose
    nose_w, nose_h = 0.028, 0.042
    nose = mpatches.Polygon(
        [[cx - nose_w, cy + r - 0.003],
         [cx + nose_w, cy + r - 0.003],
         [cx, cy + r + nose_h]],
        closed=True, color=NAVY, zorder=11, transform=ax.transAxes
    )
    ax.add_patch(nose)

    # Ears
    for side in [-1, 1]:
        ex = cx + side * (r + 0.012)
        ear = mpatches.FancyBboxPatch(
            (ex - 0.011, cy - 0.04), 0.022, 0.08,
            boxstyle="round,pad=0.006",
            facecolor="#D4DEE4", edgecolor=NAVY,
            linewidth=1.3, zorder=2, transform=ax.transAxes
        )
        ax.add_patch(ear)


def generate_qeeg_topomap(
    title: str,
    condition_name: str,
    anodes: list[str] | None = None,
    cathodes: list[str] | None = None,
    tps_targets: list[str] | None = None,
    intensity_map: dict[str, float] | None = None,
    highlight_electrodes: dict[str, str] | None = None,
    output_path: str | Path | None = None,
    figsize: tuple = (8, 9),
    dpi: int = 200,
    show_heatmap: bool = True,
    colormap: str = "RdYlBu_r",
    subtitle: str = "",
) -> bytes:
    """Generate a high-quality 10-10 QEEG topographic brain map.

    Args:
        title: Main title (e.g. "tDCS Protocol C1 — Motor Cortex Targeting")
        condition_name: Condition display name
        anodes: Electrode names for anode positions (red)
        cathodes: Electrode names for cathode positions (blue)
        tps_targets: Electrode names for TPS targets (orange)
        intensity_map: Dict of electrode_name -> intensity value (0-1) for heatmap
        highlight_electrodes: Dict of electrode_name -> hex_color for custom highlighting
        output_path: Optional file path to save PNG
        figsize: Figure size in inches
        dpi: Resolution
        show_heatmap: If True and intensity_map provided, render interpolated heatmap
        colormap: Matplotlib colormap name for heatmap
        subtitle: Optional subtitle line

    Returns:
        PNG image bytes
    """
    anodes = anodes or []
    cathodes = cathodes or []
    tps_targets = tps_targets or []
    highlight_electrodes = highlight_electrodes or {}

    # Auto-generate intensity map from electrode roles if not provided
    if intensity_map is None and show_heatmap:
        intensity_map = {}
        for e in anodes:
            intensity_map[e] = 1.0
        for e in cathodes:
            intensity_map[e] = -1.0
        for e in tps_targets:
            intensity_map[e] = 0.8

    fig, ax = plt.subplots(figsize=figsize, facecolor="white")
    ax.set_aspect("equal")
    ax.axis("off")

    # Drawing parameters
    cx, cy = 0.5, 0.46
    r = 0.34

    def to_ax(nx, ny):
        return cx + nx * r, cy + ny * r

    # ── Heatmap interpolation ──────────────────────────────────────────
    if show_heatmap and intensity_map:
        # Build interpolation grid
        xi = np.linspace(cx - r * 1.1, cx + r * 1.1, 200)
        yi = np.linspace(cy - r * 1.15, cy + r * 1.1, 200)
        XI, YI = np.meshgrid(xi, yi)

        # Collect known intensity points
        xp, yp, zp = [], [], []
        for ename, val in intensity_map.items():
            if ename in EEG_10_10:
                nx, ny = EEG_10_10[ename]
                ax_x, ax_y = to_ax(nx, ny)
                xp.append(ax_x)
                yp.append(ax_y)
                zp.append(val)

        if len(xp) >= 3:
            try:
                rbf = Rbf(xp, yp, zp, function="gaussian", epsilon=0.06)
                ZI = rbf(XI, YI)

                # Mask outside head
                dist = np.sqrt((XI - cx) ** 2 + (YI - cy) ** 2)
                ZI[dist > r * 1.02] = np.nan

                # Normalize
                vmax = max(abs(np.nanmin(ZI)), abs(np.nanmax(ZI)), 0.01)
                cmap = plt.get_cmap(colormap)
                cmap.set_bad(alpha=0)

                ax.contourf(
                    XI, YI, ZI, levels=50,
                    cmap=cmap, alpha=0.55, vmin=-vmax, vmax=vmax,
                    zorder=2, transform=ax.transAxes,
                    extend="both",
                )
            except Exception as e:
                logger.debug(f"Heatmap interpolation failed: {e}")

    # ── Head outline (on top of heatmap) ───────────────────────────────
    _draw_head(ax, cx, cy, r)

    # ── Crosshair reference lines ──────────────────────────────────────
    ax.plot([cx, cx], [cy - r, cy + r], color="#A0B4BF",
            lw=0.5, ls=":", zorder=3, alpha=0.5, transform=ax.transAxes)
    ax.plot([cx - r, cx + r], [cy, cy], color="#A0B4BF",
            lw=0.5, ls=":", zorder=3, alpha=0.5, transform=ax.transAxes)

    # ── Electrode dots ─────────────────────────────────────────────────
    active_set = set(anodes) | set(cathodes) | set(tps_targets) | set(highlight_electrodes.keys())
    skip_labels = {"T3", "T4", "T9", "T10", "T5", "T6", "F9", "F10", "FT9", "FT10",
                   "TP9", "TP10"}

    drawn_positions = set()
    for ename, (nx, ny) in EEG_10_10.items():
        pos_key = (round(nx, 3), round(ny, 3))
        if pos_key in drawn_positions:
            continue
        drawn_positions.add(pos_key)

        ax_x, ax_y = to_ax(nx, ny)

        if ename in anodes:
            color, edge, dot_r, z = ANODE_RED, "white", 0.019, 8
        elif ename in cathodes:
            color, edge, dot_r, z = CATHODE_BLUE, "white", 0.019, 8
        elif ename in tps_targets:
            color, edge, dot_r, z = TPS_ORANGE, "white", 0.019, 8
        elif ename in highlight_electrodes:
            color, edge, dot_r, z = highlight_electrodes[ename], "white", 0.017, 7
        else:
            color, edge, dot_r, z = DOT_GRAY, DOT_GRAY, 0.007, 5

        dot = plt.Circle((ax_x, ax_y), dot_r, color=color,
                          ec=edge, linewidth=0.8, zorder=z,
                          transform=ax.transAxes)
        ax.add_patch(dot)

        # Labels
        if ename in LABELLED_ELECTRODES and ename not in skip_labels:
            is_active = ename in active_set
            offset_y = dot_r + 0.010
            fs = 5.8 if is_active else 4.8
            fw = "bold" if is_active else "normal"
            fc = NAVY if is_active else "#8899AA"
            ax.text(ax_x, ax_y - offset_y, ename,
                    transform=ax.transAxes, ha="center", va="top",
                    fontsize=fs, fontweight=fw, color=fc, zorder=9)

    # ── Title block ────────────────────────────────────────────────────
    ax.text(0.5, 0.97, title, transform=ax.transAxes,
            ha="center", va="top", fontsize=13, fontweight="bold",
            color=NAVY, fontfamily="sans-serif")
    if subtitle:
        ax.text(0.5, 0.935, subtitle, transform=ax.transAxes,
                ha="center", va="top", fontsize=10, color=TEAL,
                fontfamily="sans-serif")
    ax.text(0.5, 0.905, condition_name, transform=ax.transAxes,
            ha="center", va="top", fontsize=9, color="#667788",
            fontfamily="sans-serif", style="italic")

    # ── Legend ─────────────────────────────────────────────────────────
    legend_items = []
    if anodes:
        legend_items.append(mpatches.Patch(color=ANODE_RED, label="Anode (+)"))
    if cathodes:
        legend_items.append(mpatches.Patch(color=CATHODE_BLUE, label="Cathode (-)"))
    if tps_targets:
        legend_items.append(mpatches.Patch(color=TPS_ORANGE, label="TPS Target"))
    for ename, color in highlight_electrodes.items():
        if ename not in anodes and ename not in cathodes and ename not in tps_targets:
            legend_items.append(mpatches.Patch(color=color, label=f"{ename} target"))
            break  # Only one custom entry in legend

    if legend_items:
        leg = ax.legend(
            handles=legend_items,
            loc="lower center",
            bbox_to_anchor=(0.5, 0.0),
            ncol=min(len(legend_items), 4),
            fontsize=8,
            frameon=True,
            framealpha=0.95,
            edgecolor="#CCCCCC",
            handlelength=1.5,
            handleheight=1.0,
        )
        leg.get_frame().set_linewidth(0.6)

    # ── SOZO branding ──────────────────────────────────────────────────
    ax.text(0.98, 0.02, "SOZO Brain Center", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=6.5, color="#AABBCC",
            fontfamily="sans-serif", style="italic")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    plt.tight_layout(pad=0.5)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    img_bytes = buf.read()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(img_bytes)
        logger.info(f"QEEG topomap saved: {output_path}")

    return img_bytes


def generate_qeeg_for_condition(condition, output_dir: str | Path) -> Optional[Path]:
    """Generate QEEG topomap from a ConditionSchema object.

    Picks the primary stimulation target and generates a topomap showing
    all stimulation targets with their electrode positions.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    anodes, cathodes, tps_list = [], [], []
    for target in condition.stimulation_targets:
        mod = target.modality.value if hasattr(target.modality, "value") else str(target.modality)
        abbr = target.target_abbreviation.upper()

        # Map target abbreviations to electrode positions
        electrode_map = {
            "L-DLPFC": "F3", "R-DLPFC": "F4", "DLPFC": "F3",
            "L-M1": "C3", "R-M1": "C4", "M1": "C3",
            "SMA": "FCz", "CEREBELLUM": "Cbz", "CB": "Cbz",
            "ACC": "Fz", "MPFC": "Fz", "OFC": "Fp1",
            "PPC": "P3", "L-PPC": "P3", "R-PPC": "P4",
            "L-STG": "T5", "R-STG": "T6", "TPJ": "P3",
            "INSULA": "FC5", "A-INSULA": "FC5",
        }

        electrode = electrode_map.get(abbr, None)
        if electrode is None:
            continue

        if mod == "tps":
            tps_list.append(electrode)
        elif mod == "tdcs":
            anodes.append(electrode)

    # Deduplicate
    anodes = list(dict.fromkeys(anodes))
    cathodes = list(dict.fromkeys(cathodes))
    tps_list = list(dict.fromkeys(tps_list))

    if not anodes and not cathodes and not tps_list:
        logger.debug(f"No electrode targets mapped for {condition.slug}")
        return None

    out_path = output_dir / f"{condition.slug}_qeeg_topomap.png"
    generate_qeeg_topomap(
        title=f"Stimulation Target Map — 10-10 EEG System",
        condition_name=condition.display_name,
        anodes=anodes,
        cathodes=cathodes,
        tps_targets=tps_list,
        output_path=str(out_path),
        subtitle=f"Primary targets: {', '.join(anodes + tps_list)}" if (anodes or tps_list) else "",
    )
    return out_path
