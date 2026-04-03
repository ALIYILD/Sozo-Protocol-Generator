"""
Coronal (Front-Facing) Brain View — Stimulation Target Visualization.

Generates a stylized coronal (vertical) brain cross-section as seen from
the front, with color-coded neuromodulation target overlays. These are NOT
real MRI images — they are high-quality anatomical illustrations designed
to show clinicians where stimulation targets are located, including depth
relationships between cortical and subcortical structures.

Visual features:
- Front-facing brain cross-section with cortical dome
- Corpus callosum bridge and lateral ventricles
- Deep structures: thalamus, basal ganglia, hippocampus, amygdala
- Cortical surface targets and deep structure targets
- TPS beam path lines from cortex surface to deep targets
- Color-coded by stimulation modality
- SOZO-branded clinical styling
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
from matplotlib.patches import Ellipse
import numpy as np

logger = logging.getLogger(__name__)

# ── Colors ──────────────────────────────────────────────────────────────────
BRAIN_BG = "#F5EFE6"       # Warm cream brain fill
CORTEX_GRAY = "#D4C4B0"    # Cortex surface
DEEP_GRAY = "#A89880"       # Deep structures
VENTRICLE = "#B8D4E3"       # CSF/ventricle blue
NAVY = "#0D2137"
TEAL = "#1A7A8A"
SOZO_BROWN = "#996600"

# Stimulation colors
TPS_COLOR = "#E07B39"       # Orange for TPS
TDCS_ANODE = "#C0392B"      # Red for anode
TDCS_CATHODE = "#2E6DA4"    # Blue for cathode
TAVNS_COLOR = "#27AE60"     # Green for taVNS
CES_COLOR = "#8E44AD"       # Purple for CES

# ── Anatomical region positions (coronal view, normalised 0-1) ───────────
# x = left-right (0 = left, 1 = right), y = dorsal-ventral (1 = top/dorsal, 0 = bottom/ventral)
BRAIN_REGIONS = {
    # Cortical surface — left hemisphere
    "L-DLPFC":  {"pos": (0.22, 0.82), "label": "L-DLPFC\n(BA 9/46)", "depth": "cortical",
                 "surface": (0.22, 0.88)},
    "L-M1":     {"pos": (0.32, 0.86), "label": "L-M1\n(BA 4)", "depth": "cortical",
                 "surface": (0.32, 0.91)},
    "L-S1":     {"pos": (0.35, 0.84), "label": "L-S1\n(BA 3/1/2)", "depth": "cortical",
                 "surface": (0.35, 0.90)},
    "L-Insula": {"pos": (0.30, 0.58), "label": "L-Insula\n(BA 13)", "depth": "subcortical",
                 "surface": (0.18, 0.72)},
    # Cortical surface — right hemisphere
    "R-DLPFC":  {"pos": (0.78, 0.82), "label": "R-DLPFC\n(BA 9/46)", "depth": "cortical",
                 "surface": (0.78, 0.88)},
    "R-M1":     {"pos": (0.68, 0.86), "label": "R-M1\n(BA 4)", "depth": "cortical",
                 "surface": (0.68, 0.91)},
    "R-S1":     {"pos": (0.65, 0.84), "label": "R-S1\n(BA 3/1/2)", "depth": "cortical",
                 "surface": (0.65, 0.90)},
    "R-Insula": {"pos": (0.70, 0.58), "label": "R-Insula\n(BA 13)", "depth": "subcortical",
                 "surface": (0.82, 0.72)},
    # Midline cortical
    "SMA":      {"pos": (0.50, 0.90), "label": "SMA\n(BA 6)", "depth": "cortical",
                 "surface": (0.50, 0.93)},
    # Deep structures — left
    "L-Thalamus":    {"pos": (0.40, 0.52), "label": "L-Thalamus", "depth": "deep",
                      "surface": (0.32, 0.91)},
    "L-BG":          {"pos": (0.36, 0.60), "label": "L-Basal\nGanglia", "depth": "deep",
                      "surface": (0.28, 0.87)},
    "L-Hippocampus": {"pos": (0.34, 0.38), "label": "L-Hippocampus", "depth": "deep",
                      "surface": (0.22, 0.88)},
    "L-Amygdala":    {"pos": (0.32, 0.34), "label": "L-Amygdala", "depth": "deep",
                      "surface": (0.20, 0.85)},
    # Deep structures — right
    "R-Thalamus":    {"pos": (0.60, 0.52), "label": "R-Thalamus", "depth": "deep",
                      "surface": (0.68, 0.91)},
    "R-BG":          {"pos": (0.64, 0.60), "label": "R-Basal\nGanglia", "depth": "deep",
                      "surface": (0.72, 0.87)},
    "R-Hippocampus": {"pos": (0.66, 0.38), "label": "R-Hippocampus", "depth": "deep",
                      "surface": (0.78, 0.88)},
    "R-Amygdala":    {"pos": (0.68, 0.34), "label": "R-Amygdala", "depth": "deep",
                      "surface": (0.80, 0.85)},
}


def _draw_coronal_brain(ax):
    """Draw a stylized coronal (front-facing) brain cross-section."""
    # ── Cortical dome (outer brain shape) ────────────────────────────
    # Upper dome — wider cortex tapering to brainstem
    theta = np.linspace(0, np.pi, 100)
    dome_x = 0.50 + 0.38 * np.cos(theta)
    dome_y = 0.70 + 0.24 * np.sin(theta)
    # Lateral walls going down
    left_wall_x = [dome_x[-1]]
    left_wall_y = [dome_y[-1]]
    right_wall_x = [dome_x[0]]
    right_wall_y = [dome_y[0]]

    # Build full brain outline: dome + sides + bottom
    outline_x = np.concatenate([
        dome_x,
        np.linspace(dome_x[-1], 0.30, 20),   # Left wall going down
        [0.30, 0.35, 0.42, 0.50, 0.58, 0.65, 0.70],  # Bottom curve
        np.linspace(0.70, dome_x[0], 20),     # Right wall going up
    ])
    outline_y = np.concatenate([
        dome_y,
        np.linspace(dome_y[-1], 0.28, 20),   # Left wall
        [0.28, 0.22, 0.18, 0.16, 0.18, 0.22, 0.28],  # Bottom
        np.linspace(0.28, dome_y[0], 20),     # Right wall
    ])
    ax.fill(outline_x, outline_y, color=BRAIN_BG, zorder=1, transform=ax.transAxes)
    ax.plot(outline_x, outline_y, color=CORTEX_GRAY, lw=2.5, zorder=2,
            transform=ax.transAxes)

    # ── Cortical mantle — thick bands at edges ───────────────────────
    # Inner cortex boundary (slightly inset)
    inner_theta = np.linspace(0, np.pi, 80)
    inner_x = 0.50 + 0.32 * np.cos(inner_theta)
    inner_y = 0.70 + 0.19 * np.sin(inner_theta)
    ax.plot(inner_x, inner_y, color=CORTEX_GRAY, lw=1.2, alpha=0.4, zorder=2,
            transform=ax.transAxes)
    # Side cortex lines
    ax.plot([0.18, 0.24], [0.50, 0.50], color=CORTEX_GRAY, lw=1.2, alpha=0.4,
            zorder=2, transform=ax.transAxes)
    ax.plot([0.76, 0.82], [0.50, 0.50], color=CORTEX_GRAY, lw=1.2, alpha=0.4,
            zorder=2, transform=ax.transAxes)

    # ── Cortex folding (sulci on surface) ────────────────────────────
    sulci = [
        [(0.24, 0.84), (0.22, 0.78), (0.20, 0.72)],
        [(0.76, 0.84), (0.78, 0.78), (0.80, 0.72)],
        [(0.36, 0.90), (0.34, 0.86), (0.33, 0.82)],
        [(0.64, 0.90), (0.66, 0.86), (0.67, 0.82)],
        [(0.48, 0.93), (0.46, 0.89)],
        [(0.52, 0.93), (0.54, 0.89)],
    ]
    for sulcus in sulci:
        xs, ys = zip(*sulcus)
        ax.plot(xs, ys, color=CORTEX_GRAY, lw=1.3, alpha=0.5, zorder=2,
                transform=ax.transAxes)

    # ── Interhemispheric fissure (top midline) ───────────────────────
    ax.plot([0.50, 0.50], [0.94, 0.82], color=CORTEX_GRAY, lw=1.8,
            alpha=0.6, zorder=3, transform=ax.transAxes)

    # ── Corpus callosum (bridge) ─────────────────────────────────────
    cc_theta = np.linspace(0.2, np.pi - 0.2, 50)
    cc_x = 0.50 + 0.18 * np.cos(cc_theta)
    cc_y = 0.72 + 0.04 * np.sin(cc_theta)
    ax.fill_between(cc_x, cc_y - 0.015, cc_y + 0.015,
                     color="#C4B49A", alpha=0.7, zorder=3, transform=ax.transAxes)
    ax.plot(cc_x, cc_y, color="#B0A080", lw=2.0, zorder=4, transform=ax.transAxes)

    # ── Lateral ventricles (butterfly-shaped) ────────────────────────
    vent_l = Ellipse((0.40, 0.62), 0.10, 0.08, angle=10,
                      facecolor=VENTRICLE, edgecolor=VENTRICLE,
                      alpha=0.50, linewidth=0, zorder=3, transform=ax.transAxes)
    vent_r = Ellipse((0.60, 0.62), 0.10, 0.08, angle=-10,
                      facecolor=VENTRICLE, edgecolor=VENTRICLE,
                      alpha=0.50, linewidth=0, zorder=3, transform=ax.transAxes)
    ax.add_patch(vent_l)
    ax.add_patch(vent_r)
    # Third ventricle (midline slit)
    ax.plot([0.50, 0.50], [0.66, 0.56], color=VENTRICLE, lw=2.5,
            alpha=0.5, zorder=3, transform=ax.transAxes)

    # ── Deep structure outlines (subtle) ─────────────────────────────
    # Thalamus — bilateral ovals
    thal_l = Ellipse((0.40, 0.52), 0.10, 0.07, angle=0,
                      facecolor=DEEP_GRAY, edgecolor=DEEP_GRAY,
                      alpha=0.20, linewidth=1.0, zorder=2, transform=ax.transAxes)
    thal_r = Ellipse((0.60, 0.52), 0.10, 0.07, angle=0,
                      facecolor=DEEP_GRAY, edgecolor=DEEP_GRAY,
                      alpha=0.20, linewidth=1.0, zorder=2, transform=ax.transAxes)
    ax.add_patch(thal_l)
    ax.add_patch(thal_r)

    # Basal ganglia — bilateral
    bg_l = Ellipse((0.36, 0.60), 0.07, 0.10, angle=5,
                    facecolor=DEEP_GRAY, edgecolor=DEEP_GRAY,
                    alpha=0.15, linewidth=0.8, zorder=2, transform=ax.transAxes)
    bg_r = Ellipse((0.64, 0.60), 0.07, 0.10, angle=-5,
                    facecolor=DEEP_GRAY, edgecolor=DEEP_GRAY,
                    alpha=0.15, linewidth=0.8, zorder=2, transform=ax.transAxes)
    ax.add_patch(bg_l)
    ax.add_patch(bg_r)

    # Hippocampus — bilateral, lower temporal
    hc_l = Ellipse((0.34, 0.38), 0.08, 0.05, angle=20,
                    facecolor=DEEP_GRAY, edgecolor=DEEP_GRAY,
                    alpha=0.15, linewidth=0.8, zorder=2, transform=ax.transAxes)
    hc_r = Ellipse((0.66, 0.38), 0.08, 0.05, angle=-20,
                    facecolor=DEEP_GRAY, edgecolor=DEEP_GRAY,
                    alpha=0.15, linewidth=0.8, zorder=2, transform=ax.transAxes)
    ax.add_patch(hc_l)
    ax.add_patch(hc_r)

    # Amygdala — bilateral, anterior-inferior to hippocampus
    amy_l = Ellipse((0.32, 0.34), 0.05, 0.04, angle=0,
                     facecolor=DEEP_GRAY, edgecolor=DEEP_GRAY,
                     alpha=0.15, linewidth=0.8, zorder=2, transform=ax.transAxes)
    amy_r = Ellipse((0.68, 0.34), 0.05, 0.04, angle=0,
                     facecolor=DEEP_GRAY, edgecolor=DEEP_GRAY,
                     alpha=0.15, linewidth=0.8, zorder=2, transform=ax.transAxes)
    ax.add_patch(amy_l)
    ax.add_patch(amy_r)

    # ── Brainstem (inferior, midline) ────────────────────────────────
    bs_x = [0.46, 0.44, 0.46, 0.50, 0.54, 0.56, 0.54]
    bs_y = [0.22, 0.14, 0.08, 0.06, 0.08, 0.14, 0.22]
    ax.fill(bs_x, bs_y, color="#D4C4B0", zorder=1, transform=ax.transAxes)
    ax.plot(bs_x, bs_y, color=CORTEX_GRAY, lw=1.5, zorder=2, transform=ax.transAxes)


def generate_coronal_brain_view(
    title: str,
    condition_name: str,
    targets: list[dict],
    output_path: str | Path | None = None,
    figsize: tuple = (9, 8),
    dpi: int = 200,
) -> bytes:
    """Generate a coronal (front-facing) brain view with stimulation targets.

    Args:
        title: Main title displayed at the top of the figure.
        condition_name: Condition display name shown as subtitle.
        targets: List of dicts with keys:
            - region: str (key from BRAIN_REGIONS)
            - modality: str ("tps", "tdcs_anode", "tdcs_cathode", "tavns", "ces")
            - label: str (optional custom label)
            - intensity: float 0-1 (optional, controls dot size/opacity)
        output_path: Optional file save path.
        figsize: Figure size in inches.
        dpi: Resolution in dots-per-inch.

    Returns:
        PNG image as bytes.
    """
    fig, ax = plt.subplots(figsize=figsize, facecolor="white")
    ax.set_aspect("equal")
    ax.axis("off")

    # Draw brain
    _draw_coronal_brain(ax)

    # ── Modality colors ─────────────────────────────────────────────
    modality_colors = {
        "tps": TPS_COLOR,
        "tdcs_anode": TDCS_ANODE,
        "tdcs_cathode": TDCS_CATHODE,
        "tdcs": TDCS_ANODE,
        "tavns": TAVNS_COLOR,
        "ces": CES_COLOR,
    }

    # ── Draw targets ────────────────────────────────────────────────
    used_modalities = set()
    for t in targets:
        region_key = t.get("region", "")
        modality = t.get("modality", "tps")
        intensity = t.get("intensity", 0.8)
        custom_label = t.get("label", "")

        region_info = BRAIN_REGIONS.get(region_key)
        if not region_info:
            continue

        px, py = region_info["pos"]
        color = modality_colors.get(modality, TPS_COLOR)
        used_modalities.add(modality)

        # ── Depth indicator line for deep/subcortical targets ──────
        if region_info["depth"] in ("deep", "subcortical"):
            surface_pt = region_info.get("surface")
            if surface_pt:
                sx, sy = surface_pt
                # Dotted line from cortex surface to deep target
                ax.plot([sx, px], [sy, py], color=color, lw=1.2,
                        ls=":", alpha=0.45, zorder=3, transform=ax.transAxes)
                # Small surface marker
                ax.plot(sx, sy, "o", color=color, markersize=3,
                        alpha=0.5, zorder=4, transform=ax.transAxes)

        # Target glow (larger, semi-transparent)
        glow_r = 0.030 * intensity + 0.012
        glow = plt.Circle((px, py), glow_r, color=color,
                           alpha=0.25, zorder=4, transform=ax.transAxes)
        ax.add_patch(glow)

        # Inner glow
        inner_r = glow_r * 0.6
        inner = plt.Circle((px, py), inner_r, color=color,
                            alpha=0.5, zorder=5, transform=ax.transAxes)
        ax.add_patch(inner)

        # Core dot
        core_r = glow_r * 0.35
        core = plt.Circle((px, py), core_r, color=color,
                           ec="white", linewidth=1.0, zorder=6,
                           transform=ax.transAxes)
        ax.add_patch(core)

        # Crosshair on target
        ch_len = glow_r * 0.8
        ax.plot([px - ch_len, px + ch_len], [py, py],
                color=color, lw=0.8, alpha=0.6, zorder=5, transform=ax.transAxes)
        ax.plot([px, px], [py - ch_len, py + ch_len],
                color=color, lw=0.8, alpha=0.6, zorder=5, transform=ax.transAxes)

        # Region label
        label = custom_label or region_info["label"]
        label_offset = glow_r + 0.02
        ax.text(px, py - label_offset, label,
                transform=ax.transAxes, ha="center", va="top",
                fontsize=6, fontweight="bold", color=NAVY, zorder=7,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                          edgecolor="#CCCCCC", alpha=0.85))

    # ── TPS beam paths for deep targets ────────────────────────────
    tps_targets = [t for t in targets if t.get("modality") == "tps"]
    for t in tps_targets:
        region_info = BRAIN_REGIONS.get(t.get("region", ""))
        if not region_info or region_info["depth"] not in ("deep", "subcortical"):
            continue
        px, py = region_info["pos"]
        surface_pt = region_info.get("surface")
        if surface_pt:
            sx, sy = surface_pt
            # Beam path from scalp (slightly above surface) to deep target
            ax.annotate(
                "", xy=(px, py + 0.03), xytext=(sx, sy + 0.04),
                transform=ax.transAxes,
                arrowprops=dict(
                    arrowstyle="->,head_width=0.008,head_length=0.006",
                    color=TPS_COLOR, lw=1.8, alpha=0.35,
                    connectionstyle="arc3,rad=0.08",
                    linestyle="--",
                ),
                zorder=3,
            )

    # ── Title ──────────────────────────────────────────────────────
    ax.text(0.5, 0.98, title, transform=ax.transAxes,
            ha="center", va="top", fontsize=14, fontweight="bold",
            color=NAVY, fontfamily="sans-serif")
    ax.text(0.5, 0.945, condition_name, transform=ax.transAxes,
            ha="center", va="top", fontsize=11, color=TEAL,
            fontfamily="sans-serif", style="italic")

    # ── Legend ─────────────────────────────────────────────────────
    legend_map = {
        "tps": ("TPS (Transcranial Pulse Stimulation)", TPS_COLOR),
        "tdcs_anode": ("tDCS Anode (+)", TDCS_ANODE),
        "tdcs_cathode": ("tDCS Cathode (-)", TDCS_CATHODE),
        "tdcs": ("tDCS", TDCS_ANODE),
        "tavns": ("taVNS", TAVNS_COLOR),
        "ces": ("CES", CES_COLOR),
    }
    legend_items = []
    for mod in sorted(used_modalities):
        if mod in legend_map:
            name, color = legend_map[mod]
            legend_items.append(mpatches.Patch(color=color, label=name))

    if legend_items:
        ax.legend(
            handles=legend_items,
            loc="lower left",
            bbox_to_anchor=(0.02, 0.02),
            fontsize=8.5,
            frameon=True,
            framealpha=0.92,
            edgecolor="#CCCCCC",
        )

    # ── Anatomical orientation labels ─────────────────────────────
    ax.text(0.06, 0.50, "Left", transform=ax.transAxes,
            ha="center", va="center", fontsize=9, color="#889999",
            rotation=90, style="italic")
    ax.text(0.94, 0.50, "Right", transform=ax.transAxes,
            ha="center", va="center", fontsize=9, color="#889999",
            rotation=90, style="italic")
    ax.text(0.50, 0.02, "Ventral", transform=ax.transAxes,
            ha="center", va="bottom", fontsize=9, color="#889999",
            style="italic")
    ax.text(0.50, 0.96, "Dorsal", transform=ax.transAxes,
            ha="center", va="top", fontsize=9, color="#889999",
            style="italic")

    # ── SOZO branding ─────────────────────────────────────────────
    ax.text(0.98, 0.02, "SOZO Brain Center", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=7, color="#AABBCC",
            fontfamily="sans-serif", style="italic")
    ax.text(0.15, 0.02, "Illustrative — not diagnostic imaging",
            transform=ax.transAxes, ha="left", va="bottom",
            fontsize=6, color="#CC9999", fontfamily="sans-serif")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    plt.tight_layout(pad=0.3)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    img_bytes = buf.read()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(img_bytes)
        logger.info(f"Coronal brain view saved: {output_path}")

    return img_bytes


def generate_coronal_for_condition(condition, output_dir: str | Path) -> Optional[Path]:
    """Generate coronal brain view from a ConditionSchema.

    Maps the condition's stimulation_targets to coronal BRAIN_REGIONS and
    renders the front-facing cross-section with color-coded targets,
    including depth indicator lines for subcortical structures.

    Args:
        condition: A ConditionSchema instance with stimulation_targets.
        output_dir: Directory where the PNG will be saved.

    Returns:
        Path to the saved PNG, or None if no targets could be mapped.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Map stimulation target abbreviations to coronal brain regions
    abbr_to_region = {
        # DLPFC — bilateral
        "L-DLPFC": "L-DLPFC", "R-DLPFC": "R-DLPFC", "DLPFC": "L-DLPFC",
        # M1 — bilateral
        "L-M1": "L-M1", "R-M1": "R-M1", "M1": "L-M1",
        # S1 — bilateral
        "L-S1": "L-S1", "R-S1": "R-S1", "S1": "L-S1",
        # SMA — midline
        "SMA": "SMA",
        # Insula — bilateral
        "INSULA": "L-Insula", "A-INSULA": "L-Insula",
        "L-INSULA": "L-Insula", "R-INSULA": "R-Insula",
        # Deep — thalamus
        "THALAMUS": "L-Thalamus", "THAL": "L-Thalamus",
        "L-THALAMUS": "L-Thalamus", "R-THALAMUS": "R-Thalamus",
        # Deep — basal ganglia
        "BG": "L-BG", "BASAL GANGLIA": "L-BG",
        "L-BG": "L-BG", "R-BG": "R-BG",
        # Deep — hippocampus
        "HIPPOCAMPUS": "L-Hippocampus", "HC": "L-Hippocampus",
        "L-HIPPOCAMPUS": "L-Hippocampus", "R-HIPPOCAMPUS": "R-Hippocampus",
        # Deep — amygdala
        "AMYGDALA": "L-Amygdala", "AMY": "L-Amygdala",
        "L-AMYGDALA": "L-Amygdala", "R-AMYGDALA": "R-Amygdala",
        # Extras mapped to nearest coronal equivalent
        "ACC": "SMA", "MPFC": "SMA",
        "OFC": "L-DLPFC", "VMPFC": "L-DLPFC",
        "PPC": "L-S1", "L-PPC": "L-S1", "R-PPC": "R-S1",
        "IPL": "L-S1", "ANGULAR": "L-S1", "AG": "L-S1",
        "L-STG": "L-Insula", "R-STG": "R-Insula", "STG": "L-Insula",
    }

    targets = []
    seen = set()
    for st in condition.stimulation_targets:
        abbr = st.target_abbreviation.upper()
        region = abbr_to_region.get(abbr)
        if region and region not in seen:
            seen.add(region)
            mod = st.modality.value if hasattr(st.modality, "value") else str(st.modality)
            targets.append({
                "region": region,
                "modality": mod,
                "intensity": 0.9 if st.evidence_level.value in ("highest", "high") else 0.6,
            })

    if not targets:
        return None

    out_path = output_dir / f"{condition.slug}_coronal_targets.png"
    generate_coronal_brain_view(
        title="Coronal View — Stimulation Targets",
        condition_name=condition.display_name,
        targets=targets,
        output_path=str(out_path),
    )
    return out_path
