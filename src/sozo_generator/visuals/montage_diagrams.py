"""
10-20 EEG montage diagram generator — creates electrode placement and
stimulation montage figures from structured protocol data.

Generates:
- 10-20 system head maps with electrode positions
- tDCS montage diagrams (anode/cathode placement)
- TPS target region diagrams
- Protocol summary visual cards
"""
from __future__ import annotations
import logging
import math
from pathlib import Path
from typing import Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle
import numpy as np

logger = logging.getLogger(__name__)

# Standard 10-20 electrode positions (normalized coordinates on unit circle head)
# Format: {electrode_name: (x, y)} where (0,0) is center, head radius ~1.0
ELECTRODES_10_20 = {
    # Midline
    "Fpz": (0.0, 0.90), "Fz": (0.0, 0.55), "Cz": (0.0, 0.0),
    "Pz": (0.0, -0.55), "Oz": (0.0, -0.90),
    # Left hemisphere
    "Fp1": (-0.30, 0.85), "F3": (-0.35, 0.45), "C3": (-0.50, 0.0),
    "P3": (-0.35, -0.45), "O1": (-0.30, -0.85),
    "F7": (-0.70, 0.55), "T3": (-0.90, 0.0), "T5": (-0.70, -0.55),
    # Right hemisphere
    "Fp2": (0.30, 0.85), "F4": (0.35, 0.45), "C4": (0.50, 0.0),
    "P4": (0.35, -0.45), "O2": (0.30, -0.85),
    "F8": (0.70, 0.55), "T4": (0.90, 0.0), "T6": (0.70, -0.55),
    # Ears
    "A1": (-1.05, 0.0), "A2": (1.05, 0.0),
}

# Common tDCS target → electrode mapping
TARGET_TO_ELECTRODE = {
    "dlpfc": {"left": "F3", "right": "F4"},
    "m1": {"left": "C3", "right": "C4"},
    "sma": {"midline": "Fz"},
    "pfc": {"left": "Fp1", "right": "Fp2"},
    "tpj": {"left": "P3", "right": "P4"},
    "ofc": {"left": "Fp1", "right": "Fp2"},
    "motor_cortex": {"left": "C3", "right": "C4"},
    "dorsolateral_prefrontal": {"left": "F3", "right": "F4"},
    "primary_motor": {"left": "C3", "right": "C4"},
    "supplementary_motor": {"midline": "Fz"},
    "broca": {"left": "F7"},
    "wernicke": {"left": "T5"},
}

# Colors
ANODE_COLOR = "#E74C3C"    # Red
CATHODE_COLOR = "#3498DB"  # Blue
TARGET_COLOR = "#996600"   # SOZO brown
NEUTRAL_COLOR = "#CCCCCC"
HEAD_COLOR = "#FFF5E6"
GRID_COLOR = "#DDDDDD"


