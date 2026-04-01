"""
SOZO Brain Center — brain region highlight maps.
Generates simplified schematic brain diagrams with target regions highlighted.
Uses matplotlib with SOZO brand colors.
"""
from __future__ import annotations

import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse, Circle, FancyBboxPatch
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# SOZO brand colors
PRIMARY_BROWN = "#996600"
PRIMARY_BLUE = "#2E75B6"
DARK_BLUE = "#1B3A5C"
ACCENT_RED = "#CC0000"
LIGHT_BLUE = "#BDD7EE"
LIGHT_BROWN = "#F5E6C8"

# Normalized (0–1) positions on top-down brain schematic
REGION_POSITIONS = {
    "DLPFC":  (0.35, 0.75),
    "M1":     (0.40, 0.65),
    "SMA":    (0.50, 0.68),
    "VLPFC":  (0.30, 0.65),
    "ACC":    (0.50, 0.72),
    "OFC":    (0.45, 0.55),
    "MPFC":   (0.50, 0.78),
    "PPC":    (0.60, 0.70),
    "IPL":    (0.65, 0.65),
    "STG":    (0.25, 0.58),
    "AG":     (0.62, 0.62),
    "HC":     (0.55, 0.45),
    "AMY":    (0.50, 0.42),
    "BG":     (0.50, 0.52),
    "THAL":   (0.50, 0.50),
    "CB":     (0.50, 0.28),
    "PFC":    (0.40, 0.72),
    "IFG":    (0.30, 0.60),
    "dmPFC":  (0.50, 0.76),
    "vmPFC":  (0.50, 0.62),
}


class BrainMapGenerator:
    """Generates simplified top-down brain maps with highlighted stimulation targets."""

    def generate_target_map(self, condition, output_dir: Path) -> Path | None:
        """
        Create a PNG showing a simplified top-down brain outline with target
        regions labeled and highlighted.

        Primary targets (first listed per modality) are shown in Primary Brown;
        additional targets in Primary Blue.

        Returns the output Path, or None on failure.
        """
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            out_path = output_dir / f"{condition.slug}_brain_map.png"

            fig, ax = plt.subplots(figsize=(8, 7))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect('equal')
            ax.axis('off')

            # Background
            fig.patch.set_facecolor('#FAFAFA')
            ax.set_facecolor('#FAFAFA')

            self._draw_brain_outline(ax)

            # Collect targets
            targets = getattr(condition, 'stimulation_targets', [])
            seen_abbrs: set[str] = set()
            primary_done = False

            for target in targets:
                abbr = getattr(target, 'target_abbreviation', None) or getattr(target, 'abbreviation', None)
                if not abbr:
                    continue
                abbr_upper = abbr.upper()
                if abbr_upper in seen_abbrs:
                    continue
                seen_abbrs.add(abbr_upper)

                position = REGION_POSITIONS.get(abbr_upper)
                if position is None:
                    logger.debug("No position defined for region %s — skipping", abbr_upper)
                    continue

                color = PRIMARY_BROWN if not primary_done else PRIMARY_BLUE
                primary_done = True
                self._highlight_region(ax, abbr_upper, position, color)

            # Title
            cond_name = getattr(condition, 'display_name', None) or getattr(condition, 'name', condition.slug)
            ax.set_title(
                f"{cond_name}\nStimulation Target Regions",
                fontsize=13,
                fontweight='bold',
                color=DARK_BLUE,
                pad=10,
            )

            # Legend
            legend_handles = [
                mpatches.Patch(facecolor=PRIMARY_BROWN, edgecolor='white', label='Primary Target'),
                mpatches.Patch(facecolor=PRIMARY_BLUE,  edgecolor='white', label='Secondary Target'),
            ]
            ax.legend(
                handles=legend_handles,
                loc='lower right',
                fontsize=8,
                framealpha=0.85,
                edgecolor='#CCCCCC',
            )

            plt.tight_layout()
            fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
            plt.close(fig)
            logger.info("Brain map saved to %s", out_path)
            return out_path

        except Exception as exc:
            logger.warning("BrainMapGenerator.generate_target_map failed: %s", exc, exc_info=True)
            return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _draw_brain_outline(self, ax: plt.Axes) -> None:
        """Draw an ellipse-based brain silhouette."""
        # Outer skull / scalp
        skull = Ellipse(
            xy=(0.5, 0.55),
            width=0.70,
            height=0.78,
            linewidth=2.5,
            edgecolor='#888888',
            facecolor='#F0EAE0',
            zorder=1,
        )
        ax.add_patch(skull)

        # Cerebellum bump at the bottom
        cb = Ellipse(
            xy=(0.5, 0.21),
            width=0.32,
            height=0.20,
            linewidth=1.5,
            edgecolor='#AAAAAA',
            facecolor='#E8E0D0',
            zorder=2,
        )
        ax.add_patch(cb)

        # Left hemisphere dividing line (very faint)
        ax.plot(
            [0.50, 0.50],
            [0.18, 0.92],
            color='#CCCCCC',
            linewidth=1.0,
            linestyle='--',
            zorder=3,
        )

        # Frontal / parietal groove approximation
        ax.plot(
            [0.27, 0.73],
            [0.63, 0.63],
            color='#CCCCCC',
            linewidth=0.8,
            linestyle=':',
            zorder=3,
        )

        # Compass labels
        for txt, x, y, ha in [
            ('Frontal', 0.50, 0.94, 'center'),
            ('Occipital', 0.50, 0.13, 'center'),
            ('L', 0.10, 0.55, 'center'),
            ('R', 0.90, 0.55, 'center'),
        ]:
            ax.text(x, y, txt, ha=ha, va='center', fontsize=7,
                    color='#888888', style='italic', zorder=4)

    def _highlight_region(
        self,
        ax: plt.Axes,
        region_abbr: str,
        position: tuple[float, float],
        color: str,
    ) -> None:
        """Draw a colored circle at position with region label."""
        x, y = position
        radius = 0.048

        circle = Circle(
            (x, y),
            radius=radius,
            facecolor=color,
            edgecolor='white',
            linewidth=1.5,
            alpha=0.88,
            zorder=5,
        )
        ax.add_patch(circle)

        ax.text(
            x, y,
            region_abbr,
            ha='center', va='center',
            fontsize=6.5,
            fontweight='bold',
            color='white',
            zorder=6,
        )
