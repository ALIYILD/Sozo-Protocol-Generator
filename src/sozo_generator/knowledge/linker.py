"""
Knowledge Linker — validates cross-references between knowledge objects.

Checks that all slug references in knowledge objects resolve to actual objects.
Produces a validation report with warnings for broken links.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from .schemas import (
    KnowledgeCondition,
    KnowledgeModality,
    KnowledgeAssessment,
    KnowledgeBrainTarget,
    KnowledgeEvidenceMap,
)

logger = logging.getLogger(__name__)


@dataclass
class LinkIssue:
    """A single cross-reference validation issue."""
    source_type: str  # "condition", "modality", etc.
    source_slug: str
    field: str
    target_type: str
    target_slug: str
    severity: str = "warning"  # "warning", "error"
    message: str = ""


@dataclass
class LinkReport:
    """Validation report for knowledge cross-references."""
    total_checks: int = 0
    resolved: int = 0
    issues: list[LinkIssue] = field(default_factory=list)

    @property
    def broken_count(self) -> int:
        return len(self.issues)

    @property
    def valid(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)


def validate_links(
    conditions: dict[str, KnowledgeCondition],
    modalities: dict[str, KnowledgeModality],
    assessments: dict[str, KnowledgeAssessment],
    targets: dict[str, KnowledgeBrainTarget],
    evidence_maps: list[KnowledgeEvidenceMap],
) -> LinkReport:
    """Validate all cross-references between knowledge objects."""
    report = LinkReport()

    # 1. Conditions → modalities
    for slug, cond in conditions.items():
        for mod_ref in cond.applicable_modalities:
            report.total_checks += 1
            if mod_ref in modalities:
                report.resolved += 1
            else:
                report.issues.append(LinkIssue(
                    source_type="condition", source_slug=slug,
                    field="applicable_modalities", target_type="modality",
                    target_slug=mod_ref,
                    message=f"Condition '{slug}' references modality '{mod_ref}' which does not exist",
                ))

    # 2. Conditions → assessments
    for slug, cond in conditions.items():
        for asmt_ref in cond.assessments:
            report.total_checks += 1
            if asmt_ref.scale_key in assessments:
                report.resolved += 1
            else:
                report.issues.append(LinkIssue(
                    source_type="condition", source_slug=slug,
                    field="assessments", target_type="assessment",
                    target_slug=asmt_ref.scale_key, severity="warning",
                    message=f"Condition '{slug}' references assessment '{asmt_ref.scale_key}' which is not loaded",
                ))

    # 3. Conditions → brain targets
    for slug, cond in conditions.items():
        for region in cond.brain_regions:
            report.total_checks += 1
            if region in targets:
                report.resolved += 1
            # Brain regions may use display names, not slugs — soft check
            # Don't flag as error since this is a common pattern

    # 4. Protocols → modalities
    for slug, cond in conditions.items():
        for proto in cond.protocols:
            report.total_checks += 1
            if proto.modality in modalities:
                report.resolved += 1
            else:
                report.issues.append(LinkIssue(
                    source_type="condition", source_slug=slug,
                    field=f"protocols[{proto.protocol_id}].modality",
                    target_type="modality", target_slug=proto.modality,
                    message=f"Protocol '{proto.protocol_id}' references modality '{proto.modality}' which does not exist",
                ))

    # 5. Evidence maps → conditions and modalities
    for emap in evidence_maps:
        report.total_checks += 2
        if emap.condition_slug in conditions:
            report.resolved += 1
        else:
            report.issues.append(LinkIssue(
                source_type="evidence_map",
                source_slug=f"{emap.condition_slug}_{emap.modality_slug}",
                field="condition_slug", target_type="condition",
                target_slug=emap.condition_slug,
                message=f"Evidence map references condition '{emap.condition_slug}' which does not exist",
            ))
        if emap.modality_slug in modalities:
            report.resolved += 1
        else:
            report.issues.append(LinkIssue(
                source_type="evidence_map",
                source_slug=f"{emap.condition_slug}_{emap.modality_slug}",
                field="modality_slug", target_type="modality",
                target_slug=emap.modality_slug,
                message=f"Evidence map references modality '{emap.modality_slug}' which does not exist",
            ))

    # 6. Modalities → applicable conditions
    for slug, mod in modalities.items():
        for cond_ref in mod.applicable_conditions:
            report.total_checks += 1
            if cond_ref in conditions:
                report.resolved += 1
            # Soft check — modality may list conditions not yet loaded

    logger.info(
        f"Knowledge link validation: {report.resolved}/{report.total_checks} resolved, "
        f"{report.broken_count} issues"
    )
    return report
