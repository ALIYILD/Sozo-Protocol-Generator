"""
EEG Power Spectral Topomap Generator.

Produces a multi-panel topographic map showing frequency band power
distribution across the scalp. Each panel represents one canonical EEG
band (Delta, Theta, Alpha, Beta, Gamma) with interpolated heatmap
overlay on a head outline.

This is a TEMPLATE visual: it shows the expected/typical spectral
profile for a condition to help clinicians understand which frequency
bands are relevant. It does NOT display patient-specific QEEG data.

Visual features:
- 1x5 grid of topomap subplots, one per frequency band
- Band-specific colormaps for visual distinction
- Condition-specific "typical dysfunction" patterns
- Smooth interpolated heatmap (Gaussian RBF) with scipy fallback
- Anatomical head outline reused from qeeg_topomap
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

# Graceful scipy fallback
try:
    from scipy.interpolate import Rbf
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

logger = logging.getLogger(__name__)

# ── Frequency band definitions ────────────────────────────────────────────────
BANDS = [
    ("Delta", "1-4 Hz", "Blues"),
    ("Theta", "4-8 Hz", "Greens"),
    ("Alpha", "8-13 Hz", "YlOrRd"),
    ("Beta", "13-30 Hz", "Purples"),
    ("Gamma", "30-100 Hz", "Reds"),
]

# ── Condition-specific spectral profiles ──────────────────────────────────────
# Mapping: condition_slug -> band_name -> electrode -> intensity (0.0-1.0)
# These represent typical dysfunction patterns found in the literature.
SPECTRAL_PROFILES: dict[str, dict[str, dict[str, float]]] = {
    "parkinsons": {
        "Delta": {
            "Fz": 0.4, "FCz": 0.35, "Cz": 0.3, "F3": 0.3, "F4": 0.3,
        },
        "Theta": {
            "Fz": 0.75, "FCz": 0.65, "Cz": 0.5, "F3": 0.5, "F4": 0.5,
            "C3": 0.4, "C4": 0.4,
        },
        "Alpha": {
            "F3": 0.25, "F4": 0.25, "Fz": 0.3,
            "P3": 0.55, "P4": 0.55, "Pz": 0.5,
            "O1": 0.6, "O2": 0.6, "Oz": 0.55,
        },
        "Beta": {
            "C3": 0.85, "C4": 0.85, "Cz": 0.7,
            "FC3": 0.65, "FC4": 0.65, "FCz": 0.55,
            "CP3": 0.6, "CP4": 0.6,
        },
        "Gamma": {
            "C3": 0.45, "C4": 0.45, "Cz": 0.35,
            "F3": 0.3, "F4": 0.3,
        },
    },
    "depression": {
        "Delta": {
            "Fz": 0.35, "F3": 0.3, "F4": 0.3,
            "Fp1": 0.25, "Fp2": 0.25,
        },
        "Theta": {
            "Fz": 0.8, "FCz": 0.7, "F3": 0.55, "F4": 0.5,
            "Cz": 0.45, "AFz": 0.6,
        },
        "Alpha": {
            # Alpha asymmetry: reduced left F3, normal right F4
            "F3": 0.25, "F4": 0.65,
            "F1": 0.3, "F2": 0.6,
            "Fz": 0.4,
            "P3": 0.5, "P4": 0.5, "Pz": 0.45,
            "O1": 0.55, "O2": 0.55,
        },
        "Beta": {
            "F3": 0.5, "F4": 0.45, "Fz": 0.45,
            "C3": 0.35, "C4": 0.35,
        },
        "Gamma": {
            "F3": 0.3, "F4": 0.25, "Fz": 0.25,
        },
    },
    "anxiety": {
        "Delta": {"Fz": 0.3, "Cz": 0.25},
        "Theta": {
            "Fz": 0.6, "FCz": 0.55, "F3": 0.5, "F4": 0.5,
        },
        "Alpha": {
            "F3": 0.3, "F4": 0.3, "Fz": 0.25,
            "P3": 0.45, "P4": 0.45, "Pz": 0.4,
        },
        "Beta": {
            "F3": 0.75, "F4": 0.75, "Fz": 0.7,
            "FC3": 0.6, "FC4": 0.6, "C3": 0.55, "C4": 0.55,
        },
        "Gamma": {
            "F3": 0.45, "F4": 0.45, "Fz": 0.4,
        },
    },
    "adhd": {
        "Delta": {"Fz": 0.5, "FCz": 0.45, "Cz": 0.4, "F3": 0.4, "F4": 0.4},
        "Theta": {
            "Fz": 0.85, "FCz": 0.75, "Cz": 0.65,
            "F3": 0.7, "F4": 0.7, "F1": 0.6, "F2": 0.6,
        },
        "Alpha": {
            "P3": 0.5, "P4": 0.5, "Pz": 0.45,
            "O1": 0.55, "O2": 0.55,
            "F3": 0.3, "F4": 0.3,
        },
        "Beta": {
            "F3": 0.2, "F4": 0.2, "Fz": 0.2,
            "C3": 0.25, "C4": 0.25,
        },
        "Gamma": {
            "F3": 0.2, "F4": 0.2,
        },
    },
}

# Generic fallback profile for unknown conditions
_GENERIC_PROFILE: dict[str, dict[str, float]] = {
    "Delta": {"Fz": 0.35, "Cz": 0.3, "Pz": 0.3},
    "Theta": {"Fz": 0.5, "FCz": 0.45, "Cz": 0.4},
    "Alpha": {
        "P3": 0.55, "P4": 0.55, "Pz": 0.5,
        "O1": 0.6, "O2": 0.6, "Oz": 0.55,
    },
    "Beta": {"C3": 0.5, "C4": 0.5, "Cz": 0.4, "F3": 0.4, "F4": 0.4},
    "Gamma": {"F3": 0.3, "F4": 0.3, "Fz": 0.25},
}


def _slug_from_condition_name(name: str) -> str:
    """Normalise a condition name to a lookup slug."""
    return name.lower().replace(" ", "_").replace("-", "_").replace("'", "")


def generate_spectral_topomap(
    title: str,
    condition_name: str,
    spectral_data: Optional[dict[str, dict[str, float]]] = None,
    output_path: str | Path | None = None,
    figsize: tuple = (16, 7),
    dpi: int = 200,
) -> bytes:
    """Generate a multi-panel EEG power spectral topomap.

    Args:
        title: Main title for the figure.
        condition_name: Display name of the condition.
        spectral_data: Optional dict of band_name -> {electrode -> intensity (0-1)}.
                       If None, looks up from SPECTRAL_PROFILES by condition slug.
        output_path: Optional file path to save PNG.
        figsize: Figure size in inches.
        dpi: Resolution.

    Returns:
        PNG image bytes.
    """
    # Resolve spectral data
    if spectral_data is None:
        slug = _slug_from_condition_name(condition_name)
        spectral_data = SPECTRAL_PROFILES.get(slug, _GENERIC_PROFILE)

    fig, axes = plt.subplots(1, 5, figsize=figsize, facecolor="white")

    # Head drawing parameters (in axes fraction coordinates)
    cx, cy = 0.5, 0.48
    r = 0.34

    def to_ax(nx, ny):
        return cx + nx * r, cy + ny * r

    for idx, (band_name, freq_range, cmap_name) in enumerate(BANDS):
        ax = axes[idx]
        ax.set_aspect("equal")
        ax.axis("off")

        band_data = spectral_data.get(band_name, {})
        cmap = plt.get_cmap(cmap_name)

        # ── Heatmap interpolation ─────────────────────────────────────
        if HAS_SCIPY and band_data:
            xi = np.linspace(cx - r * 1.1, cx + r * 1.1, 150)
            yi = np.linspace(cy - r * 1.15, cy + r * 1.1, 150)
            XI, YI = np.meshgrid(xi, yi)

            xp, yp, zp = [], [], []
            for ename, val in band_data.items():
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

                    # Mask outside head circle
                    dist = np.sqrt((XI - cx) ** 2 + (YI - cy) ** 2)
                    ZI[dist > r * 1.02] = np.nan

                    cmap_copy = cmap.copy()
                    cmap_copy.set_bad(alpha=0)

                    ax.contourf(
                        XI, YI, ZI, levels=40,
                        cmap=cmap_copy, alpha=0.6, vmin=0.0, vmax=1.0,
                        zorder=2, transform=ax.transAxes,
                        extend="both",
                    )
                except Exception as e:
                    logger.debug(f"Spectral heatmap interpolation failed for {band_name}: {e}")

        # ── Head outline ──────────────────────────────────────────────
        _draw_head(ax, cx, cy, r)

        # ── Electrode dots ────────────────────────────────────────────
        drawn_positions = set()
        skip_aliases = {"T3", "T4", "T9", "T10", "T5", "T6", "F9", "F10",
                        "FT9", "FT10", "TP9", "TP10"}
        for ename, (nx, ny) in EEG_10_10.items():
            pos_key = (round(nx, 3), round(ny, 3))
            if pos_key in drawn_positions:
                continue
            drawn_positions.add(pos_key)
            if ename in skip_aliases:
                continue

            ax_x, ax_y = to_ax(nx, ny)
            intensity = band_data.get(ename, 0.0)

            if intensity > 0 and not HAS_SCIPY:
                # Fallback: show colored dots when scipy not available
                dot_color = cmap(intensity)
                dot_r = 0.012
            else:
                dot_color = DOT_GRAY
                dot_r = 0.005

            dot = plt.Circle(
                (ax_x, ax_y), dot_r, color=dot_color,
                ec=DOT_GRAY, linewidth=0.3, zorder=6,
                transform=ax.transAxes,
            )
            ax.add_patch(dot)

        # ── Band label ────────────────────────────────────────────────
        ax.text(0.5, 0.08, f"{band_name}", transform=ax.transAxes,
                ha="center", va="center", fontsize=11, fontweight="bold",
                color=NAVY, fontfamily="sans-serif")
        ax.text(0.5, 0.03, f"({freq_range})", transform=ax.transAxes,
                ha="center", va="center", fontsize=8, color="#667788",
                fontfamily="sans-serif")

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    # ── Main title ────────────────────────────────────────────────────────
    fig.suptitle(title, fontsize=14, fontweight="bold", color=NAVY,
                 fontfamily="sans-serif", y=0.97)
    fig.text(0.5, 0.935, condition_name, ha="center", fontsize=10,
             color=TEAL, fontfamily="sans-serif", style="italic")

    # ── Disclaimer ────────────────────────────────────────────────────────
    fig.text(0.5, 0.01, "Template \u2014 not patient-specific QEEG data",
             ha="center", fontsize=7, color="#AABBCC",
             fontfamily="sans-serif", style="italic")

    # ── SOZO branding ─────────────────────────────────────────────────────
    fig.text(0.98, 0.01, "SOZO Brain Center", ha="right", fontsize=6.5,
             color="#AABBCC", fontfamily="sans-serif", style="italic")

    plt.tight_layout(rect=[0, 0.03, 1, 0.92])

    # ── Output ────────────────────────────────────────────────────────────
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    img_bytes = buf.read()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(img_bytes)
        logger.info(f"Spectral topomap saved: {output_path}")

    return img_bytes


def generate_spectral_for_condition(
    condition,
    output_dir: str | Path,
) -> Optional[Path]:
    """Generate a spectral topomap from a ConditionSchema object.

    Args:
        condition: A ConditionSchema instance with slug/display_name.
        output_dir: Directory to write the output PNG.

    Returns:
        Path to the generated PNG, or None if generation fails.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    slug = condition.slug
    spectral_data = SPECTRAL_PROFILES.get(slug, _GENERIC_PROFILE)

    out_path = output_dir / f"{slug}_spectral_topomap.png"

    try:
        generate_spectral_topomap(
            title="EEG Power Spectral Distribution \u2014 Band Topography",
            condition_name=condition.display_name,
            spectral_data=spectral_data,
            output_path=str(out_path),
        )
        return out_path
    except Exception as e:
        logger.error(f"Failed to generate spectral topomap for {slug}: {e}")
        return None
