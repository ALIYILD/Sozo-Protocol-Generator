"""Harness adapter for GenerationService (canonical / document pipeline)."""
from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional

from ..normalize import document_spec_to_benchmark_markdown, docx_to_benchmark_markdown
from ..schemas import BenchmarkCase, HarnessMetadata, HarnessResult
from .base_harness import AgentHarness


def _normalize_tier(raw: Any) -> str:
    s = (str(raw) if raw is not None else "fellow").strip().lower()
    if s in ("partner", "partners"):
        return "partners"
    if s in ("fellow", "fellows"):
        return "fellow"
    if s == "both":
        return "both"
    return s or "fellow"


def _normalize_doc_type(raw: Any) -> str:
    d = (str(raw) if raw is not None else "evidence_based_protocol").strip()
    return d or "evidence_based_protocol"


def _render_generation_failure_markdown(
    *,
    case: BenchmarkCase,
    error: str | None,
    qa_issues: list[str],
) -> str:
    lines = [
        "# Generation failed",
        "",
        "_AutoAgent-Clinical harness output — internal QA only, not a clinical record._",
        "",
        f"- **Case:** `{case.id}`",
        f"- **Harness:** `generation_service`",
    ]
    if error:
        lines.append(f"- **Error:** {error}")
    if qa_issues:
        lines.append("- **QA / pipeline notes:**")
        lines.extend(f"  - {i}" for i in qa_issues)
    return "\n".join(lines)


