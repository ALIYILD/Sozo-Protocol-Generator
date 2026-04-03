"""
Network Connectivity Heatmap Generator.

Produces a 6x6 inter-network connectivity matrix with dysfunction overlay,
showing which brain networks are affected and their inter-relationships
for a given condition.

Visual features:
- 6x6 matrix (DMN, CEN, SN, SMN, LIMBIC, ATTENTION)
- Color intensity = connection strength / dysfunction severity
- Dysfunction indicators on diagonal (hypo/hyper)
- FNON-aligned color coding
- Clean clinical heatmap styling
"""
from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

logger = logging.getLogger(__name__)

NAVY = "#0D2137"
TEAL = "#1A7A8A"

# Canonical network order
NETWORKS = ["DMN", "CEN", "SN", "SMN", "LIMBIC", "ATN"]
NETWORK_LABELS = {
    "DMN": "Default Mode\nNetwork",
    "CEN": "Central Executive\nNetwork",
    "SN": "Salience\nNetwork",
    "SMN": "Sensorimotor\nNetwork",
    "LIMBIC": "Limbic/Emotional\nNetwork",
    "ATN": "Attention\nNetworks",
}
NETWORK_COLORS = {
    "DMN": "#8E44AD",
    "CEN": "#2E75B6",
    "SN": "#E74C3C",
    "SMN": "#27AE60",
    "LIMBIC": "#F39C12",
    "ATN": "#3498DB",
}

# Known inter-network connections (based on FNON framework)
# Values represent typical connectivity strength (0 = none, 1 = strong)
BASELINE_CONNECTIVITY = np.array([
    # DMN   CEN   SN    SMN   LIM   ATN
    [1.0,   0.6,  0.7,  0.3,  0.8,  0.4],  # DMN
    [0.6,   1.0,  0.8,  0.5,  0.4,  0.9],  # CEN
    [0.7,   0.8,  1.0,  0.6,  0.9,  0.7],  # SN
    [0.3,   0.5,  0.6,  1.0,  0.3,  0.5],  # SMN
    [0.8,   0.4,  0.9,  0.3,  1.0,  0.3],  # LIMBIC
    [0.4,   0.9,  0.7,  0.5,  0.3,  1.0],  # ATN
])


