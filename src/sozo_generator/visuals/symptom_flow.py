"""
SOZO Brain Center — symptom → network → modality flow diagrams.
Shows how symptoms map to affected networks and treatment modalities.
"""

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
PRIMARY_BLUE = "#2E75B6"
DARK_BLUE = "#1B3A5C"
ACCENT_RED = "#CC0000"
LIGHT_BLUE = "#BDD7EE"
LIGHT_BROWN = "#F5E6C8"

# Column background colors
COL_COLORS = {
    'symptoms':   LIGHT_BROWN,
    'networks':   LIGHT_BLUE,
    'modalities': PRIMARY_BLUE,
}

# Which severities are shown in the Networks column
_SHOWN_SEVERITIES = {'high', 'severe', 'moderate', 'medium'}

# Human-readable modality labels
MODALITY_LABELS = {
    'tdcs':       'tDCS',
    'tps':        'TPS',
    'tavns':      'taVNS',
    'ces':        'CES',
    'multimodal': 'Multimodal',
}

_MAX_SYMPTOMS = 5
_MAX_NETWORKS = 4
_MAX_MODALITIES = 6


def _wrap_text(text: str, max_chars: int = 22) -> str:
    """Rudimentary word-wrap for box labels."""
    if len(text) <= max_chars:
        return text
    words = text.split()
    lines, current = [], []
    for w in words:
        if sum(len(x) + 1 for x in current) + len(w) > max_chars:
            if current:
                lines.append(' '.join(current))
            current = [w]
        else:
            current.append(w)
    if current:
        lines.append(' '.join(current))
    return '\n'.join(lines)


def _draw_box(ax, x_center, y_center, width, height, label, bg_color, text_color='#1A1A1A', fontsize=8):
    """Draw a rounded rectangle box with centered text."""
    box = FancyBboxPatch(
        (x_center - width / 2, y_center - height / 2),
        width, height,
        boxstyle="round,pad=0.01",
        facecolor=bg_color,
        edgecolor='white',
        linewidth=1.2,
        zorder=3,
    )
    ax.add_patch(box)
    ax.text(
        x_center, y_center,
        label,
        ha='center', va='center',
        fontsize=fontsize,
        color=text_color,
        fontweight='bold',
        zorder=4,
        wrap=False,
    )


def _draw_arrow(ax, x0, y0, x1, y1):
    """Draw a simple horizontal arrow between two points."""
    ax.annotate(
        '',
        xy=(x1, y1),
        xytext=(x0, y0),
        arrowprops=dict(
            arrowstyle='-|>',
            color='#555555',
            lw=1.2,
            mutation_scale=12,
        ),
        zorder=2,
    )


