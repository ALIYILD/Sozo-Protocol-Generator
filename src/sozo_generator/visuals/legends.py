"""
SOZO Brain Center — shared legend figures.
Evidence level legend, confidence label legend, network color legend.
"""

import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# SOZO brand colors
PRIMARY_BROWN = "#996600"
PRIMARY_BLUE  = "#2E75B6"
DARK_BLUE     = "#1B3A5C"
ACCENT_RED    = "#CC0000"
LIGHT_BLUE    = "#BDD7EE"
LIGHT_BROWN   = "#F5E6C8"

# Evidence level hierarchy (highest → lowest) with label and color
EVIDENCE_LEVELS = [
    ("HIGHEST",  "#1A7A1A"),   # rich green
    ("HIGH",     "#4CAF50"),   # medium green
    ("MEDIUM",   "#FFC107"),   # amber
    ("LOW",      "#FF7043"),   # deep orange
    ("VERY LOW", "#CC0000"),   # red
    ("MISSING",  "#AAAAAA"),   # grey
]

# Network colors (same as network_diagrams.py — kept in sync manually)
NETWORK_LEGEND_DATA = [
    ("DMN",       "#2E75B6", "Default Mode Network"),
    ("CEN",       "#996600", "Central Executive Network"),
    ("SN",        "#CC0000", "Salience Network"),
    ("SMN",       "#1B3A5C", "Sensorimotor Network"),
    ("LIMBIC",    "#7B68EE", "Limbic Network"),
    ("ATTENTION", "#20B2AA", "Attention Network"),
]

# Confidence labels
CONFIDENCE_LEGEND_DATA = [
    ("High Confidence",        "#1A7A1A"),
    ("Medium Confidence",      "#FFC107"),
    ("Low Confidence",         "#FF7043"),
    ("Insufficient / Review",  "#CC0000"),
]


class LegendGenerator:
    """Generates shared SOZO legend PNG files."""

    # ------------------------------------------------------------------
    # Evidence legend
    # ------------------------------------------------------------------

    def generate_evidence_legend(self, output_dir: Path) -> Path | None:
        """
        Horizontal bar chart showing the evidence hierarchy from
        HIGHEST (green) down to MISSING (grey).

        Returns output Path, or None on failure.
        """
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            out_path = output_dir / "evidence_legend.png"

            labels = [lvl[0] for lvl in EVIDENCE_LEVELS]
            colors = [lvl[1] for lvl in EVIDENCE_LEVELS]
            n = len(labels)

            fig, ax = plt.subplots(figsize=(7, 2.6))
            fig.patch.set_facecolor('#FAFAFA')
            ax.set_facecolor('#FAFAFA')

            bar_values = list(range(n, 0, -1))  # descending so highest is tallest
            bars = ax.barh(
                labels,
                bar_values,
                color=colors,
                edgecolor='white',
                linewidth=1.2,
                height=0.60,
            )

            # Value labels inside bars
            for bar, (label, color) in zip(bars, zip(labels, colors)):
                ax.text(
                    bar.get_width() - 0.15,
                    bar.get_y() + bar.get_height() / 2,
                    label,
                    va='center', ha='right',
                    fontsize=8.5,
                    fontweight='bold',
                    color='white',
                )

            ax.set_xlim(0, n + 0.3)
            ax.axis('off')
            ax.set_title(
                "Evidence Level Hierarchy",
                fontsize=10,
                fontweight='bold',
                color=DARK_BLUE,
                pad=8,
            )

            plt.tight_layout(pad=0.5)
            fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
            plt.close(fig)
            logger.info("Evidence legend saved to %s", out_path)
            return out_path

        except Exception as exc:
            logger.warning("LegendGenerator.generate_evidence_legend failed: %s", exc, exc_info=True)
            return None

    # ------------------------------------------------------------------
    # Network color legend
    # ------------------------------------------------------------------

    def generate_network_legend(self, output_dir: Path) -> Path | None:
        """
        Six colored squares with network names and abbreviations.

        Returns output Path, or None on failure.
        """
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            out_path = output_dir / "network_legend.png"

            n = len(NETWORK_LEGEND_DATA)
            fig, ax = plt.subplots(figsize=(6.5, 2.0))
            fig.patch.set_facecolor('#FAFAFA')
            ax.set_facecolor('#FAFAFA')
            ax.axis('off')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)

            cols = 3
            rows = int(np.ceil(n / cols))
            cell_w = 1.0 / cols
            cell_h = 0.75 / rows
            square_side = min(cell_w, cell_h) * 0.35
            y_offset = 0.18

            for i, (abbr, color, full_name) in enumerate(NETWORK_LEGEND_DATA):
                col_i = i % cols
                row_i = i // cols
                cx = cell_w * col_i + cell_w * 0.18
                cy = 1.0 - y_offset - row_i * cell_h - cell_h * 0.4

                square = mpatches.FancyBboxPatch(
                    (cx, cy - square_side / 2),
                    square_side, square_side,
                    boxstyle="round,pad=0.005",
                    facecolor=color,
                    edgecolor='white',
                    linewidth=1.0,
                    transform=ax.transData,
                    zorder=2,
                )
                ax.add_patch(square)

                ax.text(
                    cx + square_side + 0.015,
                    cy,
                    f"{abbr} — {full_name}",
                    va='center', ha='left',
                    fontsize=8,
                    color='#1A1A1A',
                    zorder=3,
                )

            ax.set_title(
                "FNON Network Color Key",
                fontsize=10,
                fontweight='bold',
                color=DARK_BLUE,
                pad=6,
            )

            plt.tight_layout(pad=0.4)
            fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
            plt.close(fig)
            logger.info("Network legend saved to %s", out_path)
            return out_path

        except Exception as exc:
            logger.warning("LegendGenerator.generate_network_legend failed: %s", exc, exc_info=True)
            return None

    # ------------------------------------------------------------------
    # Confidence legend
    # ------------------------------------------------------------------

    def generate_confidence_legend(self, output_dir: Path) -> Path | None:
        """
        Four confidence labels with colored dot indicators.

        Returns output Path, or None on failure.
        """
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            out_path = output_dir / "confidence_legend.png"

            n = len(CONFIDENCE_LEGEND_DATA)
            fig, ax = plt.subplots(figsize=(5.5, 1.8))
            fig.patch.set_facecolor('#FAFAFA')
            ax.set_facecolor('#FAFAFA')
            ax.axis('off')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)

            cell_h = 0.72 / n
            y_start = 0.88

            for i, (label, color) in enumerate(CONFIDENCE_LEGEND_DATA):
                cy = y_start - i * cell_h

                # Colored dot
                dot = plt.Circle(
                    (0.05, cy),
                    radius=0.04,
                    facecolor=color,
                    edgecolor='white',
                    linewidth=1.0,
                    zorder=2,
                    transform=ax.transData,
                )
                ax.add_patch(dot)

                ax.text(
                    0.12, cy,
                    label,
                    va='center', ha='left',
                    fontsize=8.5,
                    color='#1A1A1A',
                    zorder=3,
                )

            ax.set_title(
                "Confidence Label Key",
                fontsize=10,
                fontweight='bold',
                color=DARK_BLUE,
                pad=6,
            )

            plt.tight_layout(pad=0.4)
            fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
            plt.close(fig)
            logger.info("Confidence legend saved to %s", out_path)
            return out_path

        except Exception as exc:
            logger.warning("LegendGenerator.generate_confidence_legend failed: %s", exc, exc_info=True)
            return None
