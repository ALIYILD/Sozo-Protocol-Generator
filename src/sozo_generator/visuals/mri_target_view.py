"""
MRI-Style Stimulation Target Visualization.

Generates stylized sagittal and axial brain views with colorful
stimulation target overlays. These are NOT real MRI images — they are
high-quality anatomical illustrations designed to show clinicians
where neuromodulation targets are located.

Visual features:
- Stylized sagittal brain cross-section with anatomical regions
- Color-coded stimulation targets with depth indicators
- TPS beam path visualization
- tDCS current flow arrows
- Anatomical labels (Brodmann areas, gyri, nuclei)
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
from matplotlib.patches import FancyArrowPatch, Ellipse
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

# ── Anatomical region positions (sagittal view, normalised 0-1) ─────────
BRAIN_REGIONS = {
    # Cortical (surface)
    "DLPFC": {"pos": (0.30, 0.82), "label": "DLPFC\n(BA 9/46)", "depth": "cortical"},
    "vmPFC": {"pos": (0.22, 0.72), "label": "vmPFC\n(BA 10/11)", "depth": "cortical"},
    "OFC": {"pos": (0.18, 0.65), "label": "OFC\n(BA 11/47)", "depth": "cortical"},
    "ACC": {"pos": (0.38, 0.72), "label": "ACC\n(BA 24/32)", "depth": "subcortical"},
    "mPFC": {"pos": (0.35, 0.78), "label": "mPFC\n(BA 10)", "depth": "cortical"},
    "M1": {"pos": (0.48, 0.88), "label": "M1\n(BA 4)", "depth": "cortical"},
    "SMA": {"pos": (0.42, 0.86), "label": "SMA\n(BA 6)", "depth": "cortical"},
    "S1": {"pos": (0.55, 0.86), "label": "S1\n(BA 3/1/2)", "depth": "cortical"},
    "PPC": {"pos": (0.65, 0.80), "label": "PPC\n(BA 7/40)", "depth": "cortical"},
    "AG": {"pos": (0.72, 0.72), "label": "Angular\n(BA 39)", "depth": "cortical"},
    "STG": {"pos": (0.55, 0.55), "label": "STG\n(BA 22)", "depth": "cortical"},
    "V1": {"pos": (0.82, 0.60), "label": "V1\n(BA 17)", "depth": "cortical"},
    "PCC": {"pos": (0.62, 0.68), "label": "PCC\n(BA 23/31)", "depth": "cortical"},
    "Precuneus": {"pos": (0.68, 0.75), "label": "Precuneus\n(BA 7)", "depth": "cortical"},
    # Deep structures
    "Hippocampus": {"pos": (0.48, 0.48), "label": "Hippocampus", "depth": "deep"},
    "Amygdala": {"pos": (0.38, 0.45), "label": "Amygdala", "depth": "deep"},
    "Thalamus": {"pos": (0.50, 0.55), "label": "Thalamus", "depth": "deep"},
    "BG": {"pos": (0.42, 0.58), "label": "Basal\nGanglia", "depth": "deep"},
    "Insula": {"pos": (0.38, 0.58), "label": "Insula\n(BA 13)", "depth": "subcortical"},
    "Cerebellum": {"pos": (0.72, 0.30), "label": "Cerebellum", "depth": "deep"},
    "Brainstem": {"pos": (0.45, 0.28), "label": "Brainstem", "depth": "deep"},
}


def _draw_sagittal_brain(ax):
    """Draw a stylized sagittal brain cross-section."""
    # Brain outline (stylized ellipse)
    brain = Ellipse((0.50, 0.58), 0.78, 0.72, angle=-5,
                     facecolor=BRAIN_BG, edgecolor=CORTEX_GRAY,
                     linewidth=2.5, zorder=1, transform=ax.transAxes)
    ax.add_patch(brain)

    # Cortex folding (sulci lines)
    sulci = [
        [(0.30, 0.85), (0.35, 0.78), (0.40, 0.82)],
        [(0.45, 0.90), (0.48, 0.82), (0.52, 0.86)],
        [(0.55, 0.88), (0.60, 0.80), (0.65, 0.84)],
        [(0.70, 0.78), (0.75, 0.70), (0.78, 0.65)],
        [(0.25, 0.72), (0.30, 0.65), (0.35, 0.60)],
    ]
    for sulcus in sulci:
        xs, ys = zip(*sulcus)
        ax.plot(xs, ys, color=CORTEX_GRAY, lw=1.5, ls="-", alpha=0.6,
                zorder=2, transform=ax.transAxes)

    # Corpus callosum (C-shape)
    theta = np.linspace(0.3, 2.8, 50)
    cc_x = 0.50 + 0.15 * np.cos(theta)
    cc_y = 0.62 + 0.08 * np.sin(theta)
    ax.plot(cc_x, cc_y, color="#C4B49A", lw=3.0, solid_capstyle="round",
            zorder=3, transform=ax.transAxes)

    # Ventricle
    vent = Ellipse((0.48, 0.56), 0.08, 0.12, angle=-10,
                    facecolor=VENTRICLE, edgecolor=VENTRICLE,
                    alpha=0.5, linewidth=0, zorder=2, transform=ax.transAxes)
    ax.add_patch(vent)

    # Cerebellum (posterior-inferior)
    cb = Ellipse((0.72, 0.30), 0.22, 0.16, angle=-15,
                  facecolor="#E8DDD0", edgecolor=CORTEX_GRAY,
                  linewidth=1.5, zorder=1, transform=ax.transAxes)
    ax.add_patch(cb)
    # Cerebellar folia lines
    for i in range(4):
        y = 0.24 + i * 0.04
        ax.plot([0.64, 0.80], [y, y + 0.01], color=CORTEX_GRAY,
                lw=0.8, alpha=0.5, zorder=2, transform=ax.transAxes)

    # Brainstem
    bs_x = [0.50, 0.48, 0.45, 0.44, 0.45, 0.50]
    bs_y = [0.45, 0.38, 0.30, 0.22, 0.18, 0.15]
    ax.fill(bs_x, bs_y, color="#D4C4B0", zorder=1, transform=ax.transAxes)
    ax.plot(bs_x, bs_y, color=CORTEX_GRAY, lw=1.5, zorder=2, transform=ax.transAxes)


def generate_mri_target_view(
    title: str,
    condition_name: str,
    targets: list[dict],
    output_path: str | Path | None = None,
    figsize: tuple = (10, 8),
    dpi: int = 200,
) -> bytes:
    """Generate an MRI-style sagittal brain view with stimulation targets.

    Args:
        title: Main title
        condition_name: Condition display name
        targets: List of dicts with keys:
            - region: str (key from BRAIN_REGIONS)
            - modality: str ("tps", "tdcs_anode", "tdcs_cathode", "tavns", "ces")
            - label: str (optional custom label)
            - intensity: float 0-1 (optional, controls dot size/opacity)
        output_path: Optional file save path
        figsize: Figure size
        dpi: Resolution

    Returns:
        PNG bytes
    """
    fig, ax = plt.subplots(figsize=figsize, facecolor="white")
    ax.set_aspect("equal")
    ax.axis("off")

    # Draw brain
    _draw_sagittal_brain(ax)

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
                fontsize=7, fontweight="bold", color=NAVY, zorder=7,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                          edgecolor="#CCCCCC", alpha=0.85))

    # ── TPS beam paths (if applicable) ─────────────────────────────
    tps_targets = [t for t in targets if t.get("modality") == "tps"]
    for t in tps_targets:
        region_info = BRAIN_REGIONS.get(t.get("region", ""))
        if not region_info:
            continue
        px, py = region_info["pos"]
        # Draw beam from scalp toward target
        scalp_x = px + (0.5 - px) * 0.15
        scalp_y = min(py + 0.35, 0.95)
        ax.annotate(
            "", xy=(px, py + 0.04), xytext=(scalp_x, scalp_y),
            transform=ax.transAxes,
            arrowprops=dict(
                arrowstyle="->,head_width=0.008,head_length=0.006",
                color=TPS_COLOR, lw=1.5, alpha=0.4,
                connectionstyle="arc3,rad=0.1",
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
        leg = ax.legend(
            handles=legend_items,
            loc="lower left",
            bbox_to_anchor=(0.02, 0.02),
            fontsize=8.5,
            frameon=True,
            framealpha=0.92,
            edgecolor="#CCCCCC",
        )

    # ── Anatomical orientation label ───────────────────────────────
    ax.text(0.12, 0.50, "Anterior", transform=ax.transAxes,
            ha="center", va="center", fontsize=8, color="#889999",
            rotation=90, style="italic")
    ax.text(0.90, 0.50, "Posterior", transform=ax.transAxes,
            ha="center", va="center", fontsize=8, color="#889999",
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
        logger.info(f"MRI target view saved: {output_path}")

    return img_bytes


def generate_mri_for_condition(condition, output_dir: str | Path) -> Optional[Path]:
    """Generate MRI-style target view from a ConditionSchema."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Map stimulation targets to brain regions
    abbr_to_region = {
        "L-DLPFC": "DLPFC", "R-DLPFC": "DLPFC", "DLPFC": "DLPFC",
        "L-M1": "M1", "R-M1": "M1", "M1": "M1",
        "SMA": "SMA", "ACC": "ACC", "MPFC": "mPFC",
        "OFC": "OFC", "VMPFC": "vmPFC",
        "PPC": "PPC", "L-PPC": "PPC", "R-PPC": "PPC",
        "IPL": "AG", "ANGULAR": "AG", "AG": "AG",
        "L-STG": "STG", "R-STG": "STG", "STG": "STG",
        "HIPPOCAMPUS": "Hippocampus", "HC": "Hippocampus",
        "AMYGDALA": "Amygdala", "AMY": "Amygdala",
        "THALAMUS": "Thalamus", "THAL": "Thalamus",
        "BG": "BG", "BASAL GANGLIA": "BG",
        "INSULA": "Insula", "A-INSULA": "Insula",
        "CEREBELLUM": "Cerebellum", "CB": "Cerebellum",
        "PCC": "PCC", "PRECUNEUS": "Precuneus",
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

    out_path = output_dir / f"{condition.slug}_mri_targets.png"
    generate_mri_target_view(
        title="Neuromodulation Stimulation Targets",
        condition_name=condition.display_name,
        targets=targets,
        output_path=str(out_path),
    )
    return out_path
