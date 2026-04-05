"""Data-driven chart builders for the SOZO long-document pipeline.

ChartBuilder constructs CanonicalChart objects AND renders them to PNG files
using matplotlib (non-interactive Agg backend).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from sozo_generator.schemas.canonical import CanonicalChart
from sozo_generator.schemas.condition import ConditionSchema

# ---------------------------------------------------------------------------
# Style constants
# ---------------------------------------------------------------------------

SOZO_PURPLE = "#6B4FA0"
SOZO_PURPLE_LIGHT = "#9B7FD0"
SOZO_NAVY = "#0D2137"
SOZO_TEAL = "#1A7A8A"
BAR_PALETTE = [
    "#6B4FA0",
    "#1A7A8A",
    "#E07B39",
    "#2E75B6",
    "#996600",
    "#CC0000",
    "#20B2AA",
    "#7B68EE",
    "#2E6DA4",
]

# Evidence level → numeric score
_EVIDENCE_SCORES: dict[str, int] = {
    "very_low": 1,
    "low": 2,
    "medium": 3,
    "high": 4,
    "highest": 5,
    "missing": 0,
}

_EVIDENCE_LABELS: dict[str, str] = {
    "very_low": "Very Low",
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "highest": "Highest",
    "missing": "—",
}

# All six FNON networks in display order
_FNON_NETWORKS = ["DMN", "CEN", "SN", "SMN", "LIMBIC", "ATTENTION"]


def _ev_score(level) -> int:
    if level is None:
        return 0
    val = level.value if hasattr(level, "value") else str(level)
    return _EVIDENCE_SCORES.get(val.lower(), 0)


def _ev_label(level) -> str:
    if level is None:
        return "—"
    val = level.value if hasattr(level, "value") else str(level)
    return _EVIDENCE_LABELS.get(val.lower(), val.title())


def _apply_grid_style(ax) -> None:
    """Apply clean SOZO chart style."""
    ax.set_facecolor("#F8F8FA")
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.8, linestyle="--", alpha=0.8)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#AAAAAA")
        ax.spines[spine].set_linewidth(0.8)


class ChartBuilder:
    """Builds and renders data-driven charts for clinical documents."""

    def __init__(self, output_dir: str = "outputs/assets") -> None:
        self.output_dir = output_dir

    # ------------------------------------------------------------------
    # Evidence bar chart
    # ------------------------------------------------------------------

    def build_evidence_bar_chart(
        self,
        condition: ConditionSchema,
        output_path: Optional[str] = None,
    ) -> tuple[CanonicalChart, str]:
        """Bar chart: modalities vs evidence level (1=Very Low … 5=Highest).

        Returns (CanonicalChart, output_path).
        """
        # Collect best evidence score per modality
        modality_scores: dict[str, int] = {}
        for target in condition.stimulation_targets:
            mod_val = (
                target.modality.value
                if hasattr(target.modality, "value")
                else str(target.modality)
            )
            mod_key = mod_val.upper()
            score = _ev_score(target.evidence_level)
            if score > modality_scores.get(mod_key, 0):
                modality_scores[mod_key] = score

        if not modality_scores:
            modality_scores = {"N/A": 0}

        labels = sorted(modality_scores.keys())
        scores = [modality_scores[k] for k in labels]

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor("#FFFFFF")
        _apply_grid_style(ax)

        x_pos = range(len(labels))
        bars = ax.bar(
            x_pos,
            scores,
            color=[BAR_PALETTE[i % len(BAR_PALETTE)] for i in range(len(labels))],
            edgecolor="white",
            linewidth=0.5,
            width=0.6,
        )

        # Value labels on bars
        for bar, score in zip(bars, scores):
            label_text = list(_EVIDENCE_LABELS.values())[score - 1] if 1 <= score <= 5 else "—"
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.05,
                label_text,
                ha="center",
                va="bottom",
                fontsize=8,
                color=SOZO_NAVY,
                fontweight="bold",
            )

        ax.set_xticks(list(x_pos))
        ax.set_xticklabels(labels, fontsize=10, color=SOZO_NAVY)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(["Very Low", "Low", "Medium", "High", "Highest"], fontsize=9)
        ax.set_ylim(0, 6)
        ax.set_xlabel("Modality", fontsize=11, color=SOZO_NAVY, labelpad=8)
        ax.set_ylabel("Evidence Level", fontsize=11, color=SOZO_NAVY, labelpad=8)
        title = f"Evidence Levels by Modality — {condition.display_name}"
        ax.set_title(title, fontsize=13, color=SOZO_NAVY, pad=14, fontweight="bold")
        fig.tight_layout()

        if output_path is None:
            output_path = self._ensure_output_dir(
                str(Path(self.output_dir) / f"{condition.slug}_evidence_bar.png")
            )
        saved = self._save_fig(fig, output_path)
        plt.close(fig)

        chart = CanonicalChart(
            title=title,
            chart_type="bar",
            data={"modalities": labels, "scores": scores},
            x_label="Modality",
            y_label="Evidence Level (1–5)",
            output_path=saved,
        )
        return chart, saved

    # ------------------------------------------------------------------
    # Session timeline chart
    # ------------------------------------------------------------------

    def build_session_timeline_chart(
        self,
        condition: ConditionSchema,
        protocol_id: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> tuple[CanonicalChart, str]:
        """Horizontal timeline: Baseline → Acute → Maintenance → Follow-up.

        Returns (CanonicalChart, output_path).
        """
        # Resolve protocol
        proto = None
        if protocol_id:
            for p in condition.protocols:
                if p.protocol_id == protocol_id:
                    proto = p
                    break
        if proto is None and condition.protocols:
            proto = condition.protocols[0]

        session_total = (proto.session_count or 20) if proto else 20
        params = (proto.parameters or {}) if proto else {}
        freq_str = str(params.get("frequency") or params.get("freq") or "3×/week")

        # Phase definitions
        phases = ["Baseline", "Acute Treatment", "Maintenance", "Follow-up"]
        durations = [1, max(session_total - 3, 10), max(session_total - 12, 2), 1]
        colors = [SOZO_TEAL, SOZO_PURPLE, "#E07B39", "#2E75B6"]
        phase_notes = [
            "Assessment",
            freq_str,
            "1–2×/month",
            "3-month endpoint",
        ]

        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#F8F8FA")
        ax.axis("off")

        total = sum(durations)
        x_cursor = 0.0
        bar_y = 0.45
        bar_h = 0.25

        for phase, dur, color, note in zip(phases, durations, colors, phase_notes):
            width = dur / total
            ax.barh(
                bar_y,
                width,
                left=x_cursor,
                height=bar_h,
                color=color,
                edgecolor="white",
                linewidth=0.8,
            )
            center_x = x_cursor + width / 2
            ax.text(
                center_x,
                bar_y,
                phase,
                ha="center",
                va="center",
                fontsize=9,
                color="white",
                fontweight="bold",
            )
            ax.text(
                center_x,
                bar_y - 0.22,
                note,
                ha="center",
                va="top",
                fontsize=8,
                color=SOZO_NAVY,
            )
            ax.text(
                center_x,
                bar_y + 0.18,
                f"{dur} sess.",
                ha="center",
                va="bottom",
                fontsize=7.5,
                color=SOZO_NAVY,
            )
            x_cursor += width

        title = f"Session Timeline — {condition.display_name}"
        ax.set_title(title, fontsize=12, color=SOZO_NAVY, pad=10, fontweight="bold")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        fig.tight_layout()

        if output_path is None:
            output_path = self._ensure_output_dir(
                str(Path(self.output_dir) / f"{condition.slug}_session_timeline.png")
            )
        saved = self._save_fig(fig, output_path)
        plt.close(fig)

        chart = CanonicalChart(
            title=title,
            chart_type="timeline",
            data={
                "phases": phases,
                "durations": durations,
                "total_sessions": session_total,
            },
            x_label="Treatment Timeline",
            y_label="",
            output_path=saved,
        )
        return chart, saved

    # ------------------------------------------------------------------
    # Network dysfunction radar
    # ------------------------------------------------------------------

    def build_network_dysfunction_radar(
        self,
        condition: ConditionSchema,
        output_path: Optional[str] = None,
    ) -> tuple[CanonicalChart, str]:
        """Radar chart of 6 FNON networks with dysfunction severity encoded.

        Encoding: hypo=1, normal=2, hyper=3. Missing network=0 (not implicated).
        Returns (CanonicalChart, output_path).
        """
        _dysfunction_scores = {"hypo": 1, "normal": 2, "hyper": 3}

        # Build lookup
        profile_scores: dict[str, int] = {}
        for profile in condition.network_profiles:
            net_key = (
                profile.network.value.upper()
                if hasattr(profile.network, "value")
                else str(profile.network).upper()
            )
            dys_val = (
                profile.dysfunction.value
                if hasattr(profile.dysfunction, "value")
                else str(profile.dysfunction)
            )
            profile_scores[net_key] = _dysfunction_scores.get(dys_val.lower(), 0)

        networks = _FNON_NETWORKS
        values = [profile_scores.get(n, 0) for n in networks]

        # Close the radar by repeating the first element
        angles = np.linspace(0, 2 * np.pi, len(networks), endpoint=False).tolist()
        angles += angles[:1]
        values_closed = values + values[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#F8F8FA")

        ax.plot(angles, values_closed, color=SOZO_PURPLE, linewidth=2.5, linestyle="solid")
        ax.fill(angles, values_closed, color=SOZO_PURPLE, alpha=0.2)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(networks, fontsize=11, color=SOZO_NAVY, fontweight="bold")
        ax.set_yticks([0, 1, 2, 3])
        ax.set_yticklabels(["", "Hypo", "Normal", "Hyper"], fontsize=8, color="#888888")
        ax.set_ylim(0, 3)
        ax.grid(color="#DDDDDD", linewidth=0.7, linestyle="--", alpha=0.8)

        title = f"Network Dysfunction Profile — {condition.display_name}"
        ax.set_title(title, fontsize=13, color=SOZO_NAVY, pad=20, fontweight="bold")
        fig.tight_layout()

        if output_path is None:
            output_path = self._ensure_output_dir(
                str(Path(self.output_dir) / f"{condition.slug}_network_radar.png")
            )
        saved = self._save_fig(fig, output_path)
        plt.close(fig)

        chart = CanonicalChart(
            title=title,
            chart_type="radar",
            data={"networks": networks, "scores": values},
            x_label="",
            y_label="Dysfunction Severity",
            output_path=saved,
        )
        return chart, saved

    # ------------------------------------------------------------------
    # Responder tracking chart
    # ------------------------------------------------------------------

    def build_responder_tracking_chart(
        self,
        condition: ConditionSchema,
        output_path: Optional[str] = None,
    ) -> tuple[CanonicalChart, str]:
        """Bar chart showing responder categories.

        Uses placeholder population distributions when real data unavailable.
        Returns (CanonicalChart, output_path).
        """
        # Use responder criteria count to drive category count; placeholder values
        n_criteria = len(condition.responder_criteria)
        if n_criteria >= 2:
            categories = ["Full Responder", "Partial Responder", "Non-Responder"]
            pct = [42, 35, 23]
        else:
            categories = ["Responder", "Non-Responder"]
            pct = [58, 42]

        colors = [SOZO_PURPLE, SOZO_TEAL, "#E07B39"][: len(categories)]

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor("#FFFFFF")
        _apply_grid_style(ax)

        bars = ax.bar(
            categories,
            pct,
            color=colors,
            edgecolor="white",
            linewidth=0.5,
            width=0.5,
        )

        for bar, val in zip(bars, pct):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.8,
                f"{val}%",
                ha="center",
                va="bottom",
                fontsize=10,
                color=SOZO_NAVY,
                fontweight="bold",
            )

        ax.set_ylim(0, max(pct) + 15)
        ax.set_ylabel("Estimated Proportion (%)", fontsize=11, color=SOZO_NAVY, labelpad=8)
        title = f"Responder Categories — {condition.display_name}"
        ax.set_title(title, fontsize=13, color=SOZO_NAVY, pad=14, fontweight="bold")

        # Placeholder note
        ax.text(
            0.99,
            0.02,
            "* Illustrative estimates — replace with site data",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=7,
            color="#999999",
            style="italic",
        )
        fig.tight_layout()

        if output_path is None:
            output_path = self._ensure_output_dir(
                str(Path(self.output_dir) / f"{condition.slug}_responder_tracking.png")
            )
        saved = self._save_fig(fig, output_path)
        plt.close(fig)

        chart = CanonicalChart(
            title=title,
            chart_type="bar",
            data={"categories": categories, "percentages": pct},
            x_label="Category",
            y_label="Proportion (%)",
            output_path=saved,
        )
        return chart, saved

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_output_dir(self, path: str) -> str:
        """Create parent directory if needed, return path unchanged."""
        parent = Path(path).parent
        parent.mkdir(parents=True, exist_ok=True)
        return path

    def _save_fig(self, fig, path: str) -> str:
        """Save matplotlib figure to path and return the path."""
        self._ensure_output_dir(path)
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        return path
