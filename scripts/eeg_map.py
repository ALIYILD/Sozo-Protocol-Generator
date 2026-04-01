"""EEG scalp map image generator — matches PD template visual style exactly."""
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# ── Colours matching PD template ────────────────────────────────────────────
NAVY      = "#0D2137"
TEAL      = "#1A7A8A"
HEAD_FILL = "#E8F4F6"
DOT_GRAY  = "#B0BEC5"
RED_ANODE = "#C0392B"
BLUE_CAT  = "#2E6DA4"
ORANGE_TPS= "#E07B39"
WHITE     = "#FFFFFF"

# ── EEG 10-20 positions (x,y normalised: 0,0=centre, 1.0=head radius) ──────
EEG_POS = {
    "Fp1": (-0.31, 0.91), "Fpz": (0.0, 0.95), "Fp2": (0.31, 0.91),
    "AF7": (-0.64, 0.75), "AF3": (-0.33, 0.81), "AFz": (0.0, 0.84),
    "AF4": (0.33, 0.81),  "AF8": (0.64, 0.75),
    "F7":  (-0.80, 0.53), "F5":  (-0.62, 0.64), "F3": (-0.42, 0.75),
    "F1":  (-0.20, 0.82), "Fz":  (0.0,  0.86),  "F2": (0.20, 0.82),
    "F4":  (0.42,  0.75), "F6":  (0.62, 0.64),  "F8": (0.80, 0.53),
    "FT7": (-0.91, 0.27), "FC5": (-0.73, 0.42), "FC3": (-0.51, 0.58),
    "FC1": (-0.25, 0.72), "FCz": (0.0,  0.77),  "FC2": (0.25, 0.72),
    "FC4": (0.51,  0.58), "FC6": (0.73, 0.42),  "FT8": (0.91, 0.27),
    "T3":  (-1.0,  0.0),  "C5":  (-0.78, 0.0),  "C3":  (-0.56, 0.0),
    "C1":  (-0.27, 0.0),  "Cz":  (0.0,  0.0),   "C2":  (0.27, 0.0),
    "C4":  (0.56,  0.0),  "C6":  (0.78, 0.0),   "T4":  (1.0,  0.0),
    "TP7": (-0.91,-0.27), "CP5": (-0.73,-0.42), "CP3": (-0.51,-0.58),
    "CP1": (-0.25,-0.72), "CPz": (0.0, -0.77),  "CP2": (0.25,-0.72),
    "CP4": (0.51, -0.58), "CP6": (0.73,-0.42),  "TP8": (0.91,-0.27),
    "T5":  (-0.80,-0.53), "P5":  (-0.62,-0.64), "P3":  (-0.42,-0.75),
    "P1":  (-0.20,-0.82), "Pz":  (0.0, -0.86),  "P2":  (0.20,-0.82),
    "P4":  (0.42, -0.75), "P6":  (0.62,-0.64),  "T6":  (0.80,-0.53),
    "PO7": (-0.56,-0.78), "PO3": (-0.31,-0.87), "POz": (0.0, -0.91),
    "PO4": (0.31, -0.87), "PO8": (0.56,-0.78),
    "O1":  (-0.31,-0.94), "Oz":  (0.0, -0.96),  "O2":  (0.31,-0.94),
    "Cb1": (-0.20,-1.04), "Cbz": (0.0, -1.07),  "Cb2": (0.20,-1.04),
}

# Positions shown with text label on the image (matches template)
LABELLED = {
    "Fp1","Fpz","Fp2","AFz","F7","F5","F3","F2","F4","F8",
    "FT7","FC5","FC3","FCz","FC4","FC6","FT8",
    "T3","C5","C3","Cz","C4","C6","T4",
    "TP7","CP5","CP3","CPz","CP4","CP6","TP8",
    "T5","P5","P3","Pz","P4","P6","T6",
    "PO7","POz","PO8","O1","Oz","O2",
    "Cb1","Cbz","Cb2",
}

# Ear pad positions
EAR_LEFT  = (-1.0, 0.0)
EAR_RIGHT = ( 1.0, 0.0)


