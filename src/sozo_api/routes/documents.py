from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from sozo_api.error_responses import INTERNAL_SERVER_DETAIL
from sozo_auth.dependencies import require_clinician, require_role


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["documents"],
)


class DocumentsGenerateRequest(BaseModel):
    condition_slug: str = Field(..., min_length=1)
    doc_type: str = Field("all", pattern="^(assessment|protocol|handbook|all)$")
    tier: str = Field("both", pattern="^(fellow|partners|both)$")
    pdf: bool = False
    visuals: bool = False
    qa: bool = True
    dry_run: bool = False
    validate_only: bool = False


@router.post("/generate", dependencies=[Depends(require_clinician)])
def generate_documents(body: DocumentsGenerateRequest) -> dict[str, Any]:
    """Generate Assessment/Protocol/Handbook docs (Fellow/Partners) for one condition."""
    try:
        from sozo_generator.generation.document_production import (
            generate_condition_documents,
            DEFAULT_DOC_TYPES,
        )

        doc_map = {
            "assessment": ("clinical_exam",),
            "protocol": ("evidence_based_protocol",),
            "handbook": ("handbook",),
            "all": DEFAULT_DOC_TYPES,
        }
        tiers = ("fellow", "partners") if body.tier == "both" else (body.tier,)

        run = generate_condition_documents(
            condition_slug=body.condition_slug,
            doc_types=tuple(doc_map[body.doc_type]),
            tiers=tuple(tiers),
            with_pdf=body.pdf,
            with_visuals=body.visuals,
            with_qa=body.qa,
            dry_run=body.dry_run,
            validate_only=body.validate_only,
        )

        return {
            "build_id": run.build_id,
            "condition_slug": run.condition_slug,
            "manifest_path": str(run.manifest_path) if run.manifest_path else None,
            "artifacts": {k: str(p) for k, p in run.outputs.items()},
            "pdf_artifacts": {k: str(p) for k, p in run.pdf_outputs.items()},
            "results": [
                {
                    "tier": r.tier,
                    "doc_type": r.doc_type,
                    "success": r.success,
                    "output_path": r.output_path,
                    "pdf_path": r.pdf_path,
                    "error": r.error,
                    "qa_issues": r.qa_issues,
                }
                for r in run.results
            ],
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_DETAIL)


@router.post(
    "/generate/batch",
    dependencies=[Depends(require_role("operator", "admin"))],
)
def generate_documents_batch(
    pdf: bool = Query(False),
    visuals: bool = Query(False),
    qa: bool = Query(True),
    dry_run: bool = Query(False),
    limit: Optional[int] = Query(None, ge=1, le=200),
) -> dict[str, Any]:
    """Generate the full 3×2 set for all knowledge conditions (synchronous)."""
    try:
        from sozo_generator.knowledge.base import KnowledgeBase
        from sozo_generator.generation.document_production import generate_condition_documents

        kb = KnowledgeBase()
        kb.load_all()
        slugs = kb.list_conditions()
        if limit is not None:
            slugs = slugs[:limit]

        builds = []
        for slug in slugs:
            run = generate_condition_documents(
                condition_slug=slug,
                with_pdf=pdf,
                with_visuals=visuals,
                with_qa=qa,
                dry_run=dry_run,
            )
            builds.append(
                {
                    "condition_slug": slug,
                    "build_id": run.build_id,
                    "manifest_path": str(run.manifest_path) if run.manifest_path else None,
                    "artifacts_count": len(run.outputs),
                }
            )

        return {"count": len(builds), "builds": builds}
    except Exception:
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_DETAIL)


@router.get("/status/{build_id}", dependencies=[Depends(require_clinician)])
def document_status(build_id: str) -> dict[str, Any]:
    """Load a build manifest by build_id (filesystem-backed)."""
    try:
        from sozo_generator.core.settings import get_settings
        from sozo_generator.orchestration.versioning import ManifestWriter

        settings = get_settings()
        writer = ManifestWriter(manifests_dir=settings.manifests_dir / "documents")
        manifest = writer.load_manifest(build_id)
        if manifest is None:
            raise HTTPException(status_code=404, detail="Build not found")
        return manifest.model_dump(mode="json")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_DETAIL)


@router.get(
    "/download/{build_id}/{artifact_key}",
    dependencies=[Depends(require_clinician)],
)
def download_artifact(build_id: str, artifact_key: str) -> FileResponse:
    """Download a generated artifact by manifest key (e.g. fellow_handbook)."""
    try:
        from sozo_generator.core.settings import get_settings
        from sozo_generator.orchestration.versioning import ManifestWriter

        settings = get_settings()
        writer = ManifestWriter(manifests_dir=settings.manifests_dir / "documents")
        manifest = writer.load_manifest(build_id)
        if manifest is None:
            raise HTTPException(status_code=404, detail="Build not found")

        match = None
        for d in manifest.documents:
            if f"{d.tier}_{d.document_type}" == artifact_key:
                match = d
                break
        if match is None or not match.output_path:
            raise HTTPException(status_code=404, detail="Artifact not found")

        path = Path(match.output_path)
        # Basic path safety: artifact must live under outputs/
        outputs_root = Path("outputs").resolve()
        if outputs_root not in path.resolve().parents:
            raise HTTPException(status_code=400, detail="Invalid artifact path")
        if not path.exists():
            raise HTTPException(status_code=404, detail="Artifact missing on disk")

        return FileResponse(
            str(path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=path.name,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_DETAIL)

