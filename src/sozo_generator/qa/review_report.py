"""
SOZO QA — Master review report generator.
Aggregates all QA checks into a comprehensive report.
"""
import logging
from datetime import datetime, timezone
from pathlib import Path

from ..schemas.condition import ConditionSchema
from ..schemas.review import ConditionQAReport, DocumentQAResult, ReviewItem
from ..core.enums import ReviewFlag
from ..conditions.registry import get_registry
from .completeness import CompletenessChecker
from .template_conformity import TemplateConformityChecker
from .evidence_coverage import EvidenceCoverageChecker
from .citation_check import CitationChecker

logger = logging.getLogger(__name__)

_PASS_ICON = "✅ PASS"
_FAIL_ICON = "❌ FAIL"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class QAReportGenerator:
    """Aggregates all QA sub-checks into a comprehensive ConditionQAReport."""

    def __init__(self) -> None:
        self._completeness = CompletenessChecker()
        self._conformity = TemplateConformityChecker()
        self._evidence = EvidenceCoverageChecker()
        self._citations = CitationChecker()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_report(
        self, condition_slug: str, output_dir: Path
    ) -> ConditionQAReport:
        """
        Run all QA checks for one condition and return a ConditionQAReport.
        """
        # 1. Load condition from registry (graceful fallback if not found)
        condition: ConditionSchema | None = None
        condition_name = condition_slug
        try:
            registry = get_registry()
            raw = registry.get(condition_slug)
            condition = ConditionSchema(**raw)
            condition_name = condition.display_name
        except Exception as exc:
            logger.warning(
                "QA report: could not load condition '%s' from registry — %s",
                condition_slug,
                exc,
            )

        # 2. Completeness check
        completeness_result = self._completeness.check_condition(
            condition_slug, output_dir
        )

        # 3. Template conformity check
        conformity_results = self._conformity.check_condition_documents(
            condition_slug, output_dir
        )

        # 4. Evidence coverage check (needs ConditionSchema)
        evidence_result: dict = {}
        if condition is not None:
            evidence_result = self._evidence.check_condition(condition)
        else:
            evidence_result = {
                "condition": condition_slug,
                "has_references": False,
                "reference_count": 0,
                "has_real_pmids": False,
                "has_protocols": False,
                "protocol_count": 0,
                "has_networks": False,
                "has_phenotypes": False,
                "evidence_gaps": [],
                "confidence_score": 0.0,
                "passed": False,
            }

        # 5. Citation check (needs ConditionSchema)
        citation_result: dict = {}
        if condition is not None:
            citation_result = self._citations.check_condition_citations(condition)
        else:
            citation_result = {
                "condition": condition_slug,
                "total_citations": 0,
                "valid_pmid_format": 0,
                "has_doi_format": 0,
                "placeholder_citations": 0,
                "duplicate_pmids": [],
                "issues": ["Condition could not be loaded from registry."],
                "passed": False,
            }

        # 6. Build DocumentQAResult list from conformity results
        document_results: list[DocumentQAResult] = []
        for conf in conformity_results:
            # Parse doc_type and tier from file path stem
            file_stem = Path(conf["file"]).stem
            doc_type, tier = _parse_doc_type_tier(file_stem, condition_slug)

            missing_sections = conf.get("required_sections_missing", [])
            review_items: list[ReviewItem] = []
            if missing_sections:
                for sec in missing_sections:
                    review_items.append(
                        ReviewItem(
                            flag=ReviewFlag.MISSING_SECTION,
                            location=sec,
                            description=f"Required section '{sec}' not found in document.",
                            severity="warning",
                        )
                    )

            paragraph_count = conf.get("paragraph_count", 0)
            completeness_score = (
                len(conf.get("required_sections_found", []))
                / max(
                    len(conf.get("required_sections_found", []))
                    + len(missing_sections),
                    1,
                )
            )

            doc_result = DocumentQAResult(
                document_type=doc_type,
                tier=tier,
                condition_slug=condition_slug,
                completeness_score=round(completeness_score, 4),
                evidence_coverage=evidence_result.get("confidence_score", 0.0),
                has_placeholders=citation_result.get("placeholder_citations", 0) > 0,
                missing_sections=missing_sections,
                review_items=review_items,
                passed=conf.get("passed", False),
                notes=[
                    f"Paragraph count: {paragraph_count}",
                    f"Has tables: {conf.get('has_tables', False)}",
                ],
            )
            document_results.append(doc_result)

        # 7. Aggregate metrics
        total_docs = len(document_results)
        passed_docs = sum(1 for d in document_results if d.passed)

        overall_completeness = (
            completeness_result["total_found"] / max(completeness_result["total_expected"], 1)
        )

        # 8. Build unresolved flags (issues that need human attention)
        unresolved_flags: list[ReviewItem] = []

        for issue in citation_result.get("issues", []):
            unresolved_flags.append(
                ReviewItem(
                    flag=ReviewFlag.MISSING_PRIMARY_SOURCE,
                    location="references",
                    description=issue,
                    severity="warning",
                )
            )

        if citation_result.get("placeholder_citations", 0) > 0:
            unresolved_flags.append(
                ReviewItem(
                    flag=ReviewFlag.PLACEHOLDER_TEXT,
                    location="references",
                    description=(
                        f"{citation_result['placeholder_citations']} placeholder citation(s) detected."
                    ),
                    severity="error",
                )
            )

        for missing_file in completeness_result.get("missing", []):
            unresolved_flags.append(
                ReviewItem(
                    flag=ReviewFlag.MISSING_SECTION,
                    location=missing_file,
                    description=f"Expected output file is missing: {missing_file}",
                    severity="error",
                )
            )

        # 9. Recommendations
        recommendations: list[str] = []
        if not evidence_result.get("has_references"):
            recommendations.append("Add peer-reviewed references with valid PMIDs.")
        if not evidence_result.get("has_protocols"):
            recommendations.append("Define at least one stimulation protocol.")
        if not evidence_result.get("has_networks"):
            recommendations.append("Add network dysfunction profiles.")
        if not evidence_result.get("has_phenotypes"):
            recommendations.append("Define at least one clinical phenotype subtype.")
        if completeness_result.get("small_files"):
            recommendations.append(
                f"Expand content in small files: {completeness_result['small_files']}"
            )

        # 10. Overall readiness
        ready = (
            completeness_result["passed"]
            and evidence_result.get("passed", False)
            and citation_result.get("passed", False)
            and passed_docs == total_docs
        )

        return ConditionQAReport(
            condition_slug=condition_slug,
            condition_name=condition_name,
            generated_at=_now_iso(),
            total_documents=total_docs,
            passed_documents=passed_docs,
            overall_completeness=round(overall_completeness, 4),
            overall_evidence_coverage=evidence_result.get("confidence_score", 0.0),
            document_results=document_results,
            unresolved_flags=unresolved_flags,
            evidence_gaps=evidence_result.get("evidence_gaps", []),
            recommendations=recommendations,
            ready_for_clinical_review=ready,
        )

    def generate_all_reports(self, output_dir: Path) -> list[ConditionQAReport]:
        """Generate QA reports for every condition found in output_dir."""
        completeness_checker = CompletenessChecker()
        all_completeness = completeness_checker.check_all(output_dir)

        reports: list[ConditionQAReport] = []
        for slug in sorted(all_completeness.keys()):
            try:
                report = self.generate_report(slug, output_dir)
                reports.append(report)
            except Exception as exc:
                logger.warning(
                    "QA report: failed to generate report for '%s' — %s", slug, exc
                )

        return reports

    def write_json_report(
        self, report: ConditionQAReport, output_path: Path
    ) -> None:
        """Serialise report to JSON."""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                report.model_dump_json(indent=2), encoding="utf-8"
            )
            logger.info("QA JSON report written to %s", output_path)
        except Exception as exc:
            logger.warning(
                "QA report: failed to write JSON report to %s — %s",
                output_path,
                exc,
            )

    def write_markdown_report(
        self, report: ConditionQAReport, output_path: Path
    ) -> None:
        """Write a human-readable Markdown QA report."""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            md = _build_markdown_report(report)
            output_path.write_text(md, encoding="utf-8")
            logger.info("QA Markdown report written to %s", output_path)
        except Exception as exc:
            logger.warning(
                "QA report: failed to write Markdown report to %s — %s",
                output_path,
                exc,
            )

    def generate_overall_summary(
        self, reports: list[ConditionQAReport]
    ) -> str:
        """Return a Markdown summary table for all conditions."""
        if not reports:
            return "No QA reports available.\n"

        lines: list[str] = [
            "# SOZO QA — Overall Summary",
            f"Generated: {_now_iso()}",
            "",
            f"Total conditions: **{len(reports)}**",
            "",
            "| Condition | Completeness | Evidence | Citations | Documents | Ready |",
            "|-----------|-------------|----------|-----------|-----------|-------|",
        ]

        for r in reports:
            completeness_pct = f"{r.overall_completeness * 100:.0f}%"
            evidence_pct = f"{r.overall_evidence_coverage * 100:.0f}%"
            docs_str = f"{r.passed_documents}/{r.total_documents}"
            ready_icon = _PASS_ICON if r.ready_for_clinical_review else _FAIL_ICON
            lines.append(
                f"| {r.condition_name} | {completeness_pct} | {evidence_pct} "
                f"| — | {docs_str} | {ready_icon} |"
            )

        lines.append("")
        return "\n".join(lines)


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _parse_doc_type_tier(file_stem: str, condition_slug: str) -> tuple[str, str]:
    """
    Extract doc_type and tier from a filename stem like
    ``{condition_slug}_{doc_type}_{tier}``.
    Returns ("unknown", "unknown") if parsing fails.
    """
    from ..core.enums import Tier, DocumentType

    known_tiers = {t.value for t in Tier}
    known_doc_types = {dt.value for dt in DocumentType}

    prefix = condition_slug + "_"
    if file_stem.startswith(prefix):
        remainder = file_stem[len(prefix):]
    else:
        remainder = file_stem

    # Try to split off the tier from the end
    for tier_val in known_tiers:
        if remainder.endswith("_" + tier_val):
            potential_doc_type = remainder[: -(len(tier_val) + 1)]
            if potential_doc_type in known_doc_types:
                return potential_doc_type, tier_val

    return "unknown", "unknown"