class GenerationServiceHarness(AgentHarness):
    """Runs SOZO generation and feeds benchmark validators.

    When ``benchmark_text_source`` is ``auto`` (default) and the service is a real
    :class:`~sozo_generator.generation.service.GenerationService` on a canonical
    route, uses :meth:`~sozo_generator.generation.service.GenerationService.assemble_canonical_document`
    to capture :class:`~sozo_generator.schemas.documents.DocumentSpec` **before** DOCX
    render and converts it to markdown. Otherwise falls back to ``generate()`` +
    DOCX extraction (``MagicMock`` services always use the legacy path).

    Opt-in text sources via ``case.inputs['benchmark_text_source']``:

    - ``auto`` — structured first, then DOCX pipeline
    - ``docx_only`` — always ``generate()`` + DOCX (Phase 2 behavior)
    - ``structured_only`` — assemble only; no DOCX fallback
    """

    def __init__(
        self,
        service_factory: Optional[Callable[[], Any]] = None,
    ) -> None:
        self._service_factory = service_factory

    @property
    def harness_id(self) -> str:
        return "generation_service"

    def _build_service(self) -> Any:
        if self._service_factory is not None:
            return self._service_factory()
        from sozo_generator.generation.service import GenerationService

        return GenerationService(
            with_visuals=False,
            with_qa=False,
            with_images=False,
            with_pdf=False,
        )

    def _result_from_structured_spec(
        self,
        case: BenchmarkCase,
        *,
        condition: str,
        tier: str,
        doc_type: str,
        spec: Any,
        provenance: Any,
        safety_qa: list[str],
        notes: list[str],
    ) -> HarnessResult:
        md = document_spec_to_benchmark_markdown(spec)
        qa = list(safety_qa)
        if provenance is not None:
            qa.extend(getattr(provenance, "warnings", []) or [])

        spec_dict = spec.model_dump(mode="json")
        prov_dict = provenance.to_dict() if provenance is not None else None

        header = (
            "<!-- AutoAgent-Clinical: generation_service — for internal QA only -->\n\n"
            "<!-- structured_source:document_spec -->\n\n"
        )
        body = md.strip()
        if qa:
            body += "\n\n## Pipeline warnings\n\n" + "\n".join(f"- {i}" for i in qa[:50])

        notes = notes + [
            f"condition={condition}",
            f"tier={tier}",
            f"doc_type={doc_type}",
            "path=assemble_canonical_document",
        ]
        return HarnessResult(
            case_id=case.id,
            output_text=header + body,
            structured_protocol=None,
            document_spec=spec_dict,
            assembly_provenance=prov_dict,
            metadata=HarnessMetadata(
                harness_id=self.harness_id,
                notes=notes,
                structured_source="document_spec",
            ),
        )

    def run(self, case: BenchmarkCase) -> HarnessResult:
        notes: list[str] = []
        inp = dict(case.inputs)

        condition = inp.get("condition")
        if not condition:
            msg = "case.inputs['condition'] is required for generation_service harness"
            notes.append(msg)
            return HarnessResult(
                case_id=case.id,
                output_text=_render_generation_failure_markdown(
                    case=case, error=msg, qa_issues=[]
                ),
                structured_protocol=None,
                document_spec=None,
                assembly_provenance=None,
                metadata=HarnessMetadata(
                    harness_id=self.harness_id,
                    notes=notes,
                    structured_source="failure",
                ),
            )

        tier = _normalize_tier(inp.get("tier") or inp.get("audience"))
        doc_type = _normalize_doc_type(inp.get("doc_type"))
        output_dir = inp.get("generation_output_dir")

        text_source_raw = str(inp.get("benchmark_text_source", "auto")).lower()
        if text_source_raw not in ("auto", "docx_only", "structured_only"):
            text_source_raw = "auto"

        service = self._build_service()
        from sozo_generator.generation.service import GenerationService

        # ── Structured path (DocumentSpec before DOCX) ─────────────────────
        if isinstance(service, GenerationService) and text_source_raw != "docx_only":
            if service.can_route_canonical(str(condition), doc_type):
                assembled = service.assemble_canonical_document(
                    str(condition), doc_type, tier
                )
                if assembled.ok and assembled.spec is not None:
                    md = document_spec_to_benchmark_markdown(assembled.spec)
                    if md.strip():
                        return self._result_from_structured_spec(
                            case,
                            condition=str(condition),
                            tier=tier,
                            doc_type=doc_type,
                            spec=assembled.spec,
                            provenance=assembled.provenance,
                            safety_qa=assembled.safety_qa_issues,
                            notes=list(notes),
                        )
                    notes.append("Structured assembly returned empty markdown projection")
                elif text_source_raw == "structured_only":
                    err = assembled.error or "canonical assembly failed"
                    notes.append(err)
                    return HarnessResult(
                        case_id=case.id,
                        output_text=_render_generation_failure_markdown(
                            case=case, error=err, qa_issues=assembled.safety_qa_issues
                        ),
                        structured_protocol=None,
                        document_spec=None,
                        assembly_provenance=None,
                        metadata=HarnessMetadata(
                            harness_id=self.harness_id,
                            notes=notes,
                            structured_source="failure",
                        ),
                    )
            elif text_source_raw == "structured_only":
                msg = f"condition/doc_type not canonical-routable: {condition}/{doc_type}"
                notes.append(msg)
                return HarnessResult(
                    case_id=case.id,
                    output_text=_render_generation_failure_markdown(
                        case=case, error=msg, qa_issues=[]
                    ),
                    structured_protocol=None,
                    document_spec=None,
                    assembly_provenance=None,
                    metadata=HarnessMetadata(
                        harness_id=self.harness_id,
                        notes=notes,
                        structured_source="failure",
                    ),
                )

        # ── DOCX path (generate + extract) ────────────────────────────────
        try:
            results = service.generate(
                condition=str(condition),
                tier=tier,
                doc_type=doc_type,
                output_dir=output_dir,
                with_visuals=False,
                with_qa=False,
            )
        except Exception as exc:  # noqa: BLE001 — surface as benchmark signal
            err = str(exc)
            notes.append(f"generate() raised: {err}")
            return HarnessResult(
                case_id=case.id,
                output_text=_render_generation_failure_markdown(
                    case=case, error=err, qa_issues=[]
                ),
                structured_protocol=None,
                document_spec=None,
                assembly_provenance=None,
                metadata=HarnessMetadata(
                    harness_id=self.harness_id,
                    notes=notes,
                    structured_source="failure",
                ),
            )

        if not results:
            notes.append("Generation returned no results")
            return HarnessResult(
                case_id=case.id,
                output_text=_render_generation_failure_markdown(
                    case=case, error="empty results list", qa_issues=[]
                ),
                structured_protocol=None,
                document_spec=None,
                assembly_provenance=None,
                metadata=HarnessMetadata(
                    harness_id=self.harness_id,
                    notes=notes,
                    structured_source="failure",
                ),
            )

        result = results[0]
        doc_type_actual = getattr(result, "doc_type", doc_type)
        tier_actual = getattr(result, "tier", tier)

        if not result.success or not result.output_path:
            err = result.error or "generation failed without error string"
            notes.append(err)
            if result.qa_issues:
                notes.extend(result.qa_issues[:20])
            return HarnessResult(
                case_id=case.id,
                output_text=_render_generation_failure_markdown(
                    case=case,
                    error=err,
                    qa_issues=result.qa_issues or [],
                ),
                structured_protocol=None,
                document_spec=None,
                assembly_provenance=None,
                metadata=HarnessMetadata(
                    harness_id=self.harness_id,
                    notes=notes
                    + [
                        f"condition={condition}",
                        f"tier={tier_actual}",
                        f"doc_type={doc_type_actual}",
                        f"build_id={getattr(result, 'build_id', '')}",
                    ],
                    structured_source="failure",
                ),
            )

        docx_path = Path(result.output_path)
        try:
            markdown = docx_to_benchmark_markdown(docx_path)
        except Exception as exc:  # noqa: BLE001
            err = f"docx normalization failed: {exc}"
            notes.append(err)
            return HarnessResult(
                case_id=case.id,
                output_text=_render_generation_failure_markdown(
                    case=case, error=err, qa_issues=result.qa_issues or []
                ),
                structured_protocol=None,
                document_spec=None,
                assembly_provenance=None,
                metadata=HarnessMetadata(
                    harness_id=self.harness_id,
                    notes=notes,
                    structured_source="failure",
                ),
            )

        if not markdown.strip():
            notes.append("DOCX contained no extractable paragraph text")
            return HarnessResult(
                case_id=case.id,
                output_text=_render_generation_failure_markdown(
                    case=case,
                    error="empty markdown after DOCX extraction",
                    qa_issues=result.qa_issues or [],
                ),
                structured_protocol=None,
                document_spec=None,
                assembly_provenance=None,
                metadata=HarnessMetadata(
                    harness_id=self.harness_id,
                    notes=notes,
                    structured_source="failure",
                ),
            )

        prov_dict: Optional[dict[str, Any]] = None
        prov_path = docx_path.with_suffix(".provenance.json")
        if prov_path.is_file():
            try:
                prov_dict = json.loads(prov_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                notes.append("provenance sidecar present but not parsed")

        header = (
            "<!-- AutoAgent-Clinical: generation_service — for internal QA only -->\n\n"
            "<!-- structured_source:docx_extract -->\n\n"
            f"<!-- source_docx:{docx_path.name} build_id:{getattr(result, 'build_id', '')} -->\n\n"
        )

        if result.qa_issues:
            qblock = "\n\n## Pipeline warnings\n\n" + "\n".join(
                f"- {i}" for i in result.qa_issues[:50]
            )
            markdown = markdown + qblock

        notes.extend(
            [
                f"condition={condition}",
                f"tier={tier_actual}",
                f"doc_type={doc_type_actual}",
                f"output_path={docx_path}",
            ]
        )

        return HarnessResult(
            case_id=case.id,
            output_text=header + markdown.strip(),
            structured_protocol=None,
            document_spec=None,
            assembly_provenance=prov_dict,
            metadata=HarnessMetadata(
                harness_id=self.harness_id,
                notes=notes,
                structured_source="docx_extract",
            ),
        )
