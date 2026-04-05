"""
Document Orchestrator — full pipeline coordinator for CanonicalDocument generation.

Pipeline: condition → blueprint → assets → sections → assembly → QA → export → provenance
"""
from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationResult:
    """Result of a document orchestration run."""
    success: bool
    condition_slug: str
    variant: str
    document_type: str
    document_id: Optional[str] = None
    output_paths: dict = field(default_factory=dict)  # {"docx": ..., "html": ..., "pdf": ..., "json": ...}
    qa_passed: bool = False
    qa_report_path: Optional[str] = None
    blueprint_path: Optional[str] = None
    provenance_path: Optional[str] = None
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    duration_seconds: float = 0.0
    sections_generated: int = 0
    assets_generated: int = 0

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "condition_slug": self.condition_slug,
            "variant": self.variant,
            "document_type": self.document_type,
            "document_id": self.document_id,
            "output_paths": self.output_paths,
            "qa_passed": self.qa_passed,
            "qa_report_path": self.qa_report_path,
            "blueprint_path": self.blueprint_path,
            "provenance_path": self.provenance_path,
            "errors": self.errors,
            "warnings": self.warnings,
            "duration_seconds": self.duration_seconds,
            "sections_generated": self.sections_generated,
            "assets_generated": self.assets_generated,
        }


