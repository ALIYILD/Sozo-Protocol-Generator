"""
Axial (Top-Down) Brain View — Stimulation Target Visualization.

Generates a stylized axial (horizontal) brain cross-section as seen from
above, with color-coded neuromodulation target overlays. These are NOT
real MRI images — they are high-quality anatomical illustrations designed
to show clinicians where stimulation targets are located in the
horizontal plane.

Visual features:
- Top-down brain shape with frontal/occipital poles
- Left/right hemispheres with interhemispheric fissure
- Lateral sulcus (Sylvian fissure) and central sulcus
- Color-coded bilateral stimulation targets with glow effects
- TPS beam path visualization
- Anatomical orientation labels (Anterior, Posterior, Left, Right)
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

# ── Anatomical region positions (axial view, normalised 0-1) ─────────────
# x = left-right (0 = left, 1 = right), y = anterior-posterior (1 = anterior/front, 0 = posterior/back)
BRAIN_REGIONS = {
    # Cortical — left hemisphere
    "L-DLPFC": {"pos": (0.28, 0.76), "label": "L-DLPFC\n(BA 9/46)", "depth": "cortical"},
    "L-M1":    {"pos": (0.30, 0.58), "label": "L-M1\n(BA 4)", "depth": "cortical"},
    "L-PPC":   {"pos": (0.28, 0.38), "label": "L-PPC\n(BA 7/40)", "depth": "cortical"},
    "L-STG":   {"pos": (0.22, 0.50), "label": "L-STG\n(BA 22)", "depth": "cortical"},
    "L-Insula": {"pos": (0.34, 0.54), "label": "L-Insula\n(BA 13)", "depth": "subcortical"},
    # Cortical — right hemisphere
    "R-DLPFC": {"pos": (0.72, 0.76), "label": "R-DLPFC\n(BA 9/46)", "depth": "cortical"},
    "R-M1":    {"pos": (0.70, 0.58), "label": "R-M1\n(BA 4)", "depth": "cortical"},
    "R-PPC":   {"pos": (0.72, 0.38), "label": "R-PPC\n(BA 7/40)", "depth": "cortical"},
    "R-STG":   {"pos": (0.78, 0.50), "label": "R-STG\n(BA 22)", "depth": "cortical"},
    "R-Insula": {"pos": (0.66, 0.54), "label": "R-Insula\n(BA 13)", "depth": "subcortical"},
    # Midline cortical
    "SMA":     {"pos": (0.50, 0.62), "label": "SMA\n(BA 6)", "depth": "cortical"},
    "OFC":     {"pos": (0.50, 0.84), "label": "OFC\n(BA 11/47)", "depth": "cortical"},
    # Deep — bilateral
    "L-Thalamus":    {"pos": (0.42, 0.50), "label": "L-Thalamus", "depth": "deep"},
    "R-Thalamus":    {"pos": (0.58, 0.50), "label": "R-Thalamus", "depth": "deep"},
    "L-BG":          {"pos": (0.38, 0.58), "label": "L-Basal\nGanglia", "depth": "deep"},
    "R-BG":          {"pos": (0.62, 0.58), "label": "R-Basal\nGanglia", "depth": "deep"},
    "L-Hippocampus": {"pos": (0.36, 0.40), "label": "L-Hippocampus", "depth": "deep"},
    "R-Hippocampus": {"pos": (0.64, 0.40), "label": "R-Hippocampus", "depth": "deep"},
}


def _draw_axial_brain(ax):
    """Draw a stylized axial (top-down) brain cross-section."""
    # ── Brain outline — slightly oval, wider laterally ────────────────
    brain = Ellipse(
        (0.50, 0.52), 0.72, 0.80, angle=0,
        facecolor=BRAIN_BG, edgecolor=CORTEX_GRAY,
        linewidth=2.5, zorder=1, transform=ax.transAxes,
    )
    ax.add_patch(brain)

    # ── Frontal pole (slight protrusion at top) ──────────────────────
    theta_front = np.linspace(-0.4, 0.4, 40)
    fx = 0.50 + 0.12 * np.sin(theta_front * np.pi)
    fy = 0.92 + 0.02 * np.cos(theta_front * np.pi)
    ax.plot(fx, fy, color=CORTEX_GRAY, lw=1.8, alpha=0.5, zorder=2,
            transform=ax.transAxes)

    # ── Occipital pole (slight notch at bottom) ──────────────────────
    theta_occ = np.linspace(-0.3, 0.3, 30)
    ox = 0.50 + 0.08 * np.sin(theta_occ * np.pi)
    oy = 0.13 + 0.015 * np.cos(theta_occ * np.pi * 2)
    ax.plot(ox, oy, color=CORTEX_GRAY, lw=1.5, alpha=0.5, zorder=2,
            transform=ax.transAxes)

    # ── Interhemispheric fissure (midline) ───────────────────────────
    ax.plot([0.50, 0.50], [0.12, 0.92], color=CORTEX_GRAY, lw=2.0,
            ls="-", alpha=0.7, zorder=3, transform=ax.transAxes)

    # ── Central sulcus (separating frontal from parietal) ────────────
    # Left side
    cs_lx = [0.50, 0.44, 0.36, 0.28, 0.22]
    cs_ly = [0.60, 0.62, 0.60, 0.56, 0.52]
    ax.plot(cs_lx, cs_ly, color=CORTEX_GRAY, lw=1.8, alpha=0.6, zorder=2,
            transform=ax.transAxes)
    # Right side
    cs_rx = [0.50, 0.56, 0.64, 0.72, 0.78]
    cs_ry = [0.60, 0.62, 0.60, 0.56, 0.52]
    ax.plot(cs_rx, cs_ry, color=CORTEX_GRAY, lw=1.8, alpha=0.6, zorder=2,
            transform=ax.transAxes)

    # ── Lateral sulcus (Sylvian fissure) — left ──────────────────────
    sf_lx = [0.42, 0.34, 0.26, 0.20]
    sf_ly = [0.56, 0.52, 0.50, 0.44]
    ax.plot(sf_lx, sf_ly, color=CORTEX_GRAY, lw=1.5, alpha=0.55, zorder=2,
            transform=ax.transAxes)
    # ── Lateral sulcus — right ───────────────────────────────────────
    sf_rx = [0.58, 0.66, 0.74, 0.80]
    sf_ry = [0.56, 0.52, 0.50, 0.44]
    ax.plot(sf_rx, sf_ry, color=CORTEX_GRAY, lw=1.5, alpha=0.55, zorder=2,
            transform=ax.transAxes)

    # ── Additional cortical sulci (gyral folds) ──────────────────────
    sulci = [
        # Frontal — left
        [(0.34, 0.78), (0.30, 0.72), (0.28, 0.66)],
        # Frontal — right
        [(0.66, 0.78), (0.70, 0.72), (0.72, 0.66)],
        # Parietal — left
        [(0.32, 0.44), (0.28, 0.38), (0.26, 0.30)],
        # Parietal — right
        [(0.68, 0.44), (0.72, 0.38), (0.74, 0.30)],
        # Occipital — left
        [(0.40, 0.26), (0.36, 0.20), (0.38, 0.16)],
        # Occipital — right
        [(0.60, 0.26), (0.64, 0.20), (0.62, 0.16)],
    ]
    for sulcus in sulci:
        xs, ys = zip(*sulcus)
        ax.plot(xs, ys, color=CORTEX_GRAY, lw=1.2, ls="-", alpha=0.5,
                zorder=2, transform=ax.transAxes)

    # ── Lateral ventricles (butterfly-shaped) ────────────────────────
    vent_l = Ellipse((0.44, 0.50), 0.08, 0.14, angle=15,
                      facecolor=VENTRICLE, edgecolor=VENTRICLE,
                      alpha=0.45, linewidth=0, zorder=2, transform=ax.transAxes)
    vent_r = Ellipse((0.56, 0.50), 0.08, 0.14, angle=-15,
                      facecolor=VENTRICLE, edgecolor=VENTRICLE,
                      alpha=0.45, linewidth=0, zorder=2, transform=ax.transAxes)
    ax.add_patch(vent_l)
    ax.add_patch(vent_r)


def generate_axial_brain_view(
    title: str,
    condition_name: str,
    targets: list[dict],
    output_path: str | Path | None = None,
    figsize: tuple = (9, 8),
    dpi: int = 200,
) -> bytes:
    """Generate an axial (top-down) brain view with stimulation targets.

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
    _draw_axial_brain(ax)

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

        # Target glow (larger, semi-transparent)
        glow_r = 0.035 * intensity + 0.015
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
                fontsize=6.5, fontweight="bold", color=NAVY, zorder=7,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                          edgecolor="#CCCCCC", alpha=0.85))

    # ── TPS beam paths (if applicable) ─────────────────────────────
    tps_targets = [t for t in targets if t.get("modality") == "tps"]
    for t in tps_targets:
        region_info = BRAIN_REGIONS.get(t.get("region", ""))
        if not region_info:
            continue
        px, py = region_info["pos"]
        # Draw beam from scalp (above) toward target
        scalp_x = px
        scalp_y = min(py + 0.30, 0.95)
        ax.annotate(
            "", xy=(px, py + 0.04), xytext=(scalp_x, scalp_y),
            transform=ax.transAxes,
            arrowprops=dict(
                arrowstyle="->,head_width=0.008,head_length=0.006",
                color=TPS_COLOR, lw=1.5, alpha=0.4,
                connectionstyle="arc3,rad=0.05",
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
    ax.text(0.50, 0.06, "Posterior", transform=ax.transAxes,
            ha="center", va="center", fontsize=9, color="#889999",
            style="italic")
    ax.text(0.50, 0.915, "Anterior", transform=ax.transAxes,
            ha="center", va="center", fontsize=9, color="#889999",
            style="italic")
    ax.text(0.06, 0.50, "Left", transform=ax.transAxes,
            ha="center", va="center", fontsize=9, color="#889999",
            rotation=90, style="italic")
    ax.text(0.94, 0.50, "Right", transform=ax.transAxes,
            ha="center", va="center", fontsize=9, color="#889999",
            rotation=90, style="italic")

    # ── SOZO branding ─────────────────────────────────────────────
    ax.text(0.98, 0.02, "SOZO Brain Center", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=7, color="#AABBCC",
            fontfamily="sans-serif", style="italic")
    ax.text(0.02, 0.02, "Illustrative — not diagnostic imaging",
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
        logger.info(f"Axial brain view saved: {output_path}")

    return img_bytes


def generate_axial_for_condition(condition, output_dir: str | Path) -> Optional[Path]:
    """Generate axial brain view from a ConditionSchema.

    Maps the condition's stimulation_targets to axial BRAIN_REGIONS and
    renders the top-down cross-section with color-coded targets.

    Args:
        condition: A ConditionSchema instance with stimulation_targets.
        output_dir: Directory where the PNG will be saved.

    Returns:
        Path to the saved PNG, or None if no targets could be mapped.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Map stimulation target abbreviations to axial brain regions
    abbr_to_region = {
        # DLPFC — bilateral
        "L-DLPFC": "L-DLPFC", "R-DLPFC": "R-DLPFC", "DLPFC": "L-DLPFC",
        # M1 — bilateral
        "L-M1": "L-M1", "R-M1": "R-M1", "M1": "L-M1",
        # SMA — midline
        "SMA": "SMA",
        # PPC — bilateral
        "L-PPC": "L-PPC", "R-PPC": "R-PPC", "PPC": "L-PPC",
        "IPL": "L-PPC", "ANGULAR": "L-PPC", "AG": "L-PPC",
        # STG — bilateral
        "L-STG": "L-STG", "R-STG": "R-STG", "STG": "L-STG",
        # Insula — bilateral
        "INSULA": "L-Insula", "A-INSULA": "L-Insula",
        "L-INSULA": "L-Insula", "R-INSULA": "R-Insula",
        # OFC — midline anterior
        "OFC": "OFC", "VMPFC": "OFC",
        # Deep — thalamus
        "THALAMUS": "L-Thalamus", "THAL": "L-Thalamus",
        "L-THALAMUS": "L-Thalamus", "R-THALAMUS": "R-Thalamus",
        # Deep — basal ganglia
        "BG": "L-BG", "BASAL GANGLIA": "L-BG",
        "L-BG": "L-BG", "R-BG": "R-BG",
        # Deep — hippocampus
        "HIPPOCAMPUS": "L-Hippocampus", "HC": "L-Hippocampus",
        "L-HIPPOCAMPUS": "L-Hippocampus", "R-HIPPOCAMPUS": "R-Hippocampus",
        # Extras mapped to nearest axial equivalent
        "ACC": "SMA", "MPFC": "OFC", "MPFC": "OFC",
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

    out_path = output_dir / f"{condition.slug}_axial_targets.png"
    generate_axial_brain_view(
        title="Axial View — Stimulation Targets",
        condition_name=condition.display_name,
        targets=targets,
        output_path=str(out_path),
    )
    return out_path