def generate_connectivity_heatmap(
    title: str,
    condition_name: str,
    network_dysfunctions: dict[str, dict],
    output_path: str | Path | None = None,
    figsize: tuple = (10, 9),
    dpi: int = 200,
) -> bytes:
    """Generate a 6x6 network connectivity heatmap.

    Args:
        title: Figure title
        condition_name: Condition display name
        network_dysfunctions: Dict mapping network key to:
            {
                "dysfunction": "hypo" | "hyper" | "normal",
                "severity": "mild" | "moderate" | "severe" | "high",
                "involved": bool
            }
        output_path: Save path
        figsize: Figure size
        dpi: Resolution

    Returns:
        PNG bytes
    """
    fig, ax = plt.subplots(figsize=figsize, facecolor="white")

    n = len(NETWORKS)

    # Build dysfunction-weighted connectivity matrix
    severity_weights = {
        "severe": 1.0, "high": 0.9, "moderate": 0.7,
        "medium": 0.6, "mild": 0.4, "low": 0.3, "normal": 0.1,
    }

    # Compute display matrix
    display_matrix = BASELINE_CONNECTIVITY.copy()
    for i, net in enumerate(NETWORKS):
        info = network_dysfunctions.get(net.lower(), network_dysfunctions.get(net, {}))
        if not info.get("involved", False):
            display_matrix[i, :] *= 0.15
            display_matrix[:, i] *= 0.15
        else:
            sev = info.get("severity", "moderate")
            w = severity_weights.get(sev, 0.5)
            display_matrix[i, i] = w

    # Custom colormap: white -> light color -> deep color
    cmap = plt.cm.YlOrRd

    # Plot heatmap
    im = ax.imshow(display_matrix, cmap=cmap, vmin=0, vmax=1,
                    aspect="equal", interpolation="nearest")

    # Grid lines
    for i in range(n + 1):
        ax.axhline(i - 0.5, color="white", linewidth=2)
        ax.axvline(i - 0.5, color="white", linewidth=2)

    # Cell values and dysfunction markers
    for i in range(n):
        for j in range(n):
            val = display_matrix[i, j]
            if val < 0.01:
                continue

            # Text color based on background
            text_color = "white" if val > 0.6 else NAVY

            if i == j:
                # Diagonal: show dysfunction type
                net = NETWORKS[i]
                info = network_dysfunctions.get(net.lower(), network_dysfunctions.get(net, {}))
                dys = info.get("dysfunction", "normal")
                sev = info.get("severity", "")

                if info.get("involved", False):
                    marker = "HYPO" if dys == "hypo" else ("HYPER" if dys == "hyper" else "")
                    ax.text(j, i, f"{marker}\n{sev}", ha="center", va="center",
                            fontsize=8, fontweight="bold", color=text_color)
                else:
                    ax.text(j, i, "—", ha="center", va="center",
                            fontsize=12, color="#CCCCCC")
            else:
                # Off-diagonal: show connectivity strength
                if val > 0.2:
                    ax.text(j, i, f"{val:.1f}", ha="center", va="center",
                            fontsize=7, color=text_color, alpha=0.8)

    # Labels
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))

    # Color-coded network labels
    xlabels, ylabels = [], []
    for net in NETWORKS:
        label = NETWORK_LABELS.get(net, net)
        xlabels.append(label)
        ylabels.append(label)

    ax.set_xticklabels(xlabels, fontsize=8, fontweight="bold", ha="center")
    ax.set_yticklabels(ylabels, fontsize=8, fontweight="bold", ha="right")
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")

    # Color the tick labels
    for i, net in enumerate(NETWORKS):
        color = NETWORK_COLORS.get(net, NAVY)
        ax.get_xticklabels()[i].set_color(color)
        ax.get_yticklabels()[i].set_color(color)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, shrink=0.7, aspect=20, pad=0.08)
    cbar.set_label("Dysfunction Severity / Connectivity", fontsize=9, color=NAVY)
    cbar.ax.tick_params(labelsize=8)

    # Title
    ax.set_title(f"\n{title}\n{condition_name}", fontsize=13, fontweight="bold",
                  color=NAVY, pad=20)

    # Branding
    fig.text(0.98, 0.02, "SOZO Brain Center", ha="right",
             fontsize=7, color="#AABBCC", style="italic")

    plt.tight_layout(pad=1.5)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    img_bytes = buf.read()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(img_bytes)
        logger.info(f"Connectivity heatmap saved: {output_path}")

    return img_bytes


def generate_connectivity_for_condition(condition, output_dir: str | Path) -> Optional[Path]:
    """Generate connectivity heatmap from a ConditionSchema."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build dysfunction map from network_profiles
    network_map = {
        "dmn": "DMN", "cen": "CEN", "sn": "SN",
        "smn": "SMN", "limbic": "LIMBIC", "attention": "ATN",
    }

    dysfunctions = {}
    for profile in condition.network_profiles:
        net_key = profile.network.value if hasattr(profile.network, "value") else str(profile.network)
        canonical = network_map.get(net_key, net_key.upper())
        dysfunctions[canonical] = {
            "dysfunction": profile.dysfunction.value if hasattr(profile.dysfunction, "value") else str(profile.dysfunction),
            "severity": profile.severity,
            "involved": True,
        }

    if not dysfunctions:
        return None

    out_path = output_dir / f"{condition.slug}_connectivity.png"
    generate_connectivity_heatmap(
        title="FNON Network Connectivity & Dysfunction Profile",
        condition_name=condition.display_name,
        network_dysfunctions=dysfunctions,
        output_path=str(out_path),
    )
    return out_path
