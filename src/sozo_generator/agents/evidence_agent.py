"""Evidence agent — retrieves and ranks evidence for conditions."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from .base import BaseAgent, AgentResult
from .registry import register_agent

logger = logging.getLogger(__name__)


@register_agent
class EvidenceAgent(BaseAgent):
    """Retrieve and rank evidence for conditions."""

    name = "evidence_agent"
    role = "Retrieve and rank evidence for conditions"

    def execute(self, input_data: dict, workspace_path: str, **kwargs) -> AgentResult:
        self._log(workspace_path, "Starting evidence retrieval and ranking")
        result = AgentResult()
        ws = Path(workspace_path)

        job = kwargs.get("job")
        conditions = input_data.get("conditions", [])
        if not conditions and job:
            conditions = job.target_conditions
        if not conditions:
            result.error = "No conditions specified"
            self._log(workspace_path, f"FAILED: {result.error}")
            return result

        recency_years = input_data.get("recency_years", 5)

        from ..conditions.registry import get_registry
        from ..evidence.section_evidence_mapper import SectionEvidenceMapper
        from ..evidence.refresh import EvidenceRefresher

        registry = get_registry()
        mapper = SectionEvidenceMapper(recency_years=recency_years)
        refresher = EvidenceRefresher(recency_years=recency_years)

        evidence_dir = ws / "evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)

        all_evidence = {}
        total_items = 0
        total_stale = 0

        for slug in conditions:
            if not registry.exists(slug):
                result.warnings.append(f"Condition '{slug}' not found in registry")
                self._log(workspace_path, f"WARNING: Condition '{slug}' not found")
                continue

            try:
                condition = registry.get(slug)
            except Exception as e:
                result.warnings.append(f"Could not load condition '{slug}': {e}")
                self._log(workspace_path, f"WARNING: Could not load '{slug}': {e}")
                continue

            # Build evidence items
            items = mapper.build_evidence_items_from_condition(condition)
            self._log(workspace_path, f"  {slug}: {len(items)} evidence items")

            # Assess staleness
            try:
                staleness = refresher.assess_staleness(condition)
            except Exception as e:
                self._log(workspace_path, f"  {slug}: staleness check failed: {e}")
                staleness = None

            # Build evidence summary for this condition
            evidence_summary = {
                "condition_slug": slug,
                "condition_name": condition.display_name,
                "total_items": len(items),
                "overall_evidence_quality": condition.overall_evidence_quality.value,
                "evidence_gaps": condition.evidence_gaps or [],
                "items": [],
            }

            for item in items:
                evidence_summary["items"].append({
                    "pmid": item.pmid or "",
                    "title": item.title,
                    "year": item.year,
                    "evidence_level": item.evidence_level.value,
                    "evidence_type": item.evidence_type.value,
                    "relation": item.relation.value if item.relation else "",
                    "key_finding": item.key_finding or "",
                })

            if staleness:
                evidence_summary["staleness"] = {
                    "stale_items": staleness.stale_items,
                    "fresh_items": staleness.fresh_items,
                    "stale_sections": staleness.stale_sections,
                    "qa_rerun_needed": staleness.qa_rerun_needed,
                }
                total_stale += staleness.stale_items

            all_evidence[slug] = evidence_summary
            total_items += len(items)

        # Write evidence summary
        evidence_path = evidence_dir / "evidence_summary.json"
        evidence_path.write_text(
            json.dumps({
                "total_conditions": len(all_evidence),
                "total_evidence_items": total_items,
                "total_stale_items": total_stale,
                "recency_years": recency_years,
                "conditions": all_evidence,
            }, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        self._log(workspace_path, f"Evidence summary: {total_items} items across {len(all_evidence)} conditions, {total_stale} stale")

        result.success = True
        result.artifacts.append({
            "type": "evidence_summary",
            "path": str(evidence_path),
            "description": f"{total_items} evidence items for {len(all_evidence)} conditions",
        })
        result.output_data = {
            "total_items": total_items,
            "total_stale": total_stale,
            "conditions_processed": list(all_evidence.keys()),
            "recency_years": recency_years,
        }
        if total_stale > total_items * 0.5:
            result.warnings.append(
                f"High staleness ratio: {total_stale}/{total_items} items are stale (>{recency_years} years old)"
            )
        return result
