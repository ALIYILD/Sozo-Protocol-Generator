"""
Unified Generation Service — the canonical entry point for all document generation.

This service orchestrates the full generation pipeline:
1. Resolve condition from registry
2. Validate tier/doc_type against document definitions
3. Optionally refresh evidence
4. Build document spec via DocumentExporter
5. Optionally generate visuals
6. Optionally run QA checks
7. Render DOCX
8. Store provenance metadata

Usage:
    from sozo_generator.generation.service import GenerationService

    service = GenerationService()

    # Generate one document
    result = service.generate(
        condition="parkinsons",
        tier="partners",
        doc_type="evidence_based_protocol",
    )

    # Generate all documents for a condition
    results = service.generate_all(condition="parkinsons", tier="both")

    # Generate everything
    results = service.generate_batch(conditions=None, tier="both")
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..conditions.registry import get_registry
from ..core.enums import DocumentType, Tier
from ..core.settings import get_settings
from ..schemas.condition import ConditionSchema
from ..schemas.definitions import (
    DocumentDefinition,
    GenerationRequest,
    get_document_definition,
)

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    """Result of generating one document."""

    condition_slug: str
    tier: str
    doc_type: str
    success: bool
    output_path: Optional[str] = None
    qa_passed: Optional[bool] = None
    qa_issues: list[str] = field(default_factory=list)
    visuals_generated: list[str] = field(default_factory=list)
    images_inserted: int = 0
    pdf_path: Optional[str] = None
    error: Optional[str] = None
    build_id: str = ""

    def __post_init__(self):
        if not self.build_id:
            self.build_id = f"build-{uuid.uuid4().hex[:8]}"


class GenerationService:
    """Canonical orchestrator for all document generation flows.

    Wraps DocumentExporter and adds evidence, QA, visuals, and provenance
    orchestration. All CLI commands and the Streamlit UI should route
    through this service.
    """

    def __init__(
        self,
        output_dir: Optional[str] = None,
        with_visuals: bool = True,
        with_qa: bool = True,
        with_images: bool = False,
        with_pdf: bool = False,
    ):
        settings = get_settings()
        self.output_dir = Path(output_dir) if output_dir else settings.output_dir / "documents"
        self.with_visuals = with_visuals
        self.with_qa = with_qa
        self.with_images = with_images
        self.with_pdf = with_pdf
        self._registry = None
        self._exporter = None
        self._image_curator = None

    @property
    def registry(self):
        if self._registry is None:
            self._registry = get_registry()
        return self._registry

    @property
    def exporter(self):
        if self._exporter is None:
            from ..docx.exporter import DocumentExporter
            self._exporter = DocumentExporter(
                output_dir=str(self.output_dir),
                with_visuals=self.with_visuals,
            )
        return self._exporter

    def generate(
        self,
        condition: str,
        tier: str = "both",
        doc_type: str = "all",
        with_visuals: Optional[bool] = None,
        with_qa: Optional[bool] = None,
        output_dir: Optional[str] = None,
    ) -> list[GenerationResult]:
        """Generate document(s) for a single condition.

        Args:
            condition: Condition slug (e.g. "parkinsons")
            tier: "fellow", "partners", or "both"
            doc_type: Document type value or "all"
            with_visuals: Override visual generation flag
            with_qa: Override QA flag
            output_dir: Override output directory

        Returns:
            List of GenerationResult objects (one per document generated)
        """
        # Resolve condition
        if not self.registry.exists(condition):
            return [GenerationResult(
                condition_slug=condition,
                tier=tier,
                doc_type=doc_type,
                success=False,
                error=f"Unknown condition: {condition}",
            )]

        schema = self.registry.get(condition)

        # Resolve tiers
        tier_enum = Tier(tier) if tier != "both" else Tier.BOTH
        tiers = [Tier.FELLOW, Tier.PARTNERS] if tier_enum == Tier.BOTH else [tier_enum]

        # Resolve doc types
        if doc_type == "all":
            doc_types = list(DocumentType)
        else:
            doc_types = [DocumentType(doc_type)]

        # Build requests
        requests = []
        for t in tiers:
            for dt in doc_types:
                # Skip network assessment for Fellow
                defn = get_document_definition(dt)
                if t not in defn.applicable_tiers:
                    continue
                requests.append(GenerationRequest(
                    condition_slug=condition,
                    tier=t,
                    doc_type=dt,
                    output_dir=output_dir,
                    with_visuals=with_visuals if with_visuals is not None else self.with_visuals,
                    with_qa=with_qa if with_qa is not None else self.with_qa,
                ))

        # Execute
        results = []
        for req in requests:
            result = self._execute_single(schema, req)
            results.append(result)

        return results

    def generate_all(
        self,
        condition: str,
        tier: str = "both",
    ) -> list[GenerationResult]:
        """Generate all document types for a condition."""
        return self.generate(condition=condition, tier=tier, doc_type="all")

    def generate_batch(
        self,
        conditions: Optional[list[str]] = None,
        tier: str = "both",
        doc_type: str = "all",
    ) -> list[GenerationResult]:
        """Generate documents for multiple conditions.

        Args:
            conditions: List of slugs, or None for all 15.
            tier: "fellow", "partners", or "both"
            doc_type: Document type or "all"
        """
        if conditions is None:
            conditions = self.registry.list_slugs()

        all_results = []
        for slug in conditions:
            logger.info(f"Generating {doc_type} for {slug} ({tier})")
            results = self.generate(condition=slug, tier=tier, doc_type=doc_type)
            all_results.extend(results)

        # Summary
        success = sum(1 for r in all_results if r.success)
        failed = sum(1 for r in all_results if not r.success)
        logger.info(
            f"Batch complete: {success} succeeded, {failed} failed, "
            f"{len(all_results)} total documents"
        )
        return all_results

    def _execute_single(
        self,
        schema: ConditionSchema,
        request: GenerationRequest,
    ) -> GenerationResult:
        """Execute a single generation request."""
        result = GenerationResult(
            condition_slug=request.condition_slug,
            tier=request.tier.value,
            doc_type=request.doc_type.value,
            success=False,
        )

        try:
            # 1. Generate the document via exporter
            output_path = self.exporter.export_single(
                condition=schema,
                doc_type=request.doc_type,
                tier=request.tier,
            )
            result.output_path = str(output_path)
            result.success = True

            # 2. Run QA if requested
            if request.with_qa:
                qa_result = self._run_qa(schema, request)
                if qa_result is not None:
                    result.qa_passed = qa_result.get("passed", None)
                    result.qa_issues = qa_result.get("issues", [])

            # 3. Generate visuals if requested
            if request.with_visuals:
                visuals = self._generate_visuals(schema, request)
                result.visuals_generated = visuals

            # 4. Curate and insert web images if requested
            if self.with_images:
                n_inserted = self._curate_and_insert_images(schema, request, output_path)
                result.images_inserted = n_inserted

            # 5. Convert to PDF if requested
            if self.with_pdf:
                pdf = self._convert_to_pdf(output_path)
                if pdf:
                    result.pdf_path = str(pdf)

            logger.info(
                f"Generated: {request.condition_slug}/{request.tier.value}/"
                f"{request.doc_type.value} -> {output_path.name}"
            )

        except Exception as e:
            result.error = str(e)
            logger.error(
                f"Failed: {request.condition_slug}/{request.tier.value}/"
                f"{request.doc_type.value}: {e}",
                exc_info=True,
            )

        return result

    def _curate_and_insert_images(
        self, schema: ConditionSchema, request: GenerationRequest, docx_path: Path
    ) -> int:
        """Curate web images and insert them into the generated DOCX."""
        try:
            from ..images.curator import ImageCurator
            from ..images.inserter import DocumentImageInserter
            from docx import Document as DocxDocument

            curator = ImageCurator(enable_web_search=True)
            manifest = curator.curate_for_document(
                condition_slug=request.condition_slug,
                document_type=request.doc_type.value,
                tier=request.tier.value,
            )

            if not manifest.images:
                logger.debug("No images curated for this document")
                return 0

            # Open the generated DOCX and append images
            doc = DocxDocument(str(docx_path))
            inserter = DocumentImageInserter()
            n_inserted = inserter.insert_images(doc, manifest)

            if n_inserted > 0:
                doc.save(str(docx_path))
                logger.info(f"Inserted {n_inserted} web images into {docx_path.name}")

                # Save manifest for provenance
                manifest_path = docx_path.parent / f"{docx_path.stem}_images.json"
                curator.save_manifest(manifest, manifest_path)

            return n_inserted

        except ImportError as e:
            logger.debug(f"Image curation unavailable: {e}")
            return 0
        except Exception as e:
            logger.warning(f"Image curation failed: {e}")
            return 0

    @staticmethod
    def _convert_to_pdf(docx_path: Path) -> Optional[Path]:
        """Convert DOCX to PDF if converter is available."""
        try:
            from ..docx.pdf_export import convert_to_pdf
            return convert_to_pdf(docx_path)
        except ImportError:
            logger.debug("PDF export module not available")
            return None
        except Exception as e:
            logger.debug(f"PDF conversion failed: {e}")
            return None

    def _run_qa(self, schema: ConditionSchema, request: GenerationRequest) -> Optional[dict]:
        """Run QA checks on a generated document. Returns summary dict or None."""
        try:
            from ..qa.engine import QAEngine
            engine = QAEngine()
            report = engine.check_condition(schema)
            return {
                "passed": report.passed,
                "issues": [f"[{i.severity.value}] {i.message}" for i in report.issues[:10]],
            }
        except Exception as e:
            logger.debug(f"QA check skipped: {e}")
            return None

    def _generate_visuals(self, schema: ConditionSchema, request: GenerationRequest) -> list[str]:
        """Generate visual assets for the document. Returns list of generated file paths."""
        generated = []
        try:
            visuals_dir = self.output_dir.parent / "visuals" / schema.slug
            visuals_dir.mkdir(parents=True, exist_ok=True)

            defn = get_document_definition(request.doc_type)

            # Map visual types to generator functions
            generators = self._get_visual_generators()

            for vspec in defn.visuals:
                gen_func = generators.get(vspec.visual_type)
                if gen_func is None:
                    logger.debug(f"No generator for visual type: {vspec.visual_type}")
                    continue
                try:
                    result = gen_func(schema, str(visuals_dir))
                    if result:
                        if isinstance(result, list):
                            generated.extend(str(p) for p in result)
                        else:
                            generated.append(str(result))
                except Exception as e:
                    logger.debug(f"Visual {vspec.visual_type} skipped: {e}")

        except ImportError:
            logger.debug("Visual generation skipped (matplotlib not available)")
        except Exception as e:
            logger.debug(f"Visual generation error: {e}")

        return generated

    @staticmethod
    def _get_visual_generators() -> dict:
        """Lazy-load all visual generator functions."""
        generators = {}
        try:
            from ..visuals.brain_maps import BrainMapGenerator
            bmg = BrainMapGenerator()
            generators["brain_map"] = lambda c, d: bmg.generate_target_map(c, d)
        except ImportError:
            pass
        try:
            from ..visuals.network_diagrams import NetworkDiagramGenerator
            ndg = NetworkDiagramGenerator()
            generators["network_diagram"] = lambda c, d: ndg.generate_network_diagram(c, d)
        except ImportError:
            pass
        try:
            from ..visuals.qeeg_topomap import generate_qeeg_for_condition
            generators["qeeg_topomap"] = generate_qeeg_for_condition
            generators["eeg_topomap"] = generate_qeeg_for_condition
        except ImportError:
            pass
        try:
            from ..visuals.mri_target_view import generate_mri_for_condition
            generators["mri_target_view"] = generate_mri_for_condition
        except ImportError:
            pass
        try:
            from ..visuals.protocol_panel import generate_protocol_panel_for_condition
            generators["montage_panel"] = generate_protocol_panel_for_condition
            generators["protocol_panel"] = generate_protocol_panel_for_condition
        except ImportError:
            pass
        try:
            from ..visuals.connectivity_map import generate_connectivity_for_condition
            generators["connectivity_map"] = generate_connectivity_for_condition
        except ImportError:
            pass
        try:
            from ..visuals.symptom_flow import SymptomFlowGenerator
            sfg = SymptomFlowGenerator()
            generators["symptom_flow"] = lambda c, d: sfg.generate_symptom_flow(c, d)
        except ImportError:
            pass
        try:
            from ..visuals.patient_journey import PatientJourneyGenerator
            pjg = PatientJourneyGenerator()
            generators["patient_journey"] = lambda c, d: pjg.generate_journey_diagram(c.slug, d)
        except ImportError:
            pass
        # ── New visual generators ──────────────────────────────────────
        try:
            from ..visuals.axial_brain_view import generate_axial_for_condition
            generators["axial_brain_view"] = generate_axial_for_condition
        except ImportError:
            pass
        try:
            from ..visuals.coronal_brain_view import generate_coronal_for_condition
            generators["coronal_brain_view"] = generate_coronal_for_condition
        except ImportError:
            pass
        try:
            from ..visuals.treatment_timeline import generate_timeline_for_condition
            generators["treatment_timeline"] = generate_timeline_for_condition
        except ImportError:
            pass
        try:
            from ..visuals.dose_response import generate_dose_response_for_condition
            generators["dose_response"] = generate_dose_response_for_condition
        except ImportError:
            pass
        try:
            from ..visuals.spectral_topomap import generate_spectral_for_condition
            generators["spectral_topomap"] = generate_spectral_for_condition
        except ImportError:
            pass
        try:
            from ..visuals.impedance_map import generate_impedance_for_condition
            generators["impedance_map"] = generate_impedance_for_condition
        except ImportError:
            pass
        return generators

    def list_conditions(self) -> list[str]:
        """List all available condition slugs."""
        return self.registry.list_slugs()

    def list_document_types(self) -> list[str]:
        """List all document type values."""
        return [dt.value for dt in DocumentType]