def generate_eeg_map(
    title: str,
    subtitle: str,
    params_text: str,
    anodes: list[str] = None,
    cathodes: list[str] = None,
    tps_targets: list[str] = None,
    output_path: str | Path = None,
    figsize: tuple = (3.5, 4.8),
    dpi: int = 150,
    show_tps_legend: bool = False,
) -> bytes:
    """
    Generate an EEG scalp map image matching the SOZO PD template style.

    Args:
        title:       Bold protocol code e.g. "C1"
        subtitle:    Protocol name e.g. "Motor (Bradykinesia & Rigidity)"
        params_text: Bottom line e.g. "2 mA · 20 min | Bilateral M1"
        anodes:      List of EEG position names for anode (red)
        cathodes:    List of EEG position names for cathode (blue)
        tps_targets: List of EEG position names for TPS ROI (orange)
        output_path: Optional file path to save PNG
        figsize:     Matplotlib figure size (inches)
        dpi:         Resolution
        show_tps_legend: Include TPS Target in legend

    Returns:
        PNG bytes
    """
    anodes      = anodes      or []
    cathodes    = cathodes    or []
    tps_targets = tps_targets or []

    fig, ax = plt.subplots(figsize=figsize, facecolor="white")
    ax.set_aspect("equal")
    ax.axis("off")

    # ── Title ─────────────────────────────────────────────────────────────
    ax.text(0.5, 0.97, title, transform=ax.transAxes,
            ha="center", va="top", fontsize=11, fontweight="bold",
            color=TEAL, fontfamily="DejaVu Sans")
    ax.text(0.5, 0.92, subtitle, transform=ax.transAxes,
            ha="center", va="top", fontsize=8.5, fontweight="bold",
            color=NAVY, fontfamily="DejaVu Sans")

    # ── Drawing area ──────────────────────────────────────────────────────
    # Centre of head in data coords
    cx, cy = 0.5, 0.47
    r  = 0.30  # head radius in axes fraction

    def to_ax(nx, ny):
        """Convert normalised EEG coords to axes fraction."""
        return cx + nx * r, cy + ny * r

    # Head circle
    head = plt.Circle((cx, cy), r, color=HEAD_FILL, zorder=1,
                       transform=ax.transAxes)
    head_ring = plt.Circle((cx, cy), r, color=NAVY, fill=False,
                            linewidth=2.2, zorder=3, transform=ax.transAxes)
    ax.add_patch(head)
    ax.add_patch(head_ring)

    # Nose triangle
    nose_w, nose_h = 0.025, 0.038
    nose = mpatches.Polygon(
        [[cx - nose_w, cy + r - 0.005],
         [cx + nose_w, cy + r - 0.005],
         [cx, cy + r + nose_h]],
        closed=True, color=NAVY, zorder=4, transform=ax.transAxes
    )
    ax.add_patch(nose)

    # Ear pads (rectangles at T3/T4)
    for ex, ey in [EAR_LEFT, EAR_RIGHT]:
        axex, axey = to_ax(ex, ey)
        ear = mpatches.FancyBboxPatch(
            (axex - 0.022, axey - 0.038), 0.022, 0.076,
            boxstyle="round,pad=0.005",
            facecolor="#C8D5DE", edgecolor=NAVY,
            linewidth=1.2, zorder=2, transform=ax.transAxes
        )
        ax.add_patch(ear)

    # Crosshair dashed lines
    ax.plot([cx, cx], [cy - r, cy + r], color="#A0B4BF",
            lw=0.6, ls="--", zorder=2, transform=ax.transAxes)
    ax.plot([cx - r, cx + r], [cy, cy], color="#A0B4BF",
            lw=0.6, ls="--", zorder=2, transform=ax.transAxes)

    # ── EEG dots ─────────────────────────────────────────────────────────
    highlight = set(anodes) | set(cathodes) | set(tps_targets)
    ear_labels = {"T3", "T4"}

    for name, (nx, ny) in EEG_POS.items():
        if name in ear_labels:
            continue  # drawn as ear pads
        ax_x, ax_y = to_ax(nx, ny)

        if name in anodes:
            dot_color, edge_color, dot_r, z = RED_ANODE, WHITE, 0.022, 6
        elif name in cathodes:
            dot_color, edge_color, dot_r, z = BLUE_CAT, WHITE, 0.022, 6
        elif name in tps_targets:
            dot_color, edge_color, dot_r, z = ORANGE_TPS, WHITE, 0.022, 6
        else:
            dot_color, edge_color, dot_r, z = DOT_GRAY, DOT_GRAY, 0.008, 3

        dot = plt.Circle((ax_x, ax_y), dot_r, color=dot_color,
                          ec=edge_color, linewidth=0.8, zorder=z,
                          transform=ax.transAxes)
        ax.add_patch(dot)

        # Label for highlighted or key positions
        if name in highlight or name in LABELLED:
            offset_y = dot_r + 0.012
            fs = 5.5 if name in highlight else 5.0
            fw = "bold" if name in highlight else "normal"
            fc = NAVY if name in highlight else "#6B7B8D"
            ax.text(ax_x, ax_y - offset_y, name,
                    transform=ax.transAxes, ha="center", va="top",
                    fontsize=fs, fontweight=fw, color=fc, zorder=7)

    # ── Parameters text ───────────────────────────────────────────────────
    ax.text(0.5, 0.10, params_text, transform=ax.transAxes,
            ha="center", va="center", fontsize=7.0, color="#4A6070",
            style="italic", fontfamily="DejaVu Sans")

    # ── Legend ────────────────────────────────────────────────────────────
    legend_items = []
    if anodes:
        legend_items.append(mpatches.Patch(color=RED_ANODE, label="Anode (+)"))
    if cathodes:
        legend_items.append(mpatches.Patch(color=BLUE_CAT, label="Cathode (−)"))
    if tps_targets or show_tps_legend:
        legend_items.append(mpatches.Patch(color=ORANGE_TPS, label="TPS Target"))

    if legend_items:
        leg = ax.legend(
            handles=legend_items,
            loc="lower center",
            bbox_to_anchor=(0.5, 0.0),
            ncol=len(legend_items),
            fontsize=6.5,
            frameon=True,
            framealpha=0.9,
            edgecolor="#CCCCCC",
            handlelength=1.2,
            handleheight=0.8,
        )
        leg.get_frame().set_linewidth(0.6)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    plt.tight_layout(pad=0.3)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    buf.seek(0)
    img_bytes = buf.read()

    if output_path:
        Path(output_path).write_bytes(img_bytes)

    return img_bytes


# ── Quick test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    generate_eeg_map(
        title="C1",
        subtitle="Motor (Bradykinesia & Rigidity)",
        params_text="2 mA · 20 min | Bilateral M1 (C3 + C4)",
        anodes=["C3", "C4"],
        cathodes=["Fp1", "Fp2"],
        output_path="test_c1_motor.png",
    )
    generate_eeg_map(
        title="T1",
        subtitle="Bradykinesia & Rigidity",
        params_text="TPS: Bilateral M1 + SMA · 3,000–5,000 pulses",
        tps_targets=["C3", "C4", "FCz"],
        output_path="test_t1_motor.png",
        show_tps_legend=True,
    )
    print("Test images written.")
