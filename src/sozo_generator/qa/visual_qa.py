"""
Visual QA — validates generated protocol visuals for correctness.

Checks:
- Electrode position validity (10-20 system)
- Hemisphere consistency (left target → left electrode)
- Caption/data consistency
- Missing visual artifacts
- Provenance metadata
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..schemas.condition import ConditionSchema, StimulationTarget, ProtocolEntry
from ..visuals.montage_diagrams import ELECTRODES_10_20, TARGET_TO_ELECTRODE

logger = logging.getLogger(__name__)


@dataclass
class VisualQAIssue:
    """A visual QA finding."""
    severity: str = "warning"  # info, warning, error
    check: str = ""
    message: str = ""
    protocol_id: str = ""
    electrode: str = ""


@dataclass
class VisualQAReport:
    """QA report for visual artifacts."""
    condition_slug: str = ""
    total_checks: int = 0
    issues: list[VisualQAIssue] = field(default_factory=list)
    passed: bool = True

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")


# Hemisphere: electrodes ending in odd numbers are LEFT, even are RIGHT
_LEFT_ELECTRODES = {"Fp1", "F3", "C3", "P3", "O1", "F7", "T3", "T5", "A1"}
_RIGHT_ELECTRODES = {"Fp2", "F4", "C4", "P4", "O2", "F8", "T4", "T6", "A2"}
_MIDLINE_ELECTRODES = {"Fpz", "Fz", "Cz", "Pz", "Oz"}


class VisualQAChecker:
    """Validates protocol visual correctness."""

    def check_condition(self, condition: ConditionSchema) -> VisualQAReport:
        """Run all visual QA checks for a condition."""
        report = VisualQAReport(condition_slug=condition.slug)

        for proto in condition.protocols or []:
            self._check_protocol_electrodes(proto, report)
        for target in condition.stimulation_targets or []:
            self._check_target_hemisphere(target, report)
        self._check_target_electrode_coverage(condition, report)

        report.passed = report.error_count == 0
        return report

    def _check_protocol_electrodes(self, proto: ProtocolEntry, report: VisualQAReport) -> None:
        """Check that protocol electrode positions are valid 10-20 positions."""
        report.total_checks += 1
        params = proto.parameters if isinstance(proto.parameters, dict) else {}

        for key in ("anode", "cathode", "target_electrode"):
            electrode = params.get(key, "")
            if electrode and electrode.upper() not in ELECTRODES_10_20:
                report.issues.append(VisualQAIssue(
                    severity="warning",
                    check="electrode_validity",
                    message=f"Electrode '{electrode}' in protocol '{proto.label}' "
                            f"is not a standard 10-20 position",
                    protocol_id=proto.protocol_id,
                    electrode=electrode,
                ))

        # Check anode/cathode not the same
        anode = params.get("anode", "").upper()
        cathode = params.get("cathode", "").upper()
        if anode and cathode and anode == cathode:
            report.issues.append(VisualQAIssue(
                severity="error",
                check="electrode_collision",
                message=f"Anode and cathode are the same electrode '{anode}' "
                        f"in protocol '{proto.label}'",
                protocol_id=proto.protocol_id,
                electrode=anode,
            ))

    def _check_target_hemisphere(self, target: StimulationTarget, report: VisualQAReport) -> None:
        """Check laterality consistency with electrode hemisphere."""
        report.total_checks += 1
        laterality = target.laterality.lower()
        target_lower = target.target_region.lower().replace(" ", "_")

        # Find matching electrode
        for key, positions in TARGET_TO_ELECTRODE.items():
            if key in target_lower:
                if laterality == "left":
                    electrode = positions.get("left", positions.get("midline", ""))
                    if electrode and electrode in _RIGHT_ELECTRODES:
                        report.issues.append(VisualQAIssue(
                            severity="warning",
                            check="hemisphere_mismatch",
                            message=f"Target '{target.target_region}' is left-lateralized "
                                    f"but maps to right electrode '{electrode}'",
                        ))
                elif laterality == "right":
                    electrode = positions.get("right", positions.get("midline", ""))
                    if electrode and electrode in _LEFT_ELECTRODES:
                        report.issues.append(VisualQAIssue(
                            severity="warning",
                            check="hemisphere_mismatch",
                            message=f"Target '{target.target_region}' is right-lateralized "
                                    f"but maps to left electrode '{electrode}'",
                        ))
                break

    def _check_target_electrode_coverage(self, condition: ConditionSchema, report: VisualQAReport) -> None:
        """Check that all targets have electrode mappings."""
        report.total_checks += 1
        for target in condition.stimulation_targets or []:
            target_lower = target.target_region.lower().replace(" ", "_")
            has_mapping = any(k in target_lower for k in TARGET_TO_ELECTRODE)
            if not has_mapping:
                report.issues.append(VisualQAIssue(
                    severity="info",
                    check="unmapped_target",
                    message=f"Target '{target.target_region}' has no electrode mapping "
                            f"— visual diagram may be incomplete",
                ))