class MontageDiagramGenerator:
    """Generates 10-20 EEG and stimulation montage diagrams."""

    def generate_montage_diagram(
        self,
        anode: str,
        cathode: str,
        condition_name: str = "",
        protocol_label: str = "",
        modality: str = "tDCS",
        output_dir: Path = None,
        filename: str = None,
    ) -> Optional[Path]:
        """Generate a head diagram showing anode/cathode placement."""
        fig, ax = plt.subplots(1, 1, figsize=(8, 9), dpi=150)
        ax.set_xlim(-1.4, 1.4)
        ax.set_ylim(-1.3, 1.4)
        ax.set_aspect("equal")
        ax.axis("off")

        # Draw head outline
        head = Circle((0, 0), 1.0, fill=True, facecolor=HEAD_COLOR,
                      edgecolor="#333333", linewidth=2)
        ax.add_patch(head)

        # Nose indicator
        ax.plot([-0.08, 0, 0.08], [1.0, 1.12, 1.0], color="#333333", linewidth=2)

        # Ears
        left_ear = patches.Ellipse((-1.05, 0), 0.12, 0.3, facecolor=HEAD_COLOR,
                                    edgecolor="#333333", linewidth=1.5)
        right_ear = patches.Ellipse((1.05, 0), 0.12, 0.3, facecolor=HEAD_COLOR,
                                     edgecolor="#333333", linewidth=1.5)
        ax.add_patch(left_ear)
        ax.add_patch(right_ear)

        # Draw all electrodes
        anode_upper = anode.upper() if anode else ""
        cathode_upper = cathode.upper() if cathode else ""

        for name, (x, y) in ELECTRODES_10_20.items():
            if name in ("A1", "A2"):
                continue
            if name == anode_upper:
                color = ANODE_COLOR
                size = 0.10
                zorder = 10
            elif name == cathode_upper:
                color = CATHODE_COLOR
                size = 0.10
                zorder = 10
            else:
                color = NEUTRAL_COLOR
                size = 0.06
                zorder = 5

            circle = Circle((x, y), size, facecolor=color, edgecolor="#333333",
                           linewidth=1, zorder=zorder)
            ax.add_patch(circle)
            # Label
            fontsize = 8 if name not in (anode_upper, cathode_upper) else 10
            fontweight = "bold" if name in (anode_upper, cathode_upper) else "normal"
            ax.text(x, y - size - 0.06, name, ha="center", va="top",
                   fontsize=fontsize, fontweight=fontweight, color="#333333")

        # Title and legend
        title = f"{modality} Montage"
        if protocol_label:
            title += f"\n{protocol_label}"
        if condition_name:
            title += f"\n{condition_name}"
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

        # Legend
        ax.text(-1.3, -1.15, f"● Anode: {anode_upper}", color=ANODE_COLOR,
               fontsize=11, fontweight="bold")
        ax.text(-1.3, -1.25, f"● Cathode: {cathode_upper}", color=CATHODE_COLOR,
               fontsize=11, fontweight="bold")
        ax.text(0.5, -1.15, f"SOZO Brain Center", color="#666666",
               fontsize=8, style="italic")

        # Save
        if output_dir is None:
            output_dir = Path("outputs/visuals")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            safe_label = (protocol_label or "montage").lower().replace(" ", "_")[:30]
            filename = f"montage_{safe_label}.png"

        out_path = output_dir / filename
        fig.savefig(str(out_path), bbox_inches="tight", facecolor="white")
        plt.close(fig)
        logger.info("Generated montage diagram: %s", out_path)
        return out_path

    def generate_target_diagram(
        self,
        target_regions: list[str],
        condition_name: str = "",
        modality: str = "",
        output_dir: Path = None,
        filename: str = None,
    ) -> Optional[Path]:
        """Generate a head diagram highlighting target stimulation regions."""
        fig, ax = plt.subplots(1, 1, figsize=(8, 9), dpi=150)
        ax.set_xlim(-1.4, 1.4)
        ax.set_ylim(-1.3, 1.4)
        ax.set_aspect("equal")
        ax.axis("off")

        # Head
        head = Circle((0, 0), 1.0, fill=True, facecolor=HEAD_COLOR,
                      edgecolor="#333333", linewidth=2)
        ax.add_patch(head)
        ax.plot([-0.08, 0, 0.08], [1.0, 1.12, 1.0], color="#333333", linewidth=2)

        # Find electrodes for target regions
        highlighted = set()
        for target in target_regions:
            target_lower = target.lower().replace(" ", "_").replace("(", "").replace(")", "")
            for key, electrodes in TARGET_TO_ELECTRODE.items():
                if key in target_lower or target_lower in key:
                    for pos_name in electrodes.values():
                        highlighted.add(pos_name)

        # Draw electrodes
        for name, (x, y) in ELECTRODES_10_20.items():
            if name in ("A1", "A2"):
                continue
            if name in highlighted:
                color = TARGET_COLOR
                size = 0.10
            else:
                color = NEUTRAL_COLOR
                size = 0.05
            circle = Circle((x, y), size, facecolor=color, edgecolor="#333333",
                           linewidth=1, zorder=5 if name not in highlighted else 10)
            ax.add_patch(circle)
            if name in highlighted:
                ax.text(x, y - size - 0.06, name, ha="center", va="top",
                       fontsize=10, fontweight="bold", color=TARGET_COLOR)

        title = f"Target Regions: {', '.join(target_regions[:3])}"
        if condition_name:
            title = f"{condition_name}\n{title}"
        ax.set_title(title, fontsize=13, fontweight="bold", pad=20)

        if output_dir is None:
            output_dir = Path("outputs/visuals")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        if filename is None:
            filename = "target_regions.png"
        out_path = output_dir / filename
        fig.savefig(str(out_path), bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return out_path

    def generate_protocol_card(
        self,
        protocol_label: str,
        modality: str,
        target_region: str,
        parameters: dict,
        condition_name: str = "",
        output_dir: Path = None,
        filename: str = None,
    ) -> Optional[Path]:
        """Generate a visual protocol summary card."""
        fig, ax = plt.subplots(1, 1, figsize=(10, 5), dpi=150)
        ax.axis("off")

        # Card background
        card = FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0.02",
                              facecolor="#FAFAFA", edgecolor="#996600", linewidth=2)
        ax.add_patch(card)

        # Title bar
        title_bar = FancyBboxPatch((0.02, 0.78), 0.96, 0.20, boxstyle="round,pad=0.01",
                                    facecolor="#996600", edgecolor="none")
        ax.add_patch(title_bar)
        ax.text(0.5, 0.88, protocol_label, ha="center", va="center",
               fontsize=14, fontweight="bold", color="white")
        ax.text(0.5, 0.80, f"{modality.upper()} — {condition_name}",
               ha="center", va="center", fontsize=10, color="#FFE0B2")

        # Parameters
        y = 0.70
        param_items = list(parameters.items())[:8]
        for key, value in param_items:
            label = key.replace("_", " ").title()
            ax.text(0.08, y, f"{label}:", fontsize=10, fontweight="bold", color="#333333")
            ax.text(0.45, y, str(value), fontsize=10, color="#555555")
            y -= 0.08

        # Target region
        ax.text(0.08, 0.08, f"Target: {target_region}", fontsize=10,
               fontweight="bold", color="#996600")
        ax.text(0.98, 0.04, "SOZO Brain Center", ha="right",
               fontsize=7, color="#999999", style="italic")

        if output_dir is None:
            output_dir = Path("outputs/visuals")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        if filename is None:
            safe = protocol_label.lower().replace(" ", "_")[:30]
            filename = f"protocol_card_{safe}.png"
        out_path = output_dir / filename
        fig.savefig(str(out_path), bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return out_path

    def generate_all_for_condition(
        self,
        condition,
        output_dir: Path,
    ) -> list[Path]:
        """Generate all montage and target diagrams for a condition's protocols."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = []

        # Target region diagram
        targets = [t.target_region for t in (condition.stimulation_targets or [])]
        if targets:
            p = self.generate_target_diagram(
                targets, condition.display_name,
                output_dir=output_dir,
                filename=f"{condition.slug}_targets.png",
            )
            if p:
                paths.append(p)

        # Per-protocol montage diagrams
        for proto in (condition.protocols or []):
            if proto.modality.value == "tdcs":
                anode = proto.parameters.get("anode", "")
                cathode = proto.parameters.get("cathode", "")
                if anode and cathode:
                    p = self.generate_montage_diagram(
                        anode=anode, cathode=cathode,
                        condition_name=condition.display_name,
                        protocol_label=proto.label,
                        modality="tDCS",
                        output_dir=output_dir,
                        filename=f"{condition.slug}_{proto.protocol_id}_montage.png",
                    )
                    if p:
                        paths.append(p)

            # Protocol card for all protocols
            p = self.generate_protocol_card(
                protocol_label=proto.label,
                modality=proto.modality.value,
                target_region=proto.target_region,
                parameters=proto.parameters,
                condition_name=condition.display_name,
                output_dir=output_dir,
                filename=f"{condition.slug}_{proto.protocol_id}_card.png",
            )
            if p:
                paths.append(p)

        logger.info("Generated %d visuals for %s", len(paths), condition.slug)
        return paths
