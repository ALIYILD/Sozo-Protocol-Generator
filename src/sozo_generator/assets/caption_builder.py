"""Caption generators for tables, figures, charts, and images.

CaptionBuilder produces human-readable captions suitable for clinical DOCX
documents.  Charts are treated as figures for numbering purposes (a standard
academic convention).
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from sozo_generator.schemas.canonical import (
    AssetRecord,
    CanonicalChart,
    CanonicalFigure,
    CanonicalTable,
)


class CaptionBuilder:
    """Generates captions for tables, figures, charts, and images."""

    # ------------------------------------------------------------------
    # Table captions
    # ------------------------------------------------------------------

    def build_table_caption(
        self,
        table: CanonicalTable,
        numbering_label: str,
        condition_name: Optional[str] = None,
    ) -> str:
        """Build a caption for a CanonicalTable.

        Format:  "Table 3. Protocol Parameters for {condition_name}. {footer}"
        If condition_name is not provided the table title is used verbatim.
        """
        title = table.title or "Untitled Table"

        # If condition_name is given and the title does not already reference it,
        # append a "for {condition_name}" qualifier.
        if condition_name and condition_name.lower() not in title.lower():
            display_title = f"{title} for {condition_name}"
        else:
            display_title = title

        caption = f"{numbering_label}. {display_title}."

        if table.footer:
            footer = table.footer.strip().rstrip(".")
            caption = f"{caption} {footer}."

        return caption

    # ------------------------------------------------------------------
    # Figure captions
    # ------------------------------------------------------------------

    def build_figure_caption(
        self,
        figure: CanonicalFigure,
        numbering_label: str,
        condition_name: Optional[str] = None,
    ) -> str:
        """Build a caption for a CanonicalFigure.

        Format:  "Figure 7. {figure.title}. {alt_text if substantive}"
        """
        title = figure.title or "Untitled Figure"

        if condition_name and condition_name.lower() not in title.lower():
            display_title = f"{title} for {condition_name}"
        else:
            display_title = title

        caption = f"{numbering_label}. {display_title}."

        # Include alt_text only when it adds information (not just "Image: ...")
        alt = (figure.alt_text or "").strip()
        if alt and not alt.lower().startswith("image:"):
            alt_clean = alt.rstrip(".")
            caption = f"{caption} {alt_clean}."

        return caption

    # ------------------------------------------------------------------
    # Chart captions
    # ------------------------------------------------------------------

    def build_chart_caption(
        self,
        chart: CanonicalChart,
        numbering_label: str,
        condition_name: Optional[str] = None,
    ) -> str:
        """Build a caption for a CanonicalChart (charts count as figures).

        Format:  "Figure 4. {chart.title}. [x_label vs y_label note]"
        """
        title = chart.title or "Untitled Chart"

        if condition_name and condition_name.lower() not in title.lower():
            display_title = f"{title} for {condition_name}"
        else:
            display_title = title

        caption = f"{numbering_label}. {display_title}."

        # Append axis description when both labels are present
        if chart.x_label and chart.y_label:
            caption = f"{caption} {chart.x_label} vs. {chart.y_label}."
        elif chart.y_label:
            caption = f"{caption} {chart.y_label}."

        return caption

    # ------------------------------------------------------------------
    # Generic asset caption dispatcher
    # ------------------------------------------------------------------

    def build_asset_caption(
        self,
        asset_record: AssetRecord,
        numbering_label: str,
        condition_name: Optional[str] = None,
    ) -> str:
        """Dispatch to the appropriate caption builder based on asset_record.asset_type.

        If asset_record.caption is already set, it is returned with
        numbering_label prepended (unless the label is already present).
        """
        # Honour a pre-set caption
        if asset_record.caption:
            existing = asset_record.caption.strip()
            if existing.startswith(numbering_label):
                return existing
            return f"{numbering_label}. {existing}"

        asset_type = asset_record.asset_type
        condition_name = condition_name or asset_record.condition_slug

        # Build a minimal stand-in object from source_data so the typed
        # builders can be reused without requiring fully-built assets.
        if asset_type == "table":
            title = (
                asset_record.source_data.get("title")
                or asset_record.source_data.get("table_type", "Table")
            )
            footer = asset_record.source_data.get("footer", None)
            proxy = CanonicalTable(title=title, footer=footer)
            return self.build_table_caption(proxy, numbering_label, condition_name)

        if asset_type in ("figure", "topomap", "montage", "diagram", "flowchart"):
            title = asset_record.source_data.get("title") or asset_record.renderer_type or "Figure"
            alt_text = asset_record.source_data.get("alt_text", "")
            proxy = CanonicalFigure(title=title, alt_text=alt_text)
            return self.build_figure_caption(proxy, numbering_label, condition_name)

        if asset_type == "chart":
            title = asset_record.source_data.get("title") or "Chart"
            x_label = asset_record.source_data.get("x_label", "")
            y_label = asset_record.source_data.get("y_label", "")
            proxy = CanonicalChart(
                title=title,
                chart_type=asset_record.source_data.get("chart_type", "bar"),
                x_label=x_label,
                y_label=y_label,
            )
            return self.build_chart_caption(proxy, numbering_label, condition_name)

        if asset_type in ("image", "timeline"):
            title = asset_record.source_data.get("title") or asset_record.asset_type.title()
            alt_text = asset_record.source_data.get("alt_text", "")
            proxy = CanonicalFigure(title=title, alt_text=alt_text)
            return self.build_figure_caption(proxy, numbering_label, condition_name)

        # Fallback: generic label
        title = (
            asset_record.source_data.get("title")
            or f"{asset_type.title()} — {condition_name}"
        )
        return f"{numbering_label}. {title}."

    # ------------------------------------------------------------------
    # Short caption for TOC / list-of-figures
    # ------------------------------------------------------------------

    def short_caption(self, full_caption: str, max_words: int = 12) -> str:
        """Truncate full_caption to max_words for TOC or list-of-tables/figures.

        Always includes the numbering label (e.g. "Table 3." or "Figure 7.")
        in the returned string.
        """
        words = full_caption.split()
        if len(words) <= max_words:
            return full_caption

        truncated = " ".join(words[:max_words])
        # Remove trailing punctuation before ellipsis
        truncated = truncated.rstrip(".,;:")
        return f"{truncated}…"
