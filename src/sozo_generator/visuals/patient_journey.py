"""
SOZO Brain Center — 8-stage patient journey diagram.
Shared across all conditions — shows the standard SOZO care pathway.
"""
from __future__ import annotations

import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# SOZO brand colors
PRIMARY_BROWN = "#996600"
PRIMARY_BLUE  = "#2E75B6"
DARK_BLUE     = "#1B3A5C"
LIGHT_BLUE    = "#BDD7EE"
LIGHT_BROWN   = "#F5E6C8"

JOURNEY_STAGES = [
    ("1", "Scheduling &\nIntake"),
    ("2", "Consent &\nOrientation"),
    ("3", "Psych\nIntake"),
    ("4", "Clinical\nExam"),
    ("5", "Protocol\nSelection"),
    ("6", "Treatment\nDelivery"),
    ("7", "Response\nTracking"),
    ("8", "Maintenance\n& Discharge"),
]


class PatientJourneyGenerator:
    """Generates the standard 8-stage SOZO patient journey flowchart."""

    def generate_journey_diagram(self, condition_slug: str, output_dir: Path) -> Path | None:
        """
        Draw a horizontal flowchart of 8 rounded boxes with arrows.
        Odd-numbered stages = Primary Brown; even-numbered = Primary Blue.
        Both use white text.

        Returns output Path, or None on failure.
        """
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            out_path = output_dir / f"{condition_slug}_patient_journey.png"

            n_stages = len(JOURNEY_STAGES)
            fig_w = 2.2 * n_stages + 0.8   # wider per stage
            fig_h = 3.2

            fig, ax = plt.subplots(figsize=(fig_w, fig_h))
            ax.set_xlim(0, fig_w)
            ax.set_ylim(0, fig_h)
            ax.axis('off')
            fig.patch.set_facecolor('#FAFAFA')
            ax.set_facecolor('#FAFAFA')

            box_w = 1.80
            box_h = 1.45
            y_center = fig_h / 2 - 0.1
            spacing = (fig_w - 0.6 - n_stages * box_w) / (n_stages - 1) if n_stages > 1 else 0
            x_start = 0.3 + box_w / 2

            box_centers: list[tuple[float, float]] = []

            for idx, (num, label) in enumerate(JOURNEY_STAGES):
                cx = x_start + idx * (box_w + spacing)
                cy = y_center

                color = PRIMARY_BROWN if int(num) % 2 == 1 else PRIMARY_BLUE

                box = FancyBboxPatch(
                    (cx - box_w / 2, cy - box_h / 2),
                    box_w, box_h,
                    boxstyle="round,pad=0.08",
                    facecolor=color,
                    edgecolor='white',
                    linewidth=1.8,
                    zorder=2,
                )
                ax.add_patch(box)

                # Stage number at top of box
                ax.text(
                    cx, cy + box_h / 2 - 0.22,
                    num,
                    ha='center', va='center',
                    fontsize=10,
                    fontweight='bold',
                    color='white',
                    alpha=0.75,
                    zorder=3,
                )

                # Stage label
                ax.text(
                    cx, cy - 0.05,
                    label,
                    ha='center', va='center',
                    fontsize=7.8,
                    fontweight='bold',
                    color='white',
                    zorder=3,
                    multialignment='center',
                )

                box_centers.append((cx, cy))

            # Arrows between boxes
            for i in range(len(box_centers) - 1):
                x0 = box_centers[i][0] + box_w / 2
                x1 = box_centers[i + 1][0] - box_w / 2
                mid_y = y_center
                ax.annotate(
                    '',
                    xy=(x1, mid_y),
                    xytext=(x0, mid_y),
                    arrowprops=dict(
                        arrowstyle='-|>',
                        color='#888888',
                        lw=1.4,
                        mutation_scale=13,
                    ),
                    zorder=1,
                )

            # Title
            ax.text(
                fig_w / 2, fig_h - 0.32,
                "SOZO Brain Center — Patient Care Pathway",
                ha='center', va='center',
                fontsize=11,
                fontweight='bold',
                color=DARK_BLUE,
            )

            plt.tight_layout(pad=0.4)
            fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
            plt.close(fig)
            logger.info("Patient journey diagram saved to %s", out_path)
            return out_path

        except Exception as exc:
            logger.warning("PatientJourneyGenerator.generate_journey_diagram failed: %s", exc, exc_info=True)
            return None
