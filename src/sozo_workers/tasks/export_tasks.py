"""Export tasks — async PDF/DOCX generation and batch visual rendering."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded

from sozo_workers.status import TaskStatusTracker

logger = logging.getLogger(__name__)

_tracker: Optional[TaskStatusTracker] = None


def _get_tracker() -> TaskStatusTracker:
    global _tracker
    if _tracker is None:
        _tracker = TaskStatusTracker()
    return _tracker


def _audit_event(event_type: str, data: dict) -> None:
    logger.info(
        "AUDIT event=%s ts=%s data=%s",
        event_type,
        datetime.now(timezone.utc).isoformat(),
        data,
    )


def _resolve_protocol_output_path(protocol_version_id: str) -> Optional[Path]:
    """Resolve the DOCX output path for a protocol version.

    Looks in the standard output directories for a matching build file.
    In production this would query the protocol version DB table.
    """
    from sozo_generator.core.settings import get_settings
    settings = get_settings()

    # Search in the documents output directory
    docs_dir = settings.output_dir / "documents"
    if docs_dir.exists():
        # Try direct match on build_id or protocol_version_id
        for docx_file in docs_dir.rglob("*.docx"):
            if protocol_version_id in docx_file.stem:
                return docx_file

    # Also check the manifests directory for a reference
    manifests_dir = settings.manifests_dir
    if manifests_dir.exists():
        import json
        for manifest_file in manifests_dir.rglob("*_manifest.json"):
            try:
                manifest = json.loads(manifest_file.read_text())
                if manifest.get("build_id") == protocol_version_id:
                    output_paths = manifest.get("output_paths", {})
                    docx_path = output_paths.get("docx")
                    if docx_path and Path(docx_path).exists():
                        return Path(docx_path)
            except (json.JSONDecodeError, OSError):
                continue

    return None


@shared_task(
    bind=True,
    name="sozo_workers.tasks.export_tasks.export_protocol_pdf",
    max_retries=2,
    default_retry_delay=30,
    acks_late=True,
    queue="sozo_default",
)
def export_protocol_pdf(
    self,
    protocol_version_id: str,
    user_id: str = "",
) -> dict:
    """Generate a PDF from an existing protocol version.

    Looks up the DOCX output for the given protocol version and converts
    it to PDF.

    Args:
        protocol_version_id: Build ID or protocol version identifier.
        user_id: Requesting user.

    Returns:
        Dict with PDF path and metadata.
    """
    task_id = self.request.id
    tracker = _get_tracker()

    tracker.set_status(
        task_id, "STARTED", progress=0.0,
        message=f"Starting PDF export for protocol: {protocol_version_id}",
        user_id=user_id,
    )
    _audit_event("export_pdf.started", {
        "task_id": task_id,
        "protocol_version_id": protocol_version_id,
        "user_id": user_id,
    })

    try:
        # Locate the source DOCX
        docx_path = _resolve_protocol_output_path(protocol_version_id)
        if docx_path is None:
            error_msg = f"No DOCX found for protocol version: {protocol_version_id}"
            tracker.set_status(
                task_id, "FAILURE", message=error_msg, user_id=user_id,
            )
            return {"error": error_msg}

        tracker.set_status(
            task_id, "PROGRESS", progress=0.3,
            message=f"Converting {docx_path.name} to PDF...",
            user_id=user_id,
        )

        # Convert to PDF
        from sozo_generator.docx.pdf_export import convert_to_pdf
        pdf_path = convert_to_pdf(docx_path)

        if pdf_path is None:
            error_msg = "PDF conversion returned None — converter may not be installed"
            tracker.set_status(
                task_id, "FAILURE", message=error_msg, user_id=user_id,
            )
            return {"error": error_msg}

        output = {
            "protocol_version_id": protocol_version_id,
            "source_docx": str(docx_path),
            "pdf_path": str(pdf_path),
            "file_size_bytes": pdf_path.stat().st_size,
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

        tracker.set_status(
            task_id, "SUCCESS", progress=1.0,
            message=f"PDF exported: {pdf_path.name}",
            metadata=output,
            user_id=user_id,
        )
        _audit_event("export_pdf.completed", {
            "task_id": task_id,
            "protocol_version_id": protocol_version_id,
            "pdf_path": str(pdf_path),
            "user_id": user_id,
        })

        return output

    except SoftTimeLimitExceeded:
        tracker.set_status(
            task_id, "FAILURE",
            message="PDF export exceeded time limit",
            user_id=user_id,
        )
        raise

    except ImportError as exc:
        error_msg = f"PDF export dependency missing: {exc}"
        logger.error(error_msg)
        tracker.set_status(
            task_id, "FAILURE", message=error_msg, user_id=user_id,
        )
        return {"error": error_msg}

    except Exception as exc:
        logger.exception("export_protocol_pdf failed")
        tracker.set_status(
            task_id, "FAILURE",
            message=f"PDF export failed: {exc}",
            user_id=user_id,
        )
        _audit_event("export_pdf.failed", {
            "task_id": task_id, "error": str(exc), "user_id": user_id,
        })
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    name="sozo_workers.tasks.export_tasks.export_protocol_docx",
    max_retries=2,
    default_retry_delay=30,
    acks_late=True,
    queue="sozo_default",
)
def export_protocol_docx(
    self,
    protocol_version_id: str,
    user_id: str = "",
) -> dict:
    """Re-generate the DOCX for a protocol version.

    This re-renders the document from the stored spec/manifest, useful when
    template styles have been updated.

    Args:
        protocol_version_id: Build ID or protocol version identifier.
        user_id: Requesting user.

    Returns:
        Dict with DOCX path and metadata.
    """
    task_id = self.request.id
    tracker = _get_tracker()

    tracker.set_status(
        task_id, "STARTED", progress=0.0,
        message=f"Starting DOCX export for protocol: {protocol_version_id}",
        user_id=user_id,
    )
    _audit_event("export_docx.started", {
        "task_id": task_id,
        "protocol_version_id": protocol_version_id,
        "user_id": user_id,
    })

    try:
        # Check if the DOCX already exists
        existing_path = _resolve_protocol_output_path(protocol_version_id)
        if existing_path and existing_path.exists():
            output = {
                "protocol_version_id": protocol_version_id,
                "docx_path": str(existing_path),
                "file_size_bytes": existing_path.stat().st_size,
                "source": "existing",
                "exported_at": datetime.now(timezone.utc).isoformat(),
            }
            tracker.set_status(
                task_id, "SUCCESS", progress=1.0,
                message=f"DOCX already exists: {existing_path.name}",
                metadata=output,
                user_id=user_id,
            )
            return output

        # If no existing file, try to regenerate from manifest
        from sozo_generator.core.settings import get_settings
        import json

        settings = get_settings()
        manifests_dir = settings.manifests_dir

        manifest_data = None
        if manifests_dir.exists():
            for manifest_file in manifests_dir.rglob("*_manifest.json"):
                try:
                    data = json.loads(manifest_file.read_text())
                    if data.get("build_id") == protocol_version_id:
                        manifest_data = data
                        break
                except (json.JSONDecodeError, OSError):
                    continue

        if manifest_data is None:
            error_msg = f"No manifest found for protocol version: {protocol_version_id}"
            tracker.set_status(
                task_id, "FAILURE", message=error_msg, user_id=user_id,
            )
            return {"error": error_msg}

        tracker.set_status(
            task_id, "PROGRESS", progress=0.3,
            message="Re-generating DOCX from manifest...",
            user_id=user_id,
        )

        # Regenerate using GenerationService
        from sozo_generator.generation.service import GenerationService

        service = GenerationService()
        results = service.generate(
            condition=manifest_data["condition_slug"],
            tier=manifest_data.get("tier", "both"),
            doc_type=manifest_data.get("doc_type", "all"),
        )

        success_results = [r for r in results if r.success]
        if not success_results:
            error_msg = "DOCX regeneration produced no successful outputs"
            tracker.set_status(
                task_id, "FAILURE", message=error_msg, user_id=user_id,
            )
            return {"error": error_msg}

        primary = success_results[0]
        output = {
            "protocol_version_id": protocol_version_id,
            "docx_path": primary.output_path,
            "build_id": primary.build_id,
            "source": "regenerated",
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

        tracker.set_status(
            task_id, "SUCCESS", progress=1.0,
            message=f"DOCX regenerated: {primary.output_path}",
            metadata=output,
            user_id=user_id,
        )
        _audit_event("export_docx.completed", {
            "task_id": task_id,
            "protocol_version_id": protocol_version_id,
            "docx_path": primary.output_path,
            "user_id": user_id,
        })

        return output

    except SoftTimeLimitExceeded:
        tracker.set_status(
            task_id, "FAILURE",
            message="DOCX export exceeded time limit",
            user_id=user_id,
        )
        raise

    except Exception as exc:
        logger.exception("export_protocol_docx failed")
        tracker.set_status(
            task_id, "FAILURE",
            message=f"DOCX export failed: {exc}",
            user_id=user_id,
        )
        _audit_event("export_docx.failed", {
            "task_id": task_id, "error": str(exc), "user_id": user_id,
        })
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    name="sozo_workers.tasks.export_tasks.generate_visuals",
    max_retries=2,
    default_retry_delay=30,
    acks_late=True,
    queue="sozo_default",
)
def generate_visuals(
    self,
    protocol_version_id: str,
    visual_types: Optional[list[str]] = None,
    user_id: str = "",
) -> dict:
    """Batch visual generation for a protocol version.

    Generates one or more visual types (brain maps, EEG topomaps, network
    diagrams, etc.) for the condition associated with a protocol version.

    Args:
        protocol_version_id: Build ID to identify the condition.
        visual_types: List of visual type slugs to generate. If None, generates all
                      available types.
        user_id: Requesting user.

    Returns:
        Dict with generated visual paths and any errors.
    """
    task_id = self.request.id
    tracker = _get_tracker()

    tracker.set_status(
        task_id, "STARTED", progress=0.0,
        message=f"Starting visual generation for: {protocol_version_id}",
        user_id=user_id,
    )
    _audit_event("generate_visuals.started", {
        "task_id": task_id,
        "protocol_version_id": protocol_version_id,
        "visual_types": visual_types,
        "user_id": user_id,
    })

    try:
        # Resolve condition from protocol version
        import json
        from sozo_generator.core.settings import get_settings

        settings = get_settings()
        condition_slug = None

        # Try to find condition from manifest
        manifests_dir = settings.manifests_dir
        if manifests_dir.exists():
            for manifest_file in manifests_dir.rglob("*_manifest.json"):
                try:
                    data = json.loads(manifest_file.read_text())
                    if data.get("build_id") == protocol_version_id:
                        condition_slug = data["condition_slug"]
                        break
                except (json.JSONDecodeError, OSError, KeyError):
                    continue

        # Fallback: try extracting from the build ID pattern
        if condition_slug is None:
            # Check if protocol_version_id is itself a condition slug
            from sozo_generator.conditions.registry import get_registry
            registry = get_registry()
            if registry.exists(protocol_version_id):
                condition_slug = protocol_version_id

        if condition_slug is None:
            error_msg = f"Cannot resolve condition for protocol version: {protocol_version_id}"
            tracker.set_status(
                task_id, "FAILURE", message=error_msg, user_id=user_id,
            )
            return {"error": error_msg}

        tracker.set_status(
            task_id, "PROGRESS", progress=0.1,
            message=f"Resolved condition: {condition_slug}, loading generators...",
            user_id=user_id,
        )

        # Load condition schema
        from sozo_generator.conditions.registry import get_registry
        registry = get_registry()
        schema = registry.get(condition_slug)

        # Get available generators
        from sozo_generator.generation.service import GenerationService
        generators = GenerationService._get_visual_generators()

        # Filter to requested types
        if visual_types:
            generators = {k: v for k, v in generators.items() if k in visual_types}

        if not generators:
            error_msg = f"No matching visual generators found for types: {visual_types}"
            tracker.set_status(
                task_id, "FAILURE", message=error_msg, user_id=user_id,
            )
            return {"error": error_msg}

        # Generate visuals
        visuals_dir = settings.visuals_dir / condition_slug
        visuals_dir.mkdir(parents=True, exist_ok=True)

        generated: list[str] = []
        errors: list[str] = []
        total_generators = len(generators)

        for idx, (vtype, gen_func) in enumerate(generators.items()):
            progress = 0.1 + (0.8 * idx / total_generators)
            tracker.set_status(
                task_id, "PROGRESS", progress=progress,
                message=f"Generating {vtype} ({idx + 1}/{total_generators})...",
                user_id=user_id,
            )

            try:
                result = gen_func(schema, str(visuals_dir))
                if result:
                    if isinstance(result, list):
                        generated.extend(str(p) for p in result)
                    else:
                        generated.append(str(result))
                    logger.info("Visual generated: %s -> %s", vtype, result)
            except Exception as e:
                error_msg = f"{vtype}: {e}"
                errors.append(error_msg)
                logger.warning("Visual generation failed: %s", error_msg)

        output = {
            "protocol_version_id": protocol_version_id,
            "condition_slug": condition_slug,
            "requested_types": visual_types or list(generators.keys()),
            "generated": generated,
            "generated_count": len(generated),
            "errors": errors,
            "visuals_dir": str(visuals_dir),
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

        tracker.set_status(
            task_id, "SUCCESS", progress=1.0,
            message=f"Visual generation complete: {len(generated)} visuals, {len(errors)} errors",
            metadata=output,
            user_id=user_id,
        )
        _audit_event("generate_visuals.completed", {
            "task_id": task_id,
            "condition_slug": condition_slug,
            "generated_count": len(generated),
            "error_count": len(errors),
            "user_id": user_id,
        })

        return output

    except SoftTimeLimitExceeded:
        tracker.set_status(
            task_id, "FAILURE",
            message="Visual generation exceeded time limit",
            user_id=user_id,
        )
        raise

    except Exception as exc:
        logger.exception("generate_visuals failed")
        tracker.set_status(
            task_id, "FAILURE",
            message=f"Visual generation failed: {exc}",
            user_id=user_id,
        )
        _audit_event("generate_visuals.failed", {
            "task_id": task_id, "error": str(exc), "user_id": user_id,
        })
        raise self.retry(exc=exc)
