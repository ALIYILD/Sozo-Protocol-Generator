"""
Review reports -- generates exportable artifacts for clinical audit:
approved-only bundles, flagged item reports, evidence gaps, stale evidence,
revision history, and section-level review summaries.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..review.manager import ReviewManager
from ..schemas.contracts import ReviewState, QAReport
from ..schemas.condition import ConditionSchema
from ..evidence.section_evidence_mapper import SectionEvidenceMapper, DocumentEvidenceProfile
from ..evidence.refresh import EvidenceRefresher, EvidenceRefreshResult
from ..orchestration.provenance import ProvenanceStore, DocumentProvenance

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class ReviewDashboardData:
    """Aggregated data for the review dashboard."""

    total_reviews: int = 0
    pending_count: int = 0
    approved_count: int = 0
    rejected_count: int = 0
    flagged_count: int = 0
    draft_count: int = 0
    exported_count: int = 0
    by_condition: dict[str, dict] = field(default_factory=dict)
    by_doc_type: dict[str, dict] = field(default_factory=dict)
    recent_decisions: list[dict] = field(default_factory=list)


@dataclass
class SectionReviewSummary:
    """Section-level review data for one section."""

    section_id: str = ""
    title: str = ""
    evidence_confidence: str = ""
    article_count: int = 0
    has_contradictions: bool = False
    is_outdated: bool = False
    is_weak: bool = False
    comments: list[dict] = field(default_factory=list)
    review_flags: list[str] = field(default_factory=list)
    needs_review: bool = False


class ReviewReporter:
    """Generates all review and audit reports."""

    def __init__(self, reviews_dir: Path, provenance_dir: Path = None):
        self.reviews_dir = Path(reviews_dir)
        self.manager = ReviewManager(self.reviews_dir)
        prov_dir = provenance_dir or (self.reviews_dir.parent / "provenance")
        if provenance_dir is not None or prov_dir.exists():
            self.provenance = ProvenanceStore(prov_dir)
        else:
            self.provenance = None

    def get_dashboard_data(self) -> ReviewDashboardData:
        """Aggregate all review data for dashboard display."""
        data = ReviewDashboardData()
        all_reviews = self.manager.list_all()
        data.total_reviews = len(all_reviews)

        status_counts = {
            "draft": 0,
            "needs_review": 0,
            "approved": 0,
            "rejected": 0,
            "flagged": 0,
            "exported": 0,
        }

        for review in all_reviews:
            status_val = review.status.value
            if status_val in status_counts:
                status_counts[status_val] += 1

            # Group by condition
            cond = review.condition_slug
            if cond not in data.by_condition:
                data.by_condition[cond] = {"total": 0, "approved": 0, "flagged": 0, "pending": 0}
            data.by_condition[cond]["total"] += 1
            if status_val == "approved":
                data.by_condition[cond]["approved"] += 1
            elif status_val == "flagged":
                data.by_condition[cond]["flagged"] += 1
            elif status_val == "needs_review":
                data.by_condition[cond]["pending"] += 1

            # Group by doc_type
            doc_type = review.document_type
            if doc_type not in data.by_doc_type:
                data.by_doc_type[doc_type] = {"total": 0, "approved": 0, "flagged": 0}
            data.by_doc_type[doc_type]["total"] += 1
            if status_val == "approved":
                data.by_doc_type[doc_type]["approved"] += 1
            elif status_val == "flagged":
                data.by_doc_type[doc_type]["flagged"] += 1

            # Collect recent decisions
            for decision in review.decisions:
                data.recent_decisions.append({
                    "build_id": review.build_id,
                    "condition": cond,
                    "document_type": doc_type,
                    "status": decision.status.value,
                    "reviewer": decision.reviewer,
                    "reason": decision.reason,
                    "decided_at": decision.decided_at,
                })

        data.draft_count = status_counts["draft"]
        data.pending_count = status_counts["needs_review"]
        data.approved_count = status_counts["approved"]
        data.rejected_count = status_counts["rejected"]
        data.flagged_count = status_counts["flagged"]
        data.exported_count = status_counts["exported"]

        # Sort recent decisions by timestamp descending
        data.recent_decisions.sort(key=lambda d: d.get("decided_at", ""), reverse=True)

        return data

    def generate_flagged_report(self) -> str:
        """Generate markdown report of all flagged documents."""
        flagged = self.manager.list_flagged()
        lines = [
            "# Flagged Documents Report",
            "",
            f"*Generated: {_now_iso()}*",
            "",
        ]

        if not flagged:
            lines.append("No documents are currently flagged.")
            return "\n".join(lines)

        lines.append(f"**Total flagged: {len(flagged)}**")
        lines.append("")

        for review in flagged:
            lines.append(f"## {review.build_id}")
            lines.append("")
            lines.append(f"- **Condition:** {review.condition_slug}")
            lines.append(f"- **Document type:** {review.document_type}")
            lines.append(f"- **Tier:** {review.tier}")
            lines.append(f"- **Version:** {review.version}")
            lines.append("")

            # Find the flagging decision
            flag_decisions = [
                d for d in review.decisions if d.status.value == "flagged"
            ]
            if flag_decisions:
                latest = flag_decisions[-1]
                lines.append(f"**Flagged by:** {latest.reviewer}")
                lines.append(f"**Reason:** {latest.reason}")
                lines.append(f"**Date:** {latest.decided_at}")
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def generate_evidence_gap_report(self, conditions: list[ConditionSchema]) -> str:
        """Generate markdown report of evidence gaps across conditions."""
        lines = [
            "# Evidence Gap Report",
            "",
            f"*Generated: {_now_iso()}*",
            "",
        ]

        if not conditions:
            lines.append("No conditions provided for analysis.")
            return "\n".join(lines)

        mapper = SectionEvidenceMapper()

        for condition in conditions:
            lines.append(f"## {condition.display_name} (`{condition.slug}`)")
            lines.append("")

            # Evidence gaps from condition schema
            gaps = condition.evidence_gaps or []
            if gaps:
                lines.append("### Declared Evidence Gaps")
                lines.append("")
                for gap in gaps:
                    lines.append(f"- {gap}")
                lines.append("")

            # Weak sections from evidence mapping
            items = mapper.build_evidence_items_from_condition(condition)
            weak_sections: list[str] = []
            if items:
                lines.append(f"### Evidence Summary")
                lines.append("")
                lines.append(f"- Total evidence items: {len(items)}")
                # Count items without year or with low evidence level
                low_evidence = [i for i in items if i.evidence_level.value in ("low", "very_low", "missing")]
                if low_evidence:
                    lines.append(f"- Low/very low evidence items: {len(low_evidence)}")
                lines.append("")
            else:
                lines.append("- **No evidence items found**")
                lines.append("")

            # Overall evidence quality
            lines.append(f"- Overall evidence quality: {condition.overall_evidence_quality.value}")
            lines.append("")

            # Review flags
            if condition.review_flags:
                lines.append("### Review Flags")
                lines.append("")
                for flag in condition.review_flags:
                    lines.append(f"- {flag}")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def generate_stale_evidence_report(
        self, conditions: list[ConditionSchema], recency_years: int = 5,
    ) -> str:
        """Generate markdown report of stale evidence per condition."""
        lines = [
            "# Stale Evidence Report",
            "",
            f"*Generated: {_now_iso()}*",
            f"*Recency window: {recency_years} years*",
            "",
        ]

        if not conditions:
            lines.append("No conditions provided for analysis.")
            return "\n".join(lines)

        refresher = EvidenceRefresher(recency_years=recency_years)

        for condition in conditions:
            lines.append(f"## {condition.display_name} (`{condition.slug}`)")
            lines.append("")

            try:
                result = refresher.assess_staleness(condition)
            except Exception as exc:
                lines.append(f"*Could not assess staleness: {exc}*")
                lines.append("")
                lines.append("---")
                lines.append("")
                continue

            lines.append(f"- Total evidence items: {result.total_items}")
            lines.append(f"- Fresh items (within {recency_years}y): {result.fresh_items}")
            lines.append(f"- Stale items (older than {recency_years}y): {result.stale_items}")

            if result.total_items > 0:
                pct = round(result.stale_items / result.total_items * 100, 1)
                lines.append(f"- Staleness ratio: {pct}%")
            lines.append("")

            if result.stale_sections:
                lines.append("### Stale Sections")
                lines.append("")
                for section_id in result.stale_sections:
                    lines.append(f"- `{section_id}`")
                lines.append("")

            if result.qa_rerun_needed:
                lines.append("**QA re-run recommended** (>50% stale evidence)")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def generate_revision_history_report(self, condition_slug: str = None) -> str:
        """Generate markdown revision history from review states."""
        all_reviews = self.manager.list_all(condition_slug=condition_slug)

        lines = [
            "# Revision History Report",
            "",
            f"*Generated: {_now_iso()}*",
        ]
        if condition_slug:
            lines.append(f"*Condition: {condition_slug}*")
        lines.append("")

        if not all_reviews:
            lines.append("No reviews found.")
            return "\n".join(lines)

        for review in all_reviews:
            lines.append(f"## {review.build_id}")
            lines.append("")
            lines.append(f"- **Condition:** {review.condition_slug}")
            lines.append(f"- **Document type:** {review.document_type}")
            lines.append(f"- **Tier:** {review.tier}")
            lines.append(f"- **Current status:** {review.status.value}")
            lines.append(f"- **Version:** {review.version}")
            lines.append(f"- **Created:** {review.created_at}")
            lines.append("")

            if review.decisions:
                lines.append("### Decision History")
                lines.append("")
                lines.append("| # | Status | Reviewer | Reason | Date |")
                lines.append("|---|--------|----------|--------|------|")
                for idx, decision in enumerate(review.decisions, 1):
                    reason_short = decision.reason[:80] if decision.reason else ""
                    lines.append(
                        f"| {idx} | {decision.status.value} | "
                        f"{decision.reviewer} | {reason_short} | "
                        f"{decision.decided_at} |"
                    )
                lines.append("")

            # Section comments
            if review.section_notes:
                lines.append("### Section Comments")
                lines.append("")
                for section_id, comments in review.section_notes.items():
                    lines.append(f"**{section_id}:**")
                    for comment in comments:
                        reviewer = comment.reviewer if hasattr(comment, "reviewer") else comment.get("reviewer", "")
                        text = comment.text if hasattr(comment, "text") else comment.get("text", "")
                        lines.append(f"  - [{reviewer}] {text}")
                    lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def generate_section_review_summaries(
        self, condition: ConditionSchema,
    ) -> list[SectionReviewSummary]:
        """Build section-level review data combining evidence + review state."""
        mapper = SectionEvidenceMapper()
        items = mapper.build_evidence_items_from_condition(condition)

        summaries: list[SectionReviewSummary] = []

        # Build a document evidence profile to get per-section data
        from ..content.assembler import ContentAssembler
        from ..schemas.documents import DocumentSpec
        from ..core.enums import DocumentType, Tier

        assembler = ContentAssembler()
        try:
            sections = assembler.assemble(condition, DocumentType.EVIDENCE_BASED_PROTOCOL, Tier.FELLOW)
            spec = DocumentSpec(
                document_type=DocumentType.EVIDENCE_BASED_PROTOCOL,
                tier=Tier.FELLOW,
                condition_slug=condition.slug,
                condition_name=condition.display_name,
                title="Section Review Check",
                sections=sections,
            )
            profile = mapper.map_to_sections(spec, items)
        except Exception as exc:
            logger.warning("Could not build section profiles for %s: %s", condition.slug, exc)
            return summaries

        # Collect any review comments keyed by section
        all_reviews = self.manager.list_all(condition_slug=condition.slug)
        section_comments: dict[str, list[dict]] = {}
        for review in all_reviews:
            for section_id, comments in review.section_notes.items():
                if section_id not in section_comments:
                    section_comments[section_id] = []
                for c in comments:
                    section_comments[section_id].append({
                        "reviewer": c.reviewer if hasattr(c, "reviewer") else "",
                        "text": c.text if hasattr(c, "text") else "",
                        "build_id": review.build_id,
                    })

        for section_id, sec_profile in profile.sections.items():
            summary = SectionReviewSummary(
                section_id=section_id,
                title=section_id.replace("_", " ").title(),
                evidence_confidence=sec_profile.confidence,
                article_count=sec_profile.article_count,
                has_contradictions=sec_profile.has_contradictions,
                is_outdated=section_id in profile.outdated_sections,
                is_weak=section_id in profile.weak_sections,
                comments=section_comments.get(section_id, []),
                review_flags=sec_profile.review_reasons,
                needs_review=sec_profile.needs_review,
            )
            summaries.append(summary)

        return summaries

    def export_approved_bundle(self, output_dir: Path) -> dict:
        """Export all approved documents as a bundle with manifest."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        copied = self.manager.export_approved_only(output_dir)

        # Build manifest
        manifest = {
            "exported_at": _now_iso(),
            "total_exported": len(copied),
            "files": [str(p.name) for p in copied],
        }

        manifest_path = output_dir / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2), encoding="utf-8",
        )

        logger.info("Exported %d approved documents to %s", len(copied), output_dir)
        return manifest

    def export_all_reports(
        self,
        output_dir: Path,
        conditions: list[ConditionSchema],
        recency_years: int = 5,
    ) -> dict[str, Path]:
        """Generate and save all report types to output_dir."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths: dict[str, Path] = {}

        # Flagged report
        flagged_md = self.generate_flagged_report()
        flagged_path = output_dir / "flagged_report.md"
        flagged_path.write_text(flagged_md, encoding="utf-8")
        paths["flagged_report"] = flagged_path

        # Evidence gaps
        gaps_md = self.generate_evidence_gap_report(conditions)
        gaps_path = output_dir / "evidence_gaps.md"
        gaps_path.write_text(gaps_md, encoding="utf-8")
        paths["evidence_gaps"] = gaps_path

        # Stale evidence
        stale_md = self.generate_stale_evidence_report(conditions, recency_years=recency_years)
        stale_path = output_dir / "stale_evidence.md"
        stale_path.write_text(stale_md, encoding="utf-8")
        paths["stale_evidence"] = stale_path

        # Revision history
        history_md = self.generate_revision_history_report()
        history_path = output_dir / "revision_history.md"
        history_path.write_text(history_md, encoding="utf-8")
        paths["revision_history"] = history_path

        logger.info("Exported all reports to %s (%d files)", output_dir, len(paths))
        return paths