class SymptomFlowGenerator:
    """Generates three-column symptom → network → modality flow diagrams."""

    def generate_symptom_flow(self, condition, output_dir: Path) -> Path | None:
        """
        Three-column layout:
          Symptoms (Light Brown) | Networks (Light Blue) | Modalities (Primary Blue)
        with arrows between columns.

        Returns output Path, or None on failure.
        """
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            out_path = output_dir / f"{condition.slug}_symptom_flow.png"

            # --- Collect data ---
            symptoms = self._get_symptoms(condition)[:_MAX_SYMPTOMS]
            networks = self._get_networks(condition)[:_MAX_NETWORKS]
            modalities = self._get_modalities(condition)[:_MAX_MODALITIES]

            if not symptoms:
                symptoms = ['(no symptoms listed)']
            if not networks:
                networks = ['(no networks)']
            if not modalities:
                modalities = ['(no modalities)']

            n_rows = max(len(symptoms), len(networks), len(modalities))
            fig_height = max(5.0, n_rows * 0.9 + 2.0)

            fig, ax = plt.subplots(figsize=(10, fig_height))
            ax.set_xlim(0, 10)
            ax.set_ylim(0, fig_height)
            ax.axis('off')
            fig.patch.set_facecolor('#FAFAFA')
            ax.set_facecolor('#FAFAFA')

            # Column x-centers and widths
            col_xs = [1.8, 5.0, 8.2]
            col_w = 2.8
            box_h = 0.56
            col_y_top = fig_height - 1.4

            col_defs = [
                ('Symptoms',   symptoms,   COL_COLORS['symptoms'],   '#1A1A1A'),
                ('Networks',   networks,   COL_COLORS['networks'],   DARK_BLUE),
                ('Modalities', modalities, COL_COLORS['modalities'], 'white'),
            ]

            # Draw column header backgrounds (full column height)
            for i, (header, items, bg, tc) in enumerate(col_defs):
                col_x = col_xs[i]
                col_bg_h = n_rows * (box_h + 0.25) + 0.3
                bg_rect = FancyBboxPatch(
                    (col_x - col_w / 2 - 0.05, col_y_top - col_bg_h - 0.1),
                    col_w + 0.10,
                    col_bg_h + 0.5,
                    boxstyle="round,pad=0.05",
                    facecolor=bg,
                    edgecolor='#CCCCCC',
                    linewidth=1,
                    alpha=0.30,
                    zorder=1,
                )
                ax.add_patch(bg_rect)

                # Header
                ax.text(
                    col_x, col_y_top,
                    header,
                    ha='center', va='center',
                    fontsize=10,
                    fontweight='bold',
                    color=DARK_BLUE if tc != 'white' else PRIMARY_BLUE,
                    zorder=5,
                )

            # Draw item boxes
            box_centers: list[list[tuple[float, float]]] = [[], [], []]
            for col_i, (header, items, bg, tc) in enumerate(col_defs):
                col_x = col_xs[col_i]
                for row_i, item in enumerate(items):
                    y = col_y_top - 0.55 - row_i * (box_h + 0.22)
                    label = _wrap_text(item, 22)
                    _draw_box(ax, col_x, y, col_w - 0.15, box_h, label, bg, tc, fontsize=7.5)
                    box_centers[col_i].append((col_x, y))

            # Arrows: symptoms → networks (fan-out from each symptom to first network centroid)
            net_ys = [c[1] for c in box_centers[1]] if box_centers[1] else []
            net_mid_y = np.mean(net_ys) if net_ys else (col_y_top - 0.55)
            sym_right_x = col_xs[0] + (col_w - 0.15) / 2
            net_left_x  = col_xs[1] - (col_w - 0.15) / 2

            for sym_x, sym_y in box_centers[0]:
                _draw_arrow(ax, sym_right_x, sym_y, net_left_x, net_mid_y)

            # Arrows: networks → modalities (fan-out from each network to modalities centroid)
            mod_ys = [c[1] for c in box_centers[2]] if box_centers[2] else []
            mod_mid_y = np.mean(mod_ys) if mod_ys else (col_y_top - 0.55)
            net_right_x = col_xs[1] + (col_w - 0.15) / 2
            mod_left_x  = col_xs[2] - (col_w - 0.15) / 2

            for net_x, net_y in box_centers[1]:
                _draw_arrow(ax, net_right_x, net_y, mod_left_x, mod_mid_y)

            # Title
            cond_name = getattr(condition, 'display_name', None) or getattr(condition, 'name', condition.slug)
            ax.set_title(
                f"{cond_name} — Symptom · Network · Modality Flow",
                fontsize=12,
                fontweight='bold',
                color=DARK_BLUE,
                pad=10,
            )

            plt.tight_layout()
            fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
            plt.close(fig)
            logger.info("Symptom flow saved to %s", out_path)
            return out_path

        except Exception as exc:
            logger.warning("SymptomFlowGenerator.generate_symptom_flow failed: %s", exc, exc_info=True)
            return None

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------

    def _get_symptoms(self, condition) -> list[str]:
        """Return up to 5 key features from the first phenotype, or core_symptoms."""
        phenotypes = getattr(condition, 'phenotypes', [])
        if phenotypes:
            features = getattr(phenotypes[0], 'key_features', [])
            if features:
                return list(features)[:_MAX_SYMPTOMS]
        return list(getattr(condition, 'core_symptoms', []))[:_MAX_SYMPTOMS]

    def _get_networks(self, condition) -> list[str]:
        """Return network names for high/medium severity profiles."""
        profiles = getattr(condition, 'network_profiles', [])
        result = []
        for p in profiles:
            sev = getattr(p, 'severity', 'moderate')
            if sev in _SHOWN_SEVERITIES:
                key = p.network.value.upper() if hasattr(p.network, 'value') else str(p.network).upper()
                result.append(key)
        return result[:_MAX_NETWORKS]

    def _get_modalities(self, condition) -> list[str]:
        """Return unique modality labels from stimulation targets."""
        targets = getattr(condition, 'stimulation_targets', [])
        seen: set[str] = set()
        result = []
        for t in targets:
            mod = getattr(t, 'modality', None)
            if mod is None:
                continue
            val = mod.value if hasattr(mod, 'value') else str(mod)
            label = MODALITY_LABELS.get(val, val.upper())
            if label not in seen:
                seen.add(label)
                result.append(label)
        return result
