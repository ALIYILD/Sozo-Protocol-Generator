"""Protocol generation tasks — single, batch, and personalization."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded

from sozo_workers.status import TaskStatusTracker

logger = logging.getLogger(__name__)

# Shared tracker instance (lazy connection)
_tracker: Optional[TaskStatusTracker] = None


def _get_tracker() -> TaskStatusTracker:
    global _tracker
    if _tracker is None:
        _tracker = TaskStatusTracker()
    return _tracker


def _audit_event(event_type: str, data: dict) -> None:
    """Write an audit event to the log. In production this would go to a DB/stream."""
    logger.info(
        "AUDIT event=%s ts=%s data=%s",
        event_type,
        datetime.now(timezone.utc).isoformat(),
        data,
    )


@shared_task(
    bind=True,
    name="sozo_workers.tasks.protocol_tasks.generate_protocol",
    max_retries=2,
    default_retry_delay=30,
    acks_late=True,
    queue="sozo_default",
)
def generate_protocol(
    self,
    condition_slug: str,
    modality: str = "all",
    tier: str = "both",
    doc_type: str = "all",
    user_id: str = "",
    options: Optional[dict[str, Any]] = None,
) -> dict:
    """Run the full GenerationService pipeline for a single condition.

    Args:
        condition_slug: Target condition (e.g. "parkinsons").
        modality: Modality filter (reserved for future use).
        tier: "fellow", "partners", or "both".
        doc_type: Document type slug or "all".
        user_id: ID of the requesting user.
        options: Extra generation options (with_visuals, with_qa, output_dir, etc.).

    Returns:
        Dict with build results, output paths, and QA summary.
    """
    task_id = self.request.id
    tracker = _get_tracker()
    options = options or {}

    tracker.set_status(
        task_id, "STARTED", progress=0.0,
        message=f"Starting protocol generation: {condition_slug}/{tier}/{doc_type}",
        user_id=user_id,
    )
    _audit_event("protocol_generation.started", {
        "task_id": task_id,
        "condition_slug": condition_slug,
        "tier": tier,
        "doc_type": doc_type,
        "user_id": user_id,
    })

    try:
        from sozo_generator.generation.service import GenerationService

        service = GenerationService(
            output_dir=options.get("output_dir"),
            with_visuals=options.get("with_visuals", True),
            with_qa=options.get("with_qa", True),
            with_images=options.get("with_images", False),
            with_pdf=options.get("with_pdf", False),
        )

        tracker.set_status(
            task_id, "PROGRESS", progress=0.1,
            message="GenerationService initialized, starting generation...",
            user_id=user_id,
        )

        results = service.generate(
            condition=condition_slug,
            tier=tier,
            doc_type=doc_type,
            with_visuals=options.get("with_visuals"),
            with_qa=options.get("with_qa"),
            output_dir=options.get("output_dir"),
        )

        tracker.set_status(
            task_id, "PROGRESS", progress=0.9,
            message=f"Generation complete, processing {len(results)} results...",
            user_id=user_id,
        )

        # Serialize results
        output = {
            "condition_slug": condition_slug,
            "tier": tier,
            "doc_type": doc_type,
            "total": len(results),
            "succeeded": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "results": [],
        }

        for r in results:
            output["results"].append({
                "condition_slug": r.condition_slug,
                "tier": r.tier,
                "doc_type": r.doc_type,
                "success": r.success,
                "output_path": r.output_path,
                "qa_passed": r.qa_passed,
                "qa_issues": r.qa_issues[:10],
                "visuals_generated": r.visuals_generated,
                "images_inserted": r.images_inserted,
                "pdf_path": r.pdf_path,
                "error": r.error,
                "build_id": r.build_id,
            })

        tracker.set_status(
            task_id, "SUCCESS", progress=1.0,
            message=f"Generated {output['succeeded']}/{output['total']} documents",
            metadata=output,
            user_id=user_id,
        )
        _audit_event("protocol_generation.completed", {
            "task_id": task_id,
            "condition_slug": condition_slug,
            "succeeded": output["succeeded"],
            "failed": output["failed"],
            "user_id": user_id,
        })

        return output

    except SoftTimeLimitExceeded:
        tracker.set_status(
            task_id, "FAILURE", progress=0.0,
            message="Task exceeded soft time limit (9 minutes)",
            user_id=user_id,
        )
        _audit_event("protocol_generation.timeout", {
            "task_id": task_id,
            "condition_slug": condition_slug,
            "user_id": user_id,
        })
        raise

    except Exception as exc:
        logger.exception("generate_protocol failed for %s", condition_slug)
        tracker.set_status(
            task_id, "FAILURE", progress=0.0,
            message=f"Generation failed: {exc}",
            user_id=user_id,
        )
        _audit_event("protocol_generation.failed", {
            "task_id": task_id,
            "condition_slug": condition_slug,
            "error": str(exc),
            "user_id": user_id,
        })
        # Retry on transient errors
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    name="sozo_workers.tasks.protocol_tasks.generate_batch",
    max_retries=1,
    default_retry_delay=60,
    acks_late=True,
    queue="sozo_default",
    time_limit=3600,  # 1 hour for batch
    soft_time_limit=3300,
)
def generate_batch(
    self,
    condition_slugs: Optional[list[str]] = None,
    tier: str = "both",
    user_id: str = "",
) -> dict:
    """Batch generation across multiple conditions.

    If condition_slugs is None, generates for all 15 conditions in the registry.

    Returns:
        Summary dict with per-condition results.
    """
    task_id = self.request.id
    tracker = _get_tracker()

    tracker.set_status(
        task_id, "STARTED", progress=0.0,
        message="Starting batch generation...",
        user_id=user_id,
    )
    _audit_event("batch_generation.started", {
        "task_id": task_id,
        "condition_slugs": condition_slugs,
        "tier": tier,
        "user_id": user_id,
    })

    try:
        from sozo_generator.generation.service import GenerationService

        service = GenerationService()

        # Resolve condition list
        if condition_slugs is None:
            condition_slugs = service.list_conditions()

        total_conditions = len(condition_slugs)
        all_output: list[dict] = []
        total_success = 0
        total_fail = 0

        for idx, slug in enumerate(condition_slugs):
            progress = idx / total_conditions
            tracker.set_status(
                task_id, "PROGRESS", progress=progress,
                message=f"Generating {slug} ({idx + 1}/{total_conditions})",
                user_id=user_id,
            )

            try:
                results = service.generate(condition=slug, tier=tier, doc_type="all")
                success_count = sum(1 for r in results if r.success)
                fail_count = sum(1 for r in results if not r.success)
                total_success += success_count
                total_fail += fail_count

                all_output.append({
                    "condition_slug": slug,
                    "succeeded": success_count,
                    "failed": fail_count,
                    "build_ids": [r.build_id for r in results if r.success],
                    "errors": [r.error for r in results if r.error],
                })
            except Exception as e:
                logger.error("Batch: condition %s failed: %s", slug, e)
                total_fail += 1
                all_output.append({
                    "condition_slug": slug,
                    "succeeded": 0,
                    "failed": 1,
                    "build_ids": [],
                    "errors": [str(e)],
                })

        output = {
            "total_conditions": total_conditions,
            "total_succeeded": total_success,
            "total_failed": total_fail,
            "tier": tier,
            "per_condition": all_output,
        }

        tracker.set_status(
            task_id, "SUCCESS", progress=1.0,
            message=f"Batch complete: {total_success} succeeded, {total_fail} failed across {total_conditions} conditions",
            metadata=output,
            user_id=user_id,
        )
        _audit_event("batch_generation.completed", {
            "task_id": task_id,
            "total_conditions": total_conditions,
            "total_succeeded": total_success,
            "total_failed": total_fail,
            "user_id": user_id,
        })

        return output

    except SoftTimeLimitExceeded:
        tracker.set_status(
            task_id, "FAILURE",
            message="Batch generation exceeded time limit",
            user_id=user_id,
        )
        _audit_event("batch_generation.timeout", {"task_id": task_id, "user_id": user_id})
        raise

    except Exception as exc:
        logger.exception("generate_batch failed")
        tracker.set_status(
            task_id, "FAILURE",
            message=f"Batch generation failed: {exc}",
            user_id=user_id,
        )
        _audit_event("batch_generation.failed", {
            "task_id": task_id, "error": str(exc), "user_id": user_id,
        })
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    name="sozo_workers.tasks.protocol_tasks.personalize_protocol",
    max_retries=2,
    default_retry_delay=30,
    acks_late=True,
    queue="sozo_default",
)
def personalize_protocol(
    self,
    protocol_id: str,
    patient_id: str,
    user_id: str = "",
) -> dict:
    """V2: Run personalization engine on a generated protocol.

    Takes a base protocol and adapts it to patient-specific parameters
    (phenotype, comorbidities, medication profile, qEEG signature).

    This is a forward-looking task — the personalization engine is under
    active development. Currently returns a stub indicating the feature
    is not yet available.

    Args:
        protocol_id: ID of the base protocol version to personalize.
        patient_id: Patient record ID for phenotype/comorbidity lookup.
        user_id: Requesting user.

    Returns:
        Dict with personalized protocol metadata.
    """
    task_id = self.request.id
    tracker = _get_tracker()

    tracker.set_status(
        task_id, "STARTED", progress=0.0,
        message=f"Starting personalization: protocol={protocol_id}, patient={patient_id}",
        user_id=user_id,
    )
    _audit_event("personalization.started", {
        "task_id": task_id,
        "protocol_id": protocol_id,
        "patient_id": patient_id,
        "user_id": user_id,
    })

    try:
        # V2 stub — replace with actual personalization engine when ready
        # Expected integration points:
        #   from sozo_generator.personalization.engine import PersonalizationEngine
        #   engine = PersonalizationEngine()
        #   result = engine.personalize(protocol_id, patient_id)

        tracker.set_status(
            task_id, "PROGRESS", progress=0.5,
            message="Personalization engine executing...",
            user_id=user_id,
        )

        personalized_id = f"pers-{uuid.uuid4().hex[:8]}"

        output = {
            "protocol_id": protocol_id,
            "patient_id": patient_id,
            "personalized_id": personalized_id,
            "status": "stub",
            "message": "Personalization engine V2 — not yet implemented. "
                       "Protocol returned unmodified.",
            "adaptations_applied": [],
        }

        tracker.set_status(
            task_id, "SUCCESS", progress=1.0,
            message="Personalization complete (V2 stub)",
            metadata=output,
            user_id=user_id,
        )
        _audit_event("personalization.completed", {
            "task_id": task_id,
            "personalized_id": personalized_id,
            "user_id": user_id,
        })

        return output

    except Exception as exc:
        logger.exception("personalize_protocol failed")
        tracker.set_status(
            task_id, "FAILURE",
            message=f"Personalization failed: {exc}",
            user_id=user_id,
        )
        _audit_event("personalization.failed", {
            "task_id": task_id, "error": str(exc), "user_id": user_id,
        })
        raise self.retry(exc=exc)
