"""
SOZO Dose-Response Tracking Template Generator.

Produces a session-by-session treatment progress chart template for
clinicians to track patient improvement over a 12-session treatment
course (3 phases of 4 weeks).

Visual features:
- X axis: Session numbers (1-12) grouped by week phases
- Y axis: Primary outcome improvement (0-100%)
- Color-coded response zones (Responder / Partial / Non-Responder)
- Decision point annotations at weeks 4 and 8
- Optional expected trajectory curve
- SOZO branding footer
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

logger = logging.getLogger(__name__)

# SOZO brand colors
NAVY = "#0D2137"
TEAL = "#1A7A8A"
SOZO_BROWN = "#996600"
SOZO_BLUE = "#2E75B6"
SOZO_DARK_BLUE = "#1B3A5C"

# Zone colors
RESPONDER_GREEN = "#27AE60"
PARTIAL_YELLOW = "#F39C12"
NON_RESPONDER_RED = "#E74C3C"


def generate_dose_response(
    title: str = "Dose-Response Tracking Template",
    condition_name: str = "",
    primary_outcome: str = "Primary Outcome Score",
    sessions: int = 12,
    output_path: str | None = None,
    figsize: tuple[int, int] = (12, 6),
    dpi: int = 200,
) -> bytes:
    """
    Generate a dose-response tracking template chart.

    This produces an empty template with response zones and decision
    point annotations — no actual patient data is plotted.

    Parameters
    ----------
    title : str
        Main chart title.
    condition_name : str
        Condition name for subtitle.
    primary_outcome : str
        Label for the primary outcome measure (Y axis).
    sessions : int
        Total number of sessions (default 12).
    output_path : str | None
        If given, save PNG to this path.
    figsize : tuple
        Figure size in inches.
    dpi : int
        Output resolution.

    Returns
    -------
    bytes
        PNG image as bytes.
    """
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#FAFAFA")

    # Response zone bands
    ax.axhspan(50, 100, alpha=0.12, color=RESPONDER_GREEN, zorder=1)
    ax.axhspan(25, 50, alpha=0.12, color=PARTIAL_YELLOW, zorder=1)
    ax.axhspan(0, 25, alpha=0.10, color=NON_RESPONDER_RED, zorder=1)

    # Zone labels (right side)
    ax.text(
        sessions + 0.6, 75, "Responder\n(\u226550% improvement)",
        ha="left", va="center", fontsize=8, fontweight="bold",
        color=RESPONDER_GREEN, alpha=0.85,
    )
    ax.text(
        sessions + 0.6, 37.5, "Partial Responder\n(25-50%)",
        ha="left", va="center", fontsize=8, fontweight="bold",
        color=PARTIAL_YELLOW, alpha=0.85,
    )
    ax.text(
        sessions + 0.6, 12.5, "Non-Responder\n(<25%)",
        ha="left", va="center", fontsize=8, fontweight="bold",
        color=NON_RESPONDER_RED, alpha=0.85,
    )

    # Threshold dashed lines
    ax.axhline(
        50, color=RESPONDER_GREEN, linewidth=1.2, linestyle="--",
        alpha=0.7, zorder=2, label="Response threshold (50%)",
    )
    ax.axhline(
        25, color=PARTIAL_YELLOW, linewidth=1.2, linestyle="--",
        alpha=0.7, zorder=2, label="Partial response threshold (25%)",
    )

    # Week assessment vertical lines
    # Weeks 1-4 = sessions 1-4, Weeks 5-8 = sessions 5-8, Weeks 9-12 = sessions 9-12
    week4_session = 4
    week8_session = 8

    ax.axvline(
        week4_session + 0.5, color=SOZO_BLUE, linewidth=1.0,
        linestyle=":", alpha=0.6, zorder=2,
    )
    ax.axvline(
        week8_session + 0.5, color=SOZO_BLUE, linewidth=1.0,
        linestyle=":", alpha=0.6, zorder=2,
    )

    # Decision point annotations
    ax.annotate(
        "Week 4:\nContinue / Adjust?",
        xy=(week4_session + 0.5, 95),
        ha="center", va="top",
        fontsize=8, fontweight="bold", color=SOZO_DARK_BLUE,
        bbox=dict(
            boxstyle="round,pad=0.3", facecolor="#BDD7EE",
            edgecolor=SOZO_BLUE, alpha=0.85,
        ),
        zorder=5,
    )
    ax.annotate(
        "Week 8:\nResponder\nClassification",
        xy=(week8_session + 0.5, 95),
        ha="center", va="top",
        fontsize=8, fontweight="bold", color=SOZO_DARK_BLUE,
        bbox=dict(
            boxstyle="round,pad=0.3", facecolor="#BDD7EE",
            edgecolor=SOZO_BLUE, alpha=0.85,
        ),
        zorder=5,
    )

    # Week grouping brackets at the bottom
    week_groups = [
        (1, 4, "Week 1\u20134"),
        (5, 8, "Week 5\u20138"),
        (9, 12, "Week 9\u201312"),
    ]
    for start, end, label in week_groups:
        mid = (start + end) / 2
        ax.text(
            mid, -8, label,
            ha="center", va="top", fontsize=8.5,
            fontweight="bold", color=NAVY,
        )

    # Expected trajectory curve (light gray, dashed)
    x_traj = np.linspace(1, sessions, 100)
    # Logistic-like growth curve: starts slow, accelerates, plateaus
    y_traj = 65 * (1 - np.exp(-0.25 * x_traj))
    ax.plot(
        x_traj, y_traj, color="#CCCCCC", linewidth=2.0,
        linestyle="--", alpha=0.6, zorder=2,
        label="Expected trajectory (typical)",
    )

    # Session markers (empty circles for clinician to fill)
    session_x = np.arange(1, sessions + 1)
    ax.scatter(
        session_x, [None] * sessions,
        s=60, facecolors="none", edgecolors="#BBBBBB",
        linewidths=1.5, zorder=3,
    )
    # Small tick marks on x-axis for each session
    for s in session_x:
        ax.plot(s, 0, marker="|", color="#CCCCCC", markersize=8, zorder=3)

    # Axes
    ax.set_xlim(0.3, sessions + 3.5)
    ax.set_ylim(-12, 105)
    ax.set_xticks(range(1, sessions + 1))
    ax.set_xticklabels([str(i) for i in range(1, sessions + 1)], fontsize=9)
    ax.set_yticks(range(0, 101, 10))
    ax.tick_params(axis="both", labelsize=9, colors=NAVY)

    ax.set_xlabel("Session Number", fontsize=10, fontweight="bold", color=NAVY)
    ax.set_ylabel(
        f"% Improvement from Baseline\n({primary_outcome})",
        fontsize=10, fontweight="bold", color=NAVY,
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")

    # Light horizontal grid
    ax.yaxis.grid(True, color="#E8E8E8", linewidth=0.5, zorder=0)

    # Title and subtitle
    subtitle_parts = []
    if condition_name:
        subtitle_parts.append(f"Condition: {condition_name}")
    if primary_outcome != "Primary Outcome Score":
        subtitle_parts.append(f"Outcome Measure: {primary_outcome}")
    subtitle = "  |  ".join(subtitle_parts) if subtitle_parts else ""

    full_title = title
    if subtitle:
        full_title += f"\n{subtitle}"
    ax.set_title(full_title, fontsize=13, fontweight="bold", color=SOZO_DARK_BLUE, pad=15)

    # Legend
    legend = ax.legend(
        loc="lower right", fontsize=8, framealpha=0.9,
        edgecolor="#CCCCCC",
    )
    legend.get_frame().set_facecolor("white")

    # SOZO branding footer
    fig.text(
        0.98, 0.02, "SOZO Brain Center",
        ha="right", fontsize=7, color="#AABBCC", style="italic",
    )

    plt.tight_layout(pad=1.2)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    img_bytes = buf.read()

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(img_bytes)
        logger.info("Dose-response template saved: %s", output_path)

    return img_bytes


def generate_dose_response_for_condition(
    condition, output_dir: str | Path
) -> Optional[Path]:
    """
    Generate a condition-specific dose-response tracking template.

    Picks the condition's primary assessment tool as the outcome measure
    label on the Y axis.

    Parameters
    ----------
    condition : ConditionSchema
        The condition schema with assessment_tools.
    output_dir : str | Path
        Directory for the output PNG.

    Returns
    -------
    Optional[Path]
        Path to the generated PNG, or None on failure.
    """
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / f"{condition.slug}_dose_response.png"

        # Find the primary assessment tool
        primary_outcome = "Primary Outcome Score"
        assessment_tools = getattr(condition, "assessment_tools", [])

        if assessment_tools:
            # Prefer baseline tools; fallback to first tool
            baseline_tools = [
                t for t in assessment_tools
                if getattr(t, "timing", "") == "baseline"
            ]
            chosen = baseline_tools[0] if baseline_tools else assessment_tools[0]
            abbrev = getattr(chosen, "abbreviation", "")
            name = getattr(chosen, "name", "")
            primary_outcome = f"{abbrev} ({name})" if abbrev else name

        # Determine session count from protocols if available
        sessions = 12
        protocols = getattr(condition, "protocols", [])
        if protocols:
            counts = [
                getattr(p, "session_count", None) for p in protocols
                if getattr(p, "session_count", None)
            ]
            if counts:
                sessions = max(counts)

        generate_dose_response(
            title="Dose-Response Tracking Template",
            condition_name=condition.display_name,
            primary_outcome=primary_outcome,
            sessions=sessions,
            output_path=str(out_path),
        )

        logger.info("Condition dose-response generated: %s", out_path)
        return out_path

    except Exception as exc:
        logger.warning(
            "generate_dose_response_for_condition failed: %s", exc, exc_info=True
        )
        return None
