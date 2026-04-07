"""
SOZO Brain Center — clinical brain region target maps.
Generates professional schematic brain diagrams with bilateral stimulation
targets highlighted per protocol, with anatomical landmarks and SOZO branding.
"""
from __future__ import annotations

import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse, Circle, FancyBboxPatch, Arc
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
GRAY = "#888888"
LIGHT_GRAY = "#CCCCCC"
BG_COLOR = "#FAFAFA"
BRAIN_COLOR = "#F0EAE0"
CEREBELLUM_COLOR = "#E8E0D0"

# Bilateral brain region positions (top-down view, normalized 0-1)
# Left hemisphere positions (mirrored for right)
REGION_POSITIONS_BILATERAL = {
    # region_key: {"left": (x, y), "right": (x, y), "midline": (x, y)}
    "DLPFC": {"left": (0.32, 0.76), "right": (0.68, 0.76)},
    "M1":    {"left": (0.34, 0.63), "right": (0.66, 0.63)},
    "SMA":   {"midline": (0.50, 0.70)},
    "VLPFC": {"left": (0.25, 0.68), "right": (0.75, 0.68)},
    "ACC":   {"midline": (0.50, 0.74)},
    "OFC":   {"left": (0.40, 0.82), "right": (0.60, 0.82)},
    "MPFC":  {"midline": (0.50, 0.80)},
    "mPFC":  {"midline": (0.50, 0.80)},
    "PPC":   {"left": (0.35, 0.45), "right": (0.65, 0.45)},
    "IPL":   {"left": (0.30, 0.42), "right": (0.70, 0.42)},
    "STG":   {"left": (0.22, 0.55), "right": (0.78, 0.55)},
    "AG":    {"left": (0.32, 0.40), "right": (0.68, 0.40)},
    "HC":    {"left": (0.40, 0.48), "right": (0.60, 0.48)},
    "AMY":   {"left": (0.38, 0.52), "right": (0.62, 0.52)},
    "BG":    {"left": (0.42, 0.55), "right": (0.58, 0.55)},
    "THAL":  {"midline": (0.50, 0.52)},
    "CB":    {"midline": (0.50, 0.25)},
    "PFC":   {"left": (0.35, 0.78), "right": (0.65, 0.78)},
    "IFG":   {"left": (0.24, 0.65), "right": (0.76, 0.65)},
    "dmPFC": {"midline": (0.50, 0.78)},
    "vmPFC": {"midline": (0.50, 0.76)},
    "V1":    {"left": (0.42, 0.18), "right": (0.58, 0.18)},
    "SN":    {"midline": (0.50, 0.50)},
    "STN":   {"left": (0.44, 0.50), "right": (0.56, 0.50)},
    "GPi":   {"left": (0.43, 0.53), "right": (0.57, 0.53)},
    "INSULA": {"left": (0.28, 0.58), "right": (0.72, 0.58)},
    "T3":    {"left": (0.22, 0.55)},
    "CES":   {"left": (0.12, 0.55), "right": (0.88, 0.55)},
    # Target abbreviation aliases
    "L-DLPFC": {"left": (0.32, 0.76)},
    "R-DLPFC": {"right": (0.68, 0.76)},
    "M1/CB":   {"left": (0.34, 0.63), "midline": (0.50, 0.25)},
    "SMA/M1":  {"midline": (0.50, 0.70), "left": (0.34, 0.63)},
    "M1-contra": {"left": (0.34, 0.63)},
    "ACC/mPFC": {"midline": (0.50, 0.74)},
    "SN/STN":  {"midline": (0.50, 0.50)},
    "T3/Insula": {"left": (0.22, 0.55)},
}

# Protocol → color mapping by modality
MODALITY_COLORS = {
    "tdcs": PRIMARY_BROWN,
    "tps":  ACCENT_RED,
    "ces":  "#228B22",
    "tavns": "#9B59B6",
}


