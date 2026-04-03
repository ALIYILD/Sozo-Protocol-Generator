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
        self._knowledge_base = None

    @property
    def registry(self):
        if self._registry is None:
            self._registry = get_registry()
        return self._registry

    @property
    def knowledge_base(self):
        """Lazy-loaded KnowledgeBase for the SOZO knowledge system."""
        if self._knowledge_base is None:
            try:
                from ..knowledge.base import KnowledgeBase
                self._knowledge_base = KnowledgeBase()
                self._knowledge_base.load_all()
            except Exception as e:
                logger.debug(f"Knowledge base not available: {e}")
                self._knowledge_base = None
        return self._knowledge_base

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

        # Execute — prefer canonical path where safe
        results = []
        for req in requests:
            dt_value = req.doc_type.value if hasattr(req.doc_type, 'value') else str(req.doc_type)
            tier_value = req.tier.value if hasattr(req.tier, 'value') else str(req.tier)

            if self.can_route_canonical(condition, dt_value):
                # Canonical path (stronger evidence/QA, provenance)
                result = self.generate_canonical(condition, dt_value, tier_value)
                result.doc_type = dt_value  # Normalize
                logger.info(f"Routed to canonical: {condition}/{dt_value}/{tier_value}")
            else:
                # Legacy path (fallback)
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

    def get_knowledge_summary(self, condition_slug: str) -> Optional[dict]:
        """Get a knowledge summary for a condition from the knowledge base.

        Returns None if knowledge base is not available or condition not found.
        """
        kb = self.knowledge_base
        if not kb:
            return None

        cond = kb.get_condition(condition_slug)
        if not cond:
            return None

        mods = kb.get_modalities_for_condition(condition_slug)
        contras = []
        for m in mods:
            contras.extend(kb.get_contraindications_for_modality(m.slug))

        return {
            "condition": {
                "slug": cond.slug,
                "name": cond.display_name,
                "icd10": cond.icd10,
                "category": cond.category,
                "evidence_quality": cond.evidence_quality,
                "protocols": len(cond.protocols),
                "phenotypes": len(cond.phenotypes),
                "references": len(cond.references),
            },
            "modalities": [
                {"slug": m.slug, "name": m.name, "regulatory": m.regulatory_status[:80]}
                for m in mods
            ],
            "contraindications": list({c.slug for c in contras}),
            "shared_rules": [r.slug for r in kb.get_shared_rules()],
            "knowledge_base_summary": kb.summary(),
        }

    def generate_canonical(
        self,
        condition: str,
        doc_type: str = "evidence_based_protocol",
        tier: str = "fellow",
    ) -> GenerationResult:
        """Generate a document using the canonical blueprint-driven path.

        This uses the KnowledgeBase + DocumentBlueprint to assemble
        documents without hardcoded dispatch logic.

        Args:
            condition: Condition slug (must exist in knowledge base)
            doc_type: Blueprint slug (e.g. "evidence_based_protocol")
            tier: "fellow" or "partners"
        """
        import uuid
        result = GenerationResult(
            condition_slug=condition,
            tier=tier,
            doc_type=doc_type,
            success=False,
            build_id=f"canon-{uuid.uuid4().hex[:8]}",
        )

        try:
            kb = self.knowledge_base
            if not kb:
                result.error = "Knowledge base not available"
                return result

            # Assemble document from blueprint + knowledge
            from ..knowledge.assembler import CanonicalDocumentAssembler
            assembler = CanonicalDocumentAssembler(kb)
            spec, provenance = assembler.assemble(condition, doc_type, tier)

            # Run safety validation before rendering
            cond_obj = kb.get_condition(condition)
            if cond_obj:
                from ..knowledge.safety import SafetyValidator
                validator = SafetyValidator()
                safety_report = validator.validate_protocol(
                    condition_slug=condition,
                    protocols=[p.model_dump() for p in cond_obj.protocols],
                    safety_rules=[s.model_dump() for s in cond_obj.safety_rules],
                    doc_type=doc_type, tier=tier,
                )
                if not safety_report.passed:
                    result.qa_issues.extend(
                        [f"[SAFETY BLOCK] {c.message}" for c in safety_report.checks if c.severity == "block"]
                    )

            # Render using existing renderer
            output_path = self.exporter.renderer.render(spec)
            result.output_path = str(output_path)
            result.success = True

            # Save provenance sidecar
            import json
            prov_path = Path(str(output_path)).with_suffix(".provenance.json")
            prov_path.write_text(json.dumps(provenance.to_dict(), indent=2))

            result.qa_issues = provenance.warnings

            # Visuals
            if self.with_visuals:
                cond_schema = self.registry.get(condition) if self.registry.exists(condition) else None
                if cond_schema:
                    visuals = self._generate_visuals(cond_schema, GenerationRequest(
                        condition_slug=condition,
                        tier=Tier(tier),
                        doc_type=DocumentType(doc_type) if doc_type in [dt.value for dt in DocumentType] else DocumentType.EVIDENCE_BASED_PROTOCOL,
                        with_visuals=True, with_qa=False,
                    ))
                    result.visuals_generated = visuals

            # PDF
            if self.with_pdf:
                pdf = self._convert_to_pdf(Path(result.output_path))
                if pdf:
                    result.pdf_path = str(pdf)

            logger.info(f"Canonical generation: {condition}/{doc_type}/{tier} → {output_path}")

        except Exception as e:
            result.error = str(e)
            logger.error(f"Canonical generation failed: {e}", exc_info=True)

        return result

    def generate_from_template(
        self,
        template_path: Optional[str] = None,
        template_id: Optional[str] = None,
        condition: str = "parkinsons",
        tier: str = "partners",
        with_ai: bool = False,
        with_research: bool = True,
        anthropic_api_key: str = "",
        openai_api_key: str = "",
    ) -> GenerationResult:
        """Generate a document using an uploaded template as the structural guide.

        This is the template-driven AI-assisted generation path. It:
        1. Ingests the template (or loads a stored profile)
        2. Researches evidence per section
        3. Builds section briefs
        4. Writes content (data-driven or AI-assisted)
        5. Validates grounding
        6. Renders DOCX matching template style
        7. Returns result with full provenance

        Args:
            template_path: Path to DOCX template (used if template_id not given)
            template_id: ID of a stored template profile
            condition: Target condition slug
            tier: "fellow" or "partners"
            with_ai: Use LLM for section drafting
            with_research: Search PubMed for evidence
            anthropic_api_key: Anthropic API key for AI drafting
            openai_api_key: OpenAI API key (alternative)
        """
        import uuid
        build_id = f"tpl-{uuid.uuid4().hex[:8]}"
        result = GenerationResult(
            condition_slug=condition,
            tier=tier,
            doc_type="from_template",
            success=False,
            build_id=build_id,
        )

        try:
            # 1. Get or build template profile
            from ..template_profiles.builder import build_template_profile
            from ..template_profiles.store import TemplateProfileStore
            from ..template_profiles.models import DocumentBuildManifest

            store = TemplateProfileStore()
            profile = None

            if template_id:
                profile = store.load(template_id)
                if not profile:
                    result.error = f"Template profile not found: {template_id}"
                    return result
            elif template_path:
                profile = build_template_profile(template_path)
                store.save(profile)
            else:
                result.error = "Either template_path or template_id must be provided"
                return result

            result.doc_type = profile.inferred_doc_type or "from_template"

            # 2. Get condition
            if not self.registry.exists(condition):
                result.error = f"Unknown condition: {condition}"
                return result
            schema = self.registry.get(condition)

            # 3. Research evidence per section
            from ..research.orchestrator import ResearchOrchestrator
            orchestrator = ResearchOrchestrator(use_pubmed=with_research)
            bundles = orchestrator.research_all_sections(
                condition, schema.display_name, profile.section_map
            )

            # 4. Build section briefs
            from ..writers.brief_builder import BriefBuilder
            brief_builder = BriefBuilder(
                condition=schema,
                tier=tier,
                doc_type=profile.inferred_doc_type or "document",
                template_sections=profile.section_map,
                research_bundles=bundles,
                tone_profile=profile.tone_profile,
            )
            briefs = brief_builder.build_all()

            # 5. Write sections
            from ..writers.section_writer import SectionWriter
            writer = SectionWriter(
                anthropic_api_key=anthropic_api_key if with_ai else "",
                openai_api_key=openai_api_key if with_ai else "",
            )
            drafted_sections = writer.write_all(briefs)

            # 6. Validate grounding
            from ..grounding.validator import GroundingValidator
            validator = GroundingValidator(target_condition_slug=condition)
            grounding_results = validator.validate_all(
                drafted_sections, bundles, condition
            )

            # Collect issues
            all_issues = []
            for gr in grounding_results:
                for issue in gr.issues:
                    all_issues.append(f"[{issue.severity}] {issue.section_id}: {issue.message}")

            # 7. Convert to DocumentSpec and render
            from ..schemas.documents import DocumentSpec, SectionContent
            from ..core.enums import DocumentType, Tier

            sections = []
            for draft in drafted_sections:
                sc = SectionContent(
                    section_id=draft.section_id,
                    title=draft.title,
                    content=draft.content,
                    tables=draft.tables,
                    figures=draft.figures,
                    review_flags=draft.review_flags,
                    evidence_pmids=draft.citations_used,
                    confidence_label=draft.confidence,
                    is_placeholder=draft.needs_review and not draft.content,
                )
                sections.append(sc)

            doc_type_enum = DocumentType(profile.inferred_doc_type) if profile.inferred_doc_type else DocumentType.EVIDENCE_BASED_PROTOCOL
            tier_enum = Tier(tier)

            spec = DocumentSpec(
                document_type=doc_type_enum,
                tier=tier_enum,
                condition_slug=condition,
                condition_name=schema.display_name,
                title=f"{profile.name} — {schema.display_name}",
                version="1.0",
                audience="clinician",
                sections=sections,
                references=schema.references,
                review_flags=[i for i in all_issues if "[block]" in i.lower()],
                build_id=build_id,
            )

            # Render
            output_path = self.exporter.renderer.render(spec)
            result.output_path = str(output_path)
            result.success = True
            result.qa_issues = all_issues[:20]

            # 8. Generate visuals if requested
            if self.with_visuals:
                visuals = self._generate_visuals(schema, GenerationRequest(
                    condition_slug=condition,
                    tier=tier_enum,
                    doc_type=doc_type_enum,
                    with_visuals=True,
                    with_qa=False,
                ))
                result.visuals_generated = visuals

            # 9. Build manifest
            manifest = DocumentBuildManifest(
                build_id=build_id,
                condition_slug=condition,
                condition_name=schema.display_name,
                tier=tier,
                doc_type=profile.inferred_doc_type or "from_template",
                template_profile_id=profile.profile_id,
                template_name=profile.name,
                sections_generated=[d.section_id for d in drafted_sections],
                sections_from_ai=sum(1 for d in drafted_sections if d.generation_method == "ai_draft"),
                sections_from_data=sum(1 for d in drafted_sections if d.generation_method == "data_driven"),
                sections_from_template=sum(1 for d in drafted_sections if d.generation_method == "template_adapt"),
                sections_needing_review=sum(1 for d in drafted_sections if d.needs_review),
                visuals_generated=result.visuals_generated,
                qa_issues=all_issues,
                output_paths={"docx": str(output_path)},
            )

            # Save manifest
            manifest_path = Path(str(output_path)).parent / f"{build_id}_manifest.json"
            manifest_path.write_text(manifest.model_dump_json(indent=2))

            logger.info(
                f"Template-driven generation complete: {condition}/{tier} "
                f"({len(drafted_sections)} sections, {manifest.sections_from_ai} AI, "
                f"{manifest.sections_from_data} data-driven)"
            )

        except Exception as e:
            result.error = str(e)
            logger.error(f"Template-driven generation failed: {e}", exc_info=True)

        return result

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

    # ── Canonical routing helpers ─────────────────────────────────────

    _CANONICAL_BLUEPRINTS = {
        "evidence_based_protocol": "evidence_based_protocol",
        "handbook": "handbook",
        "clinical_exam": "clinical_exam",
        "all_in_one_protocol": "all_in_one_protocol",
        "phenotype_classification": "phenotype_classification",
        "responder_tracking": "responder_tracking",
        "psych_intake": "psych_intake",
        "network_assessment": "network_assessment",
    }

    def can_route_canonical(self, condition: str, doc_type: str) -> bool:
        """Check if a legacy generate() call can be safely routed to canonical."""
        kb = self.knowledge_base
        if not kb:
            return False
        if doc_type not in self._CANONICAL_BLUEPRINTS:
            return False
        return kb.get_condition(condition) is not None

    def list_conditions(self) -> list[str]:
        """List all available condition slugs."""
        return self.registry.list_slugs()

    def list_document_types(self) -> list[str]:
        """List all document type values."""
        return [dt.value for dt in DocumentType]
