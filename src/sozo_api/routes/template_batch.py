"""Batch generation from an uploaded DOCX template (Streamlit parity for /api)."""
from __future__ import annotations

import io
import logging
import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from sozo_api.error_responses import INTERNAL_SERVER_DETAIL
from sozo_auth.dependencies import get_current_user, require_clinician
from sozo_generator.core.enums import DocumentType, Tier
from sozo_generator.core.exceptions import ConditionNotFoundError
from sozo_generator.conditions.registry import get_registry
from sozo_generator.docx.renderer import DocumentRenderer
from sozo_generator.template.template_driven_generator import TemplateDrivenGenerator

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/generate",
    tags=["generation"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/template-batch",
    dependencies=[Depends(require_clinician)],
)
def post_template_batch(
    template: UploadFile = File(..., description="DOCX with Heading styles"),
    condition_slugs: str = Form(
        ...,
        description="Comma-separated slugs, e.g. depression,parkinsons",
    ),
    tier: str = Form("fellow", description="fellow, partners, or both"),
    document_type: str | None = Form(
        None,
        description="Optional DocumentType enum value to override inference from filename",
    ),
):
    """
    Parse structure, render per condition/tier with layout copied from the upload, ZIP results.
    """
    name = template.filename or "template.docx"
    if not name.lower().endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Template must be a .docx file.",
        )

    slugs = [s.strip() for s in condition_slugs.split(",") if s.strip()]
    if not slugs:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one condition slug is required.",
        )

    tier_key = tier.strip().lower()
    try:
        if tier_key == "both":
            tier_enum = Tier.BOTH
        else:
            tier_enum = Tier(tier_key)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid tier. Use fellow, partners, or both.",
        )
    tiers = [Tier.FELLOW, Tier.PARTNERS] if tier_enum == Tier.BOTH else [tier_enum]

    doc_type_override: DocumentType | None = None
    if document_type is not None and document_type.strip():
        try:
            doc_type_override = DocumentType(document_type.strip())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid document_type: {document_type}",
            )

    registry = get_registry()
    for slug in slugs:
        if not registry.exists(slug):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unknown condition: {slug}",
            )

    try:
        raw = template.file.read()
    finally:
        template.file.close()

    try:
        buf = io.BytesIO()
        with tempfile.TemporaryDirectory(prefix="sozo_template_batch_") as tmp:
            tdir = Path(tmp)
            template_path = tdir / "uploaded_template.docx"
            template_path.write_bytes(raw)

            generator = TemplateDrivenGenerator(template_path)
            template_sections = generator.parse_template()
            if not template_sections:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        "Could not parse sections from template. "
                        "Ensure headings use Word Heading styles."
                    ),
                )

            out_root = tdir / "out"
            out_root.mkdir(parents=True, exist_ok=True)
            renderer = DocumentRenderer(output_dir=str(out_root))

            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for slug in slugs:
                    try:
                        condition = registry.get(slug)
                    except ConditionNotFoundError as exc:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=str(exc),
                        ) from exc
                    for t in tiers:
                        spec = generator.generate_for_condition(
                            condition,
                            t,
                            document_type=doc_type_override,
                        )
                        out_file = out_root / spec.output_filename
                        renderer.render(
                            spec,
                            out_file,
                            layout_template_path=template_path,
                        )
                        zf.write(out_file, arcname=spec.output_filename)

        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/zip",
            headers={
                "Content-Disposition": 'attachment; filename="sozo_template_batch.zip"',
            },
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("template-batch generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_DETAIL,
        ) from None
