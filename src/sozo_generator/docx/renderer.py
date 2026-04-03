"""
Main document renderer — assembles complete .docx documents from DocumentSpec.
"""
import logging
from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor
from ..schemas.documents import DocumentSpec
from ..schemas.branding import BrandingConfig
from ..core.enums import Tier
from ..core.utils import ensure_dir, current_month_year
from .styles import COLOR_DARK_BLUE, COLOR_ACCENT_RED, FONT_HEADING, FONT_BODY, apply_heading_style
from .layout import configure_page_layout, add_title_block
from .headers import add_header, add_footer
from .sections import render_section
from .tables import add_clinical_table, add_warning_box
from .images import insert_figure_placeholder

logger = logging.getLogger(__name__)


class DocumentRenderer:
    """Renders DocumentSpec objects to .docx files."""

    def __init__(
        self,
        output_dir: str = "outputs/documents/",
        branding: BrandingConfig = None,
    ):
        self.output_dir = Path(output_dir)
        ensure_dir(self.output_dir)
        self.branding = branding or BrandingConfig()

    def render(self, spec: DocumentSpec, output_path=None, image_manifest=None) -> Path:
        """
        Render a DocumentSpec to a .docx file. Returns output path.
        output_path is optional — if omitted, a path is built from spec fields.
        image_manifest: optional DocumentImageManifest for inline image insertion.
        """
        doc = Document()
        configure_page_layout(doc)

        # Determine tier labels
        tier = spec.tier
        if tier == Tier.FELLOW or (hasattr(tier, "value") and tier.value == "fellow"):
            tier_label = self.branding.fellow_tier_label
            tier_desc = self.branding.fellow_tier_description
        else:
            tier_label = self.branding.partners_tier_label
            tier_desc = self.branding.partners_tier_description

        version_str = f"Version {spec.version}"

        # Header + footer
        add_header(
            doc,
            condition_name=spec.condition_name,
            tier_label=tier_label,
            version=version_str,
            confidentiality=spec.confidentiality_mark,
            document_title=spec.title,
        )
        add_footer(doc, condition_name=spec.condition_name, organization=self.branding.organization)

        # Title block
        add_title_block(
            doc,
            title=spec.title,
            subtitle=spec.subtitle or "",
            condition_name=spec.condition_name,
            tier_label=tier_label,
            tier_description=tier_desc,
            version=version_str,
            date_label=spec.date_label or current_month_year(),
            confidentiality=spec.confidentiality_mark,
        )

        # Render sections (with optional inline images)
        for section in spec.sections:
            render_section(doc, section, level=1, image_manifest=image_manifest)

        # Top-level figures list
        if spec.figures:
            fig_heading = doc.add_paragraph()
            run = fig_heading.add_run("Figures")
            apply_heading_style(fig_heading, level=1)
            for fig_path in spec.figures:
                insert_figure_placeholder(doc, fig_path)

        # References section
        if spec.references:
            self._render_references(doc, spec.references)

        # Review flags summary
        if spec.review_flags:
            self._render_review_summary(doc, spec.review_flags)

            logger.warning(
                f"Document '{spec.title}' has {len(spec.review_flags)} review flags"
            )

        # Clinical Decision Support Disclaimer
        self._render_disclaimer(doc)

        # Provenance footer
        self._render_provenance_block(doc, spec)

        # Save
        if output_path is not None:
            out_path = Path(output_path)
        else:
            out_path = self._build_output_path(spec)

        ensure_dir(out_path.parent)
        doc.save(str(out_path))
        logger.info(f"Saved: {out_path}")
        return out_path

    def _render_references(self, doc: Document, references: list) -> None:
        """Add references section."""
        p = doc.add_paragraph()
        run = p.add_run("References & Evidence Sources")
        run.bold = True
        run.font.size = Pt(12)
        run.font.color.rgb = COLOR_DARK_BLUE
        run.font.name = FONT_HEADING

        for i, ref in enumerate(references, 1):
            authors = ref.get("authors", "")
            year = ref.get("year", "n.d.")
            title = ref.get("title", "[Title not available]")
            journal = ref.get("journal", "")
            pmid = ref.get("pmid", "")
            doi = ref.get("doi", "")

            p_ref = doc.add_paragraph()
            p_ref.paragraph_format.left_indent = Pt(24)
            p_ref.paragraph_format.first_line_indent = Pt(-18)
            text = f"{i}. {authors} ({year}). {title}."
            if journal:
                text += f" {journal}."
            if pmid and not str(pmid).startswith("placeholder"):
                text += f" PMID: {pmid}."
            elif pmid and str(pmid).startswith("placeholder"):
                text += f" [PMID REVIEW REQUIRED]"
            if doi:
                text += f" DOI: {doi}."

            run = p_ref.add_run(text)
            run.font.size = Pt(9)
            run.font.name = FONT_BODY
            notes = ref.get("notes", "")
            if notes and "\u26a0" in str(notes):
                run.font.color.rgb = COLOR_ACCENT_RED

    def _render_review_summary(self, doc: Document, flags: list) -> None:
        """Add a review flags summary appendix."""
        doc.add_page_break()
        p = doc.add_paragraph()
        run = p.add_run("\u26a0 DOCUMENT REVIEW FLAGS \u2014 Action Required")
        run.bold = True
        run.font.size = Pt(13)
        run.font.color.rgb = COLOR_ACCENT_RED
        run.font.name = FONT_HEADING

        for flag in flags:
            p_flag = doc.add_paragraph()
            try:
                p_flag.style = "List Bullet"
            except Exception:
                pass
            run_flag = p_flag.add_run(flag)
            run_flag.font.size = Pt(10)
            run_flag.font.color.rgb = COLOR_ACCENT_RED
            run_flag.font.name = FONT_BODY

    def _render_disclaimer(self, doc: Document) -> None:
        """Add Clinical Decision Support disclaimer."""
        doc.add_page_break()
        p = doc.add_paragraph()
        run = p.add_run("Clinical Decision Support Disclaimer")
        run.bold = True
        run.font.size = Pt(11)
        run.font.name = FONT_HEADING

        disclaimer_text = (
            "This document was generated by the SOZO Protocol Generator, a clinical "
            "decision support system. It is intended to assist qualified healthcare "
            "professionals in developing evidence-based neuromodulation protocols. "
            "This document does NOT constitute medical advice, autonomous prescribing, "
            "or a substitute for clinical judgment. All recommendations must be "
            "independently reviewed, verified, and approved by a qualified clinician "
            "before clinical application. The treating clinician retains full "
            "responsibility for patient care decisions."
        )
        p_disc = doc.add_paragraph()
        run = p_disc.add_run(disclaimer_text)
        run.font.size = Pt(9)
        run.font.name = FONT_BODY
        run.italic = True

    def _render_provenance_block(self, doc: Document, spec: DocumentSpec) -> None:
        """Add provenance/build metadata footer."""
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(24)
        meta_parts = [
            f"Build ID: {spec.build_id}" if hasattr(spec, 'build_id') and spec.build_id else None,
            f"Condition: {spec.condition_slug}",
            f"Tier: {spec.tier.value}",
            f"Document Type: {spec.document_type.value}",
        ]
        meta_text = " | ".join(part for part in meta_parts if part)
        run = p.add_run(meta_text)
        run.font.size = Pt(8)
        run.font.name = FONT_BODY
        run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    def _build_output_path(self, spec: DocumentSpec) -> Path:
        """Build the output file path from spec."""
        if spec.output_filename:
            # Place in output_dir/condition_slug/tier/
            return (
                self.output_dir
                / spec.condition_slug
                / spec.tier.value
                / spec.output_filename
            )
        # Build from document type
        doc_type_slug = spec.document_type.value.replace("_", "-")
        filename = f"{spec.condition_slug}_{doc_type_slug}_{spec.tier.value}.docx"
        return self.output_dir / spec.condition_slug / spec.tier.value / filename