class BrainMapGenerator:
    """Generates professional top-down brain maps with bilateral stimulation targets."""

    def generate_target_map(self, condition, output_dir: Path) -> Path | None:
        """Create a clinical-grade brain map showing all protocol targets."""
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            out_path = output_dir / f"{condition.slug}_brain_map.png"

            fig, ax = plt.subplots(figsize=(10, 9), dpi=180)
            ax.set_xlim(-0.02, 1.02)
            ax.set_ylim(-0.02, 1.02)
            ax.set_aspect('equal')
            ax.axis('off')
            fig.patch.set_facecolor(BG_COLOR)
            ax.set_facecolor(BG_COLOR)

            self._draw_brain_outline(ax)
            self._draw_sulci(ax)

            # Collect all targets from protocols (not stimulation_targets)
            protocols = getattr(condition, 'protocols', [])
            placed_targets = {}  # abbr -> list of (protocol_id, color)

            for proto in protocols:
                abbr = getattr(proto, 'target_abbreviation', None)
                modality = getattr(proto, 'modality', None)
                if not abbr:
                    continue
                color = MODALITY_COLORS.get(modality.value if modality else "tdcs", PRIMARY_BROWN)
                if abbr not in placed_targets:
                    placed_targets[abbr] = []
                placed_targets[abbr].append((proto.protocol_id, color, proto.label))

            # Draw targets
            for abbr, protos in placed_targets.items():
                positions = REGION_POSITIONS_BILATERAL.get(abbr, REGION_POSITIONS_BILATERAL.get(abbr.upper(), {}))
                if not positions:
                    # Try partial match
                    for key in REGION_POSITIONS_BILATERAL:
                        if key.upper() in abbr.upper() or abbr.upper() in key.upper():
                            positions = REGION_POSITIONS_BILATERAL[key]
                            break
                if not positions:
                    continue

                # Use first protocol's color as primary
                primary_color = protos[0][1]
                proto_labels = ", ".join(p[0] for p in protos[:3])

                for side, pos in positions.items():
                    self._draw_target(ax, pos, abbr, proto_labels, primary_color,
                                     is_primary=(primary_color == PRIMARY_BROWN))

            # Title
            cond_name = getattr(condition, 'display_name', condition.slug)
            ax.text(0.50, 0.99, f"{cond_name}", ha='center', va='top',
                    fontsize=16, fontweight='bold', color=DARK_BLUE,
                    transform=ax.transAxes)
            ax.text(0.50, 0.96, "Neuromodulation Stimulation Target Map",
                    ha='center', va='top', fontsize=11, color=GRAY,
                    style='italic', transform=ax.transAxes)

            # Legend
            legend_handles = []
            for mod_name, color in [("tDCS", PRIMARY_BROWN), ("TPS", ACCENT_RED),
                                     ("CES", "#228B22"), ("taVNS", "#9B59B6")]:
                # Only show modalities used
                if any(mod_name.lower() == p.modality.value for p in protocols):
                    legend_handles.append(
                        mpatches.Patch(facecolor=color, edgecolor='white',
                                       alpha=0.85, label=f"{mod_name} Target"))
            if legend_handles:
                ax.legend(handles=legend_handles, loc='lower right', fontsize=9,
                         framealpha=0.9, edgecolor=LIGHT_GRAY, fancybox=True)

            # SOZO branding
            ax.text(0.02, 0.02, "SOZO Brain Center — Not for diagnostic imaging",
                    fontsize=7, color=LIGHT_GRAY, style='italic',
                    transform=ax.transAxes)
            ax.text(0.98, 0.02, f"Protocols: {len(protocols)}",
                    fontsize=7, color=LIGHT_GRAY, ha='right',
                    transform=ax.transAxes)

            plt.tight_layout(pad=0.5)
            fig.savefig(out_path, dpi=180, bbox_inches='tight',
                       facecolor=fig.get_facecolor())
            plt.close(fig)
            logger.info("Brain map saved to %s", out_path)
            return out_path

        except Exception as exc:
            logger.warning("BrainMapGenerator.generate_target_map failed: %s", exc, exc_info=True)
            return None

    def _draw_brain_outline(self, ax: plt.Axes) -> None:
        """Draw anatomically-informed brain silhouette with hemispheres."""
        # Outer skull
        skull = Ellipse(xy=(0.50, 0.53), width=0.72, height=0.82,
                       linewidth=2.5, edgecolor='#777777',
                       facecolor=BRAIN_COLOR, zorder=1)
        ax.add_patch(skull)

        # Left hemisphere
        left_hemi = Ellipse(xy=(0.38, 0.55), width=0.32, height=0.65,
                           linewidth=0, facecolor='#EDE5D5', alpha=0.4, zorder=2)
        ax.add_patch(left_hemi)

        # Right hemisphere
        right_hemi = Ellipse(xy=(0.62, 0.55), width=0.32, height=0.65,
                            linewidth=0, facecolor='#EDE5D5', alpha=0.4, zorder=2)
        ax.add_patch(right_hemi)

        # Cerebellum
        cb = Ellipse(xy=(0.50, 0.20), width=0.34, height=0.18,
                    linewidth=1.5, edgecolor='#AAAAAA',
                    facecolor=CEREBELLUM_COLOR, zorder=2)
        ax.add_patch(cb)
        ax.text(0.50, 0.20, "Cerebellum", ha='center', va='center',
                fontsize=7, color='#999999', style='italic', zorder=3)

        # Nose indicator
        nose_x = [0.47, 0.50, 0.53]
        nose_y = [0.93, 0.97, 0.93]
        ax.fill(nose_x, nose_y, color='#D4C4A8', edgecolor='#999999',
                linewidth=1.5, zorder=3)

        # Interhemispheric fissure
        ax.plot([0.50, 0.50], [0.16, 0.92], color='#BBBBBB',
                linewidth=1.2, linestyle='-', zorder=3, alpha=0.7)

    def _draw_sulci(self, ax: plt.Axes) -> None:
        """Draw major anatomical sulci/fissures for orientation."""
        # Central sulcus (Rolandic fissure) — separates frontal/parietal
        cs_left_x = [0.30, 0.38, 0.46]
        cs_left_y = [0.55, 0.60, 0.62]
        cs_right_x = [0.54, 0.62, 0.70]
        cs_right_y = [0.62, 0.60, 0.55]
        ax.plot(cs_left_x, cs_left_y, color='#C0B8A8', linewidth=1.0,
                zorder=3, alpha=0.6)
        ax.plot(cs_right_x, cs_right_y, color='#C0B8A8', linewidth=1.0,
                zorder=3, alpha=0.6)

        # Lateral (Sylvian) fissure
        sf_left_x = [0.22, 0.30, 0.38]
        sf_left_y = [0.55, 0.57, 0.54]
        sf_right_x = [0.62, 0.70, 0.78]
        sf_right_y = [0.54, 0.57, 0.55]
        ax.plot(sf_left_x, sf_left_y, color='#C0B8A8', linewidth=0.8,
                zorder=3, alpha=0.5)
        ax.plot(sf_right_x, sf_right_y, color='#C0B8A8', linewidth=0.8,
                zorder=3, alpha=0.5)

        # Lobe labels (subtle)
        for txt, x, y in [
            ('Frontal', 0.50, 0.86),
            ('Parietal', 0.50, 0.45),
            ('Occipital', 0.50, 0.30),
            ('Temporal', 0.20, 0.48),
            ('Temporal', 0.80, 0.48),
        ]:
            ax.text(x, y, txt, ha='center', va='center', fontsize=7,
                    color='#BBBBBB', style='italic', zorder=3, alpha=0.7)

        # Hemisphere labels
        ax.text(0.08, 0.55, 'Left', ha='center', va='center', fontsize=9,
                color=GRAY, fontweight='bold', rotation=90, zorder=4)
        ax.text(0.92, 0.55, 'Right', ha='center', va='center', fontsize=9,
                color=GRAY, fontweight='bold', rotation=-90, zorder=4)
        ax.text(0.50, 0.96, 'Anterior', ha='center', va='center', fontsize=8,
                color=GRAY, zorder=4)
        ax.text(0.50, 0.10, 'Posterior', ha='center', va='center', fontsize=8,
                color=GRAY, zorder=4)

    def _draw_target(self, ax, pos, abbr, proto_labels, color, is_primary=False):
        """Draw a target region with glow effect, label, and protocol ID."""
        x, y = pos
        radius = 0.035

        # Outer glow
        glow = Circle((x, y), radius=radius * 2.2, facecolor=color,
                      alpha=0.15, edgecolor='none', zorder=4)
        ax.add_patch(glow)

        # Mid glow
        mid_glow = Circle((x, y), radius=radius * 1.5, facecolor=color,
                          alpha=0.25, edgecolor='none', zorder=4)
        ax.add_patch(mid_glow)

        # Core circle
        core = Circle((x, y), radius=radius, facecolor=color,
                      edgecolor='white', linewidth=1.5, alpha=0.9, zorder=5)
        ax.add_patch(core)

        # Region abbreviation
        ax.text(x, y, abbr, ha='center', va='center', fontsize=7,
                fontweight='bold', color='white', zorder=6)

        # Protocol label below
        ax.text(x, y - radius - 0.025, proto_labels, ha='center', va='top',
                fontsize=5.5, color=color, fontweight='bold', zorder=6,
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white',
                         edgecolor=color, alpha=0.85, linewidth=0.5))
