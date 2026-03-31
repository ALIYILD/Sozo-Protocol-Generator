"""
SOZO Brain Center — FNON network diagrams.
Generates network involvement diagrams showing which of the 6 FNON networks
are affected and their interconnections.
"""

import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
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

# Per-network display colors
NETWORK_COLORS = {
    "DMN":       "#2E75B6",
    "CEN":       "#996600",
    "SN":        "#CC0000",
    "SMN":       "#1B3A5C",
    "LIMBIC":    "#7B68EE",
    "ATTENTION": "#20B2AA",
}

# Hexagon positions (normalized 0–1)
NETWORK_POSITIONS = {
    "DMN":       (0.50, 0.85),
    "CEN":       (0.85, 0.62),
    "SN":        (0.85, 0.38),
    "SMN":       (0.50, 0.15),
    "LIMBIC":    (0.15, 0.38),
    "ATTENTION": (0.15, 0.62),
}

# Which networks share functional hubs / connections
NETWORK_ADJACENCY = [
    ("DMN", "CEN"),
    ("DMN", "SN"),
    ("DMN", "LIMBIC"),
    ("CEN", "SN"),
    ("CEN", "ATTENTION"),
    ("SN", "LIMBIC"),
    ("SN", "SMN"),
    ("SMN", "ATTENTION"),
    ("LIMBIC", "DMN"),
]

# Node radius (axes units)
_NODE_RADIUS = 0.085

# Severity → (radius_scale, alpha)
_SEVERITY_STYLE = {
    "high":     (1.00, 0.92),
    "severe":   (1.00, 0.92),
    "moderate": (0.82, 0.75),
    "medium":   (0.82, 0.75),
    "mild":     (0.65, 0.58),
    "low":      (0.65, 0.58),
}


class NetworkDiagramGenerator:
    """Generates FNON network involvement hexagon diagrams."""

    def generate_network_diagram(self, condition, output_dir: Path) -> Path | None:
        """
        Draw 6 FNON network nodes in a hexagon.  Nodes present in
        condition.network_profiles are colored; absent ones are gray.
        Edges connect networks that share functional hubs.

        Returns output Path, or None on failure.
        """
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            out_path = output_dir / f"{condition.slug}_network_diagram.png"

            # Build lookup: network_key_upper → NetworkProfile
            profiles = getattr(condition, 'network_profiles', [])
            profile_map: dict[str, object] = {}
            for np_obj in profiles:
                key = np_obj.network.value.upper() if hasattr(np_obj.network, 'value') else str(np_obj.network).upper()
                profile_map[key] = np_obj

            fig, ax = plt.subplots(figsize=(8, 8))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect('equal')
            ax.axis('off')
            fig.patch.set_facecolor('#F8F8F8')
            ax.set_facecolor('#F8F8F8')

            # Draw edges first (behind nodes)
            for net_a, net_b in NETWORK_ADJACENCY:
                xa, ya = NETWORK_POSITIONS[net_a]
                xb, yb = NETWORK_POSITIONS[net_b]
                both_present = net_a in profile_map and net_b in profile_map
                edge_color = '#AAAAAA' if not both_present else '#666666'
                edge_lw = 0.8 if not both_present else 1.4
                ax.plot(
                    [xa, xb], [ya, yb],
                    color=edge_color,
                    linewidth=edge_lw,
                    linestyle='--' if not both_present else '-',
                    alpha=0.6,
                    zorder=1,
                )

            # Draw nodes
            for net_name, (nx_, ny_) in NETWORK_POSITIONS.items():
                profile = profile_map.get(net_name)
                if profile is not None:
                    base_color = NETWORK_COLORS[net_name]
                    severity_raw = getattr(profile, 'severity', 'moderate')
                    scale, alpha = _SEVERITY_STYLE.get(severity_raw, (0.82, 0.75))
                    severity_label = severity_raw
                else:
                    base_color = '#CCCCCC'
                    scale = 0.55
                    alpha = 0.45
                    severity_label = ''

                radius = _NODE_RADIUS * scale

                circle = plt.Circle(
                    (nx_, ny_),
                    radius=radius,
                    facecolor=base_color,
                    edgecolor='white',
                    linewidth=2,
                    alpha=alpha,
                    zorder=2,
                )
                ax.add_patch(circle)

                # Network abbreviation
                ax.text(
                    nx_, ny_ + 0.008,
                    net_name,
                    ha='center', va='center',
                    fontsize=9,
                    fontweight='bold',
                    color='white',
                    zorder=3,
                )

                # Severity sub-label
                if severity_label:
                    ax.text(
                        nx_, ny_ - 0.025,
                        severity_label,
                        ha='center', va='center',
                        fontsize=6.5,
                        color='white',
                        alpha=0.9,
                        zorder=3,
                    )

            # Title
            cond_name = getattr(condition, 'display_name', None) or getattr(condition, 'name', condition.slug)
            ax.set_title(
                f"{cond_name}\nFNON Network Involvement",
                fontsize=13,
                fontweight='bold',
                color=DARK_BLUE,
                pad=12,
            )

            # Legend patches
            legend_handles = [
                mpatches.Patch(facecolor=NETWORK_COLORS[n], label=n)
                for n in NETWORK_COLORS
            ]
            legend_handles.append(
                mpatches.Patch(facecolor='#CCCCCC', label='Not involved')
            )
            ax.legend(
                handles=legend_handles,
                loc='lower center',
                ncol=4,
                fontsize=7.5,
                framealpha=0.85,
                edgecolor='#CCCCCC',
                bbox_to_anchor=(0.5, -0.02),
            )

            plt.tight_layout()
            fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
            plt.close(fig)
            logger.info("Network diagram saved to %s", out_path)
            return out_path

        except Exception as exc:
            logger.warning("NetworkDiagramGenerator.generate_network_diagram failed: %s", exc, exc_info=True)
            return None