def _build_markdown_report(report: ConditionQAReport) -> str:
    """Build a full Markdown QA report for a single condition."""
    # --- Compute per-section pass/fail for the summary table ---
    # Completeness
    completeness_passed = report.overall_completeness >= 1.0
    completeness_score_str = (
        f"{report.passed_documents}/{report.total_documents}"
    )

    # Template conformity
    conformity_passed = all(d.passed for d in report.document_results)
    conformity_passed_count = sum(1 for d in report.document_results if d.passed)
    conformity_score_str = f"{conformity_passed_count}/{len(report.document_results)}"

    # Evidence
    evidence_passed = report.overall_evidence_coverage >= 0.6
    evidence_score_str = f"{report.overall_evidence_coverage * 100:.1f}%"

    # Citations — derive from unresolved flags tagged as placeholder/missing
    citation_issues = [
        f for f in report.unresolved_flags
        if f.flag in (ReviewFlag.MISSING_PRIMARY_SOURCE, ReviewFlag.PLACEHOLDER_TEXT)
        and f.location == "references"
    ]
    citation_passed = len(citation_issues) == 0
    # Count valid PMIDs from notes is not available here; use generic label
    citation_score_str = "see issues" if citation_issues else "ok"

    # --- Issues list ---
    issue_lines: list[str] = []
    for flag in report.unresolved_flags:
        sev_label = flag.severity.upper()
        issue_lines.append(
            f"- **[{sev_label}]** `{flag.location}` — {flag.description}"
        )
    if not issue_lines:
        issue_lines = ["- No issues flagged."]

    # --- Document table ---
    doc_rows: list[str] = []
    for d in report.document_results:
        status = _PASS_ICON if d.passed else _FAIL_ICON
        missing = ", ".join(d.missing_sections) if d.missing_sections else "—"
        doc_rows.append(
            f"| {d.document_type} | {d.tier} | {status} "
            f"| {d.completeness_score:.0%} | {missing} |"
        )

    # --- Evidence gaps ---
    gap_lines = (
        [f"- {g}" for g in report.evidence_gaps]
        if report.evidence_gaps
        else ["- None identified."]
    )

    # --- Recommendations ---
    rec_lines = (
        [f"- {r}" for r in report.recommendations]
        if report.recommendations
        else ["- None."]
    )

    overall_status = _PASS_ICON if report.ready_for_clinical_review else _FAIL_ICON

    lines: list[str] = [
        f"# SOZO QA Report — {report.condition_name}",
        f"Generated: {report.generated_at}",
        "",
        f"**Condition slug:** `{report.condition_slug}`  ",
        f"**Overall status:** {overall_status}",
        "",
        "## Summary",
        "",
        "| Check | Status | Score |",
        "|-------|--------|-------|",
        f"| Document Completeness | {_PASS_ICON if completeness_passed else _FAIL_ICON} | {completeness_score_str} |",
        f"| Template Conformity | {_PASS_ICON if conformity_passed else _FAIL_ICON} | {conformity_score_str} |",
        f"| Evidence Coverage | {_PASS_ICON if evidence_passed else _FAIL_ICON} | {evidence_score_str} |",
        f"| Citation Validity | {_PASS_ICON if citation_passed else _FAIL_ICON} | {citation_score_str} |",
        "",
        "## Issues Requiring Human Review",
        "",
        *issue_lines,
        "",
        "## Document Results",
        "",
        "| Document Type | Tier | Status | Completeness | Missing Sections |",
        "|---------------|------|--------|-------------|-----------------|",
        *doc_rows,
        "",
        "## Evidence Gaps",
        "",
        *gap_lines,
        "",
        "## Recommendations",
        "",
        *rec_lines,
        "",
    ]

    return "\n".join(lines)