class DocumentOrchestrator:
    """
    Full pipeline orchestrator for CanonicalDocument generation.

    Coordinates: blueprint building → asset registration → section generation
    → asset building → document assembly → QA → export → provenance.

    Designed to be:
    - Resumable: save/load CanonicalDocument JSON at any stage
    - Debuggable: each step logged, errors isolated
    - Partially rebuildable: regenerate section only, assets only, QA only, export only
    """

    def __init__(
        self,
        output_base_dir: str = "outputs",
        skip_assets: bool = False,
        skip_pdf: bool = True,
    ):
        self.output_base_dir = output_base_dir
        self.skip_assets = skip_assets
        self.skip_pdf = skip_pdf
        self._components: dict = {}

    def _get(self, name: str) -> Any:
        """Lazy-initialize pipeline components to avoid circular imports."""
        if name not in self._components:
            self._components[name] = self._init_component(name)
        return self._components[name]

    def _init_component(self, name: str) -> Any:  # noqa: PLR0911
        if name == "blueprint_builder":
            from sozo_generator.planning.document_blueprint_builder import DocumentBlueprintBuilder
            return DocumentBlueprintBuilder()
        if name == "asset_registry":
            from sozo_generator.services.asset_registry import AssetRegistry
            return AssetRegistry()
        if name == "section_generator":
            from sozo_generator.generation.section_generator import SectionGenerator
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            return SectionGenerator(
                asset_registry=self._get("asset_registry"),
                use_llm=bool(api_key),
                api_key=api_key or None,
            )
        if name == "table_builder":
            from sozo_generator.assets.table_builder import TableBuilder
            return TableBuilder()
        if name == "figure_builder":
            from sozo_generator.assets.figure_builder import FigureBuilder
            return FigureBuilder(output_dir=os.path.join(self.output_base_dir, "assets"))
        if name == "chart_builder":
            from sozo_generator.assets.chart_builder import ChartBuilder
            return ChartBuilder(output_dir=os.path.join(self.output_base_dir, "assets"))
        if name == "caption_builder":
            from sozo_generator.assets.caption_builder import CaptionBuilder
            return CaptionBuilder()
        if name == "assembler":
            from sozo_generator.assembly.document_assembler import DocumentAssembler
            return DocumentAssembler(asset_registry=self._get("asset_registry"))
        if name == "qa_runner":
            from sozo_generator.qa.validators.document_qa_runner import DocumentQARunner
            return DocumentQARunner()
        if name == "docx_exporter":
            from sozo_generator.export.docx_exporter import CanonicalDocxExporter
            return CanonicalDocxExporter(
                output_dir=os.path.join(self.output_base_dir, "documents")
            )
        if name == "html_exporter":
            from sozo_generator.export.html_preview_exporter import HTMLPreviewExporter
            return HTMLPreviewExporter(
                output_dir=os.path.join(self.output_base_dir, "documents")
            )
        raise ValueError(f"Unknown component: {name}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        condition_slug: str,
        variant: str,
        document_type: str = "handbook",
        target_page_count: int = 60,
        output_dir: Optional[str] = None,
    ) -> OrchestrationResult:
        """Full pipeline: condition → exported document."""
        start = time.time()
        out_dir = output_dir or self._output_dir_for(condition_slug, variant, document_type)
        os.makedirs(out_dir, exist_ok=True)

        result = OrchestrationResult(
            success=False,
            condition_slug=condition_slug,
            variant=variant,
            document_type=document_type,
        )

        # Step 1 — load condition
        condition = self._load_condition(condition_slug, result)

        # Step 2 — build blueprint
        try:
            blueprint = self._get("blueprint_builder").build(
                condition_slug=condition_slug,
                variant=variant,
                document_type=document_type,
                target_page_count=target_page_count,
            )
            blueprint_path = self._get("blueprint_builder").save(blueprint, out_dir)
            result.blueprint_path = blueprint_path
            logger.info("Blueprint built: %d sections", len(blueprint.sections))
        except Exception as exc:
            result.errors.append(f"Blueprint build failed: {exc}")
            logger.error("Blueprint build failed: %s", exc)
            result.duration_seconds = time.time() - start
            return result

        # Step 3 — register assets
        try:
            self._register_assets_for_blueprint(blueprint, condition)
        except Exception as exc:
            result.warnings.append(f"Asset registration error: {exc}")
            logger.warning("Asset registration error: %s", exc)

        # Step 4 — generate sections
        sections = []
        for spec in blueprint.sections:
            try:
                section = self._get("section_generator").generate_section(
                    spec, condition, variant
                )
                sections.append(section)
            except Exception as exc:
                result.warnings.append(f"Section '{spec.title}' failed: {exc}")
                logger.warning("Section '%s' failed: %s", spec.title, exc)
        result.sections_generated = len(sections)

        # Step 5 — build assets
        if not self.skip_assets:
            try:
                self._build_assets(condition, variant)
                result.assets_generated = len(
                    self._get("asset_registry").get_by_status("generated")
                )
            except Exception as exc:
                result.warnings.append(f"Asset build error: {exc}")
                logger.warning("Asset build error: %s", exc)

        # Step 6 — assemble
        try:
            from sozo_generator.schemas.canonical import CanonicalCitation
            refs: list[CanonicalCitation] = []
            if condition and hasattr(condition, "references"):
                for r in (condition.references or []):
                    try:
                        refs.append(CanonicalCitation(
                            pmid=r.get("pmid"),
                            title=r.get("title", ""),
                            authors_short=r.get("authors_short", r.get("authors", "")),
                            year=r.get("year"),
                            journal=r.get("journal"),
                        ))
                    except Exception:
                        pass

            document = self._get("assembler").assemble(
                blueprint=blueprint,
                sections=sections,
                condition=condition,
                references=refs or None,
            )
            result.document_id = document.document_id
        except Exception as exc:
            result.errors.append(f"Assembly failed: {exc}")
            logger.error("Assembly failed: %s", exc, exc_info=True)
            result.duration_seconds = time.time() - start
            return result

        # Step 7 — QA
        try:
            qa_report = self._get("qa_runner").run(document)
            result.qa_passed = qa_report.overall_passed
            qa_path = self._get("qa_runner").save_report(qa_report, out_dir)
            result.qa_report_path = qa_path
        except Exception as exc:
            result.warnings.append(f"QA failed: {exc}")
            logger.warning("QA failed: %s", exc)

        # Step 8 — save canonical JSON
        try:
            json_path = self._save_canonical_document(document, out_dir)
            result.output_paths["json"] = json_path
        except Exception as exc:
            result.warnings.append(f"JSON save failed: {exc}")

        # Step 9 — export DOCX
        try:
            docx_path = self._get("docx_exporter").export(document)
            result.output_paths["docx"] = docx_path
        except Exception as exc:
            result.warnings.append(f"DOCX export failed: {exc}")
            logger.warning("DOCX export failed: %s", exc)

        # Step 10 — export HTML
        try:
            html_path = self._get("html_exporter").export(document)
            result.output_paths["html"] = html_path
        except Exception as exc:
            result.warnings.append(f"HTML export failed: {exc}")
            logger.warning("HTML export failed: %s", exc)

        # Step 11 — PDF (optional)
        if not self.skip_pdf:
            try:
                from sozo_generator.export.pdf_export_bridge import PDFExportBridge
                bridge = PDFExportBridge(self._get("docx_exporter"))
                pdf_path = bridge.export(document)
                if pdf_path:
                    result.output_paths["pdf"] = pdf_path
            except Exception as exc:
                result.warnings.append(f"PDF export failed: {exc}")

        # Step 12 — save result metadata
        result.success = True
        result.duration_seconds = time.time() - start
        self._save_result_metadata(result, out_dir)
        return result

    def generate_section_only(
        self,
        condition_slug: str,
        variant: str,
        section_id: str,
        blueprint: Any,
    ) -> Any:
        """Regenerate a single section by section_id using an existing blueprint."""
        condition = self._load_condition(condition_slug, None)
        spec = next((s for s in blueprint.sections if s.section_id == section_id), None)
        if spec is None:
            raise ValueError(f"Section {section_id} not found in blueprint")
        return self._get("section_generator").generate_section(spec, condition, variant)

    def rebuild_assets_only(
        self,
        condition_slug: str,
        variant: str,
        document_type: str,
    ) -> dict:
        """Rebuild all assets without regenerating text."""
        condition = self._load_condition(condition_slug, None)
        blueprint = self._get("blueprint_builder").build(condition_slug, variant, document_type)
        self._register_assets_for_blueprint(blueprint, condition)
        self._build_assets(condition, variant)
        return self._get("asset_registry").summary()

    def reassemble(self, canonical_doc_path: str) -> OrchestrationResult:
        """Load a CanonicalDocument JSON and re-run assembly + export without regenerating."""
        document = self._load_canonical_document(canonical_doc_path)
        out_dir = os.path.dirname(os.path.abspath(canonical_doc_path))
        result = OrchestrationResult(
            success=False,
            condition_slug=document.condition_slug,
            variant=document.variant,
            document_type=document.document_type,
            document_id=document.document_id,
        )
        try:
            docx_path = self._get("docx_exporter").export(document)
            result.output_paths["docx"] = docx_path
        except Exception as exc:
            result.warnings.append(f"DOCX export failed: {exc}")
            logger.warning("DOCX export failed during reassemble: %s", exc)

        try:
            html_path = self._get("html_exporter").export(document)
            result.output_paths["html"] = html_path
        except Exception as exc:
            result.warnings.append(f"HTML export failed: {exc}")
            logger.warning("HTML export failed during reassemble: %s", exc)

        result.success = True
        return result

    def qa_only(self, canonical_doc_path: str) -> OrchestrationResult:
        """Load a CanonicalDocument JSON and run QA only."""
        document = self._load_canonical_document(canonical_doc_path)
        result = OrchestrationResult(
            success=False,
            condition_slug=document.condition_slug,
            variant=document.variant,
            document_type=document.document_type,
            document_id=document.document_id,
        )
        try:
            qa_report = self._get("qa_runner").run(document)
            result.qa_passed = qa_report.overall_passed
            out_dir = os.path.dirname(canonical_doc_path)
            result.qa_report_path = self._get("qa_runner").save_report(qa_report, out_dir)
            result.success = True
        except Exception as exc:
            result.errors.append(str(exc))
        return result

    def export_only(
        self,
        canonical_doc_path: str,
        formats: Optional[list] = None,
    ) -> OrchestrationResult:
        """Load a CanonicalDocument JSON and export in specified formats."""
        formats = formats or ["docx", "html"]
        document = self._load_canonical_document(canonical_doc_path)
        result = OrchestrationResult(
            success=False,
            condition_slug=document.condition_slug,
            variant=document.variant,
            document_type=document.document_type,
            document_id=document.document_id,
        )
        if "docx" in formats:
            try:
                result.output_paths["docx"] = self._get("docx_exporter").export(document)
            except Exception as exc:
                result.errors.append(f"DOCX: {exc}")
        if "html" in formats:
            try:
                result.output_paths["html"] = self._get("html_exporter").export(document)
            except Exception as exc:
                result.errors.append(f"HTML: {exc}")
        if "pdf" in formats:
            try:
                from sozo_generator.export.pdf_export_bridge import PDFExportBridge
                path = PDFExportBridge(self._get("docx_exporter")).export(document)
                if path:
                    result.output_paths["pdf"] = path
            except Exception as exc:
                result.errors.append(f"PDF: {exc}")
        result.success = not result.errors
        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_condition(self, condition_slug: str, result: Optional[OrchestrationResult]) -> Any:
        try:
            from sozo_generator.conditions.registry import get_registry
            return get_registry().get(condition_slug)
        except Exception as exc:
            msg = f"Could not load condition '{condition_slug}': {exc}"
            logger.warning(msg)
            if result:
                result.warnings.append(msg)
            return None

    def _register_assets_for_blueprint(self, blueprint: Any, condition: Any) -> None:
        registry = self._get("asset_registry")
        condition_slug = blueprint.condition_slug
        for spec in blueprint.sections:
            for block in spec.blocks:
                if block.block_type in ("table", "figure", "chart", "image", "diagram"):
                    asset_id = block.asset_id
                    renderer = f"{block.block_type}_builder"
                    source: dict = {}
                    if block.block_type == "table" and condition:
                        source = {
                            "table_type": "protocol_parameters",
                            "condition_slug": condition_slug,
                        }
                    try:
                        existing = registry.get(asset_id) if asset_id else None
                        if existing is None:
                            rec = registry.register(
                                asset_type=block.block_type,
                                condition_slug=condition_slug,
                                section_target=spec.section_id,
                                renderer_type=renderer,
                                source_data=source,
                                asset_id=asset_id,
                                variant_tags=block.variant_tags,
                            )
                            # Keep the same ID if block already had one
                            if asset_id and rec.asset_id != asset_id:
                                registry._records[asset_id] = rec
                    except Exception as exc:
                        logger.warning("Asset register error for %s: %s", asset_id, exc)

    def _build_assets(self, condition: Any, variant: str) -> None:
        registry = self._get("asset_registry")
        table_builder = self._get("table_builder")
        condition_slug = condition.slug if condition else "unknown"

        for record in registry.get_pending_assets():
            try:
                if record.asset_type == "table":
                    table = table_builder.build_protocol_parameters_table(condition) if condition else None
                    if table:
                        registry.update_status(
                            record.asset_id,
                            "generated",
                            output_path=None,
                        )
                        # Store table data in source_data for DOCX renderer
                        record.source_data = {
                            "headers": table.headers,
                            "rows": table.rows,
                            "title": table.title,
                            "landscape": table.landscape,
                        }
                    else:
                        registry.update_status(record.asset_id, "failed", error_message="No condition data")
                else:
                    # Figures/charts: mark as pending — FigureBuilder delegates to visuals
                    # which may not be available in all environments
                    registry.update_status(record.asset_id, "failed", error_message="Renderer not invoked")
            except Exception as exc:
                registry.update_status(record.asset_id, "failed", error_message=str(exc))
                logger.warning("Asset build failed [%s]: %s", record.asset_id, exc)

    def _save_canonical_document(self, document: Any, output_dir: str) -> str:
        os.makedirs(output_dir, exist_ok=True)
        filename = f"canonical_{document.document_type}_{document.variant}_{document.document_id[:8]}.json"
        path = os.path.join(output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(document.model_dump(mode="json"), f, indent=2, ensure_ascii=False)
        return path

    def _load_canonical_document(self, path: str) -> Any:
        from sozo_generator.schemas.canonical import CanonicalDocument
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return CanonicalDocument.model_validate(data)

    def _save_result_metadata(self, result: OrchestrationResult, output_dir: str) -> None:
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, "orchestration_result.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2)
        result.provenance_path = path

    def _output_dir_for(self, condition_slug: str, variant: str, document_type: str) -> str:
        return os.path.join(
            self.output_base_dir, "documents", condition_slug, variant, "canonical"
        )
