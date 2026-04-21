from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..core.settings import get_settings
from ..orchestration.versioning import ManifestWriter, create_build_id
from .service import GenerationService, GenerationResult


DEFAULT_DOC_TYPES = (
    "clinical_exam",
    "evidence_based_protocol",
    "handbook",
)

DEFAULT_TIERS = (
    "fellow",
    "partners",
)


@dataclass
class ProductionRun:
    build_id: str
    condition_slug: str
    outputs: dict[str, Path]
    pdf_outputs: dict[str, Path]
    results: list[GenerationResult]
    manifest_path: Optional[Path] = None


def generate_condition_documents(
    *,
    condition_slug: str,
    doc_types: tuple[str, ...] = DEFAULT_DOC_TYPES,
    tiers: tuple[str, ...] = DEFAULT_TIERS,
    output_dir: Optional[str] = None,
    with_pdf: bool = False,
    with_visuals: bool = False,
    with_qa: bool = True,
    dry_run: bool = False,
    validate_only: bool = False,
) -> ProductionRun:
    """Generate the canonical 3×2 long-form document set for one condition.

    Returns a ProductionRun with output paths and a persisted build manifest.
    """
    settings = get_settings()
    build_id = create_build_id(condition_slug)

    svc = GenerationService(
        output_dir=output_dir,
        with_visuals=with_visuals,
        with_qa=with_qa,
        with_pdf=with_pdf,
    )

    outputs: dict[str, Path] = {}
    pdf_outputs: dict[str, Path] = {}
    results: list[GenerationResult] = []

    for tier in tiers:
        for doc_type in doc_types:
            key = f"{tier}_{doc_type}"
            if validate_only:
                assembled = svc.assemble_canonical_document(condition_slug, doc_type, tier)
                if not assembled.ok:
                    results.append(
                        GenerationResult(
                            condition_slug=condition_slug,
                            tier=tier,
                            doc_type=doc_type,
                            success=False,
                            error=assembled.error or "validation failed",
                            qa_issues=list(assembled.safety_qa_issues),
                            build_id=f"{build_id}-{key}",
                        )
                    )
                else:
                    results.append(
                        GenerationResult(
                            condition_slug=condition_slug,
                            tier=tier,
                            doc_type=doc_type,
                            success=True,
                            qa_issues=list(assembled.safety_qa_issues),
                            build_id=f"{build_id}-{key}",
                        )
                    )
                continue

            if dry_run:
                results.append(
                    GenerationResult(
                        condition_slug=condition_slug,
                        tier=tier,
                        doc_type=doc_type,
                        success=True,
                        output_path=None,
                        build_id=f"{build_id}-{key}",
                    )
                )
                continue

            res = svc.generate_canonical(condition_slug, doc_type, tier)
            res.build_id = f"{build_id}-{key}"
            results.append(res)
            if res.success and res.output_path:
                outputs[key] = Path(res.output_path)
            if res.success and res.pdf_path:
                pdf_outputs[key] = Path(res.pdf_path)

    manifest_path: Optional[Path] = None
    if settings.enable_build_manifests and not dry_run:
        try:
            kb = svc.knowledge_base
            cond = kb.get_condition(condition_slug) if kb else None
            writer = ManifestWriter(manifests_dir=settings.manifests_dir / "documents")
            manifest = writer.create_manifest(
                build_id=build_id,
                condition_slug=condition_slug,
                condition_name=(cond.display_name if cond else condition_slug),
                document_outputs=outputs,
                qa_summary=None,
            )
            manifest_path = writer.save_manifest(manifest)
        except Exception:
            manifest_path = None

    return ProductionRun(
        build_id=build_id,
        condition_slug=condition_slug,
        outputs=outputs,
        pdf_outputs=pdf_outputs,
        results=results,
        manifest_path=manifest_path,
    )

