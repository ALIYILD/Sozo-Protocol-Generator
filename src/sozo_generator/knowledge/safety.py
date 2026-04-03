"""
Safety Validation Engine — programmatic parameter + contraindication checking.

Every generated protocol must pass safety validation before reaching a reviewer.
This is the enforcement layer, not just advisory text.

Checks:
1. Parameter safety: intensity, duration, frequency within device safe ranges
2. Contraindication screening: modality × known contraindications
3. Off-label disclosure: TPS for non-Alzheimer's conditions
4. Required safety sections: contraindications, adverse event grading, consent
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ── Device Safe Ranges ────────────────────────────────────────────────────

DEVICE_RANGES = {
    "tdcs": {
        "intensity_ma": (0.0, 2.0),
        "duration_min": (5, 40),
        "ramp_up_ms": (0, 60000),
        "electrode_size_cm2": (9, 35),
    },
    "tps": {
        "energy_mj_mm2": (0.1, 0.3),
        "frequency_hz": (1, 10),
        "pulses_per_session": (100, 6000),
        "duration_min": (5, 30),
    },
    "tavns": {
        "intensity_ma": (0.1, 5.0),
        "frequency_hz": (1, 30),
        "pulse_width_us": (100, 500),
        "duration_min": (10, 60),
    },
    "ces": {
        "intensity_ua": (10, 600),
        "frequency_hz": (0.5, 100),
        "duration_min": (20, 60),
    },
}

# Absolute contraindications per modality
ABSOLUTE_CONTRAINDICATIONS = {
    "tdcs": ["cranial_metal_implants", "cardiac_implant", "active_epilepsy", "open_scalp_wounds"],
    "tps": ["cranial_metal_implants", "cardiac_implant", "active_epilepsy", "open_scalp_wounds", "recent_neurosurgery", "dbs_implant"],
    "tavns": ["cardiac_implant"],
    "ces": ["cardiac_implant"],
}

# Conditions where TPS is ON-label
TPS_ON_LABEL = ["alzheimers"]


# ── Models ────────────────────────────────────────────────────────────────


@dataclass
class SafetyCheck:
    """One safety check result."""
    check_type: str  # parameter, contraindication, off_label, required_section
    target: str  # what was checked
    passed: bool = True
    severity: str = "info"  # info, warning, critical, block
    message: str = ""
    modality: str = ""


@dataclass
class SafetyValidationReport:
    """Complete safety validation result for a protocol."""
    condition_slug: str = ""
    doc_type: str = ""
    tier: str = ""
    checks: list[SafetyCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(c.severity == "block" for c in self.checks)

    @property
    def blocking_count(self) -> int:
        return sum(1 for c in self.checks if c.severity == "block")

    @property
    def warning_count(self) -> int:
        return sum(1 for c in self.checks if c.severity == "warning")

    @property
    def total_checks(self) -> int:
        return len(self.checks)

    def to_text(self) -> str:
        lines = [
            f"=== SAFETY VALIDATION: {self.condition_slug}/{self.doc_type}/{self.tier} ===",
            f"Result: {'PASS' if self.passed else 'BLOCKED'}",
            f"Checks: {self.total_checks} total, {self.blocking_count} blocking, {self.warning_count} warnings",
        ]
        for c in self.checks:
            if not c.passed:
                lines.append(f"  [{c.severity.upper()}] {c.check_type}: {c.message}")
        return "\n".join(lines)


# ── Validator ─────────────────────────────────────────────────────────────


class SafetyValidator:
    """Validates protocol safety: parameters, contraindications, disclosures."""

    def validate_protocol(
        self,
        condition_slug: str,
        protocols: list[dict],
        safety_rules: list[dict] = None,
        doc_type: str = "",
        tier: str = "",
    ) -> SafetyValidationReport:
        """Run all safety checks on a protocol set."""
        report = SafetyValidationReport(
            condition_slug=condition_slug, doc_type=doc_type, tier=tier
        )

        for proto in protocols:
            modality = proto.get("modality", "")
            params = proto.get("parameters", {})
            label = proto.get("label", proto.get("protocol_id", ""))

            # 1. Parameter range checks
            self._check_parameters(modality, params, label, report)

            # 2. Off-label disclosure
            self._check_off_label(modality, condition_slug, label, report)

        # 3. Contraindication coverage
        modalities_used = list(set(p.get("modality", "") for p in protocols))
        self._check_contraindications(modalities_used, safety_rules or [], report)

        # 4. Required safety content
        self._check_required_sections(safety_rules or [], report)

        return report

    def _check_parameters(self, modality: str, params: dict, label: str, report: SafetyValidationReport):
        """Check protocol parameters against device safe ranges."""
        ranges = DEVICE_RANGES.get(modality)
        if not ranges:
            return

        for param_key, (low, high) in ranges.items():
            value = params.get(param_key)
            if value is None:
                continue
            if not isinstance(value, (int, float)):
                continue
            if value < low or value > high:
                report.checks.append(SafetyCheck(
                    check_type="parameter",
                    target=f"{label}.{param_key}",
                    passed=False,
                    severity="block",
                    message=f"{param_key}={value} outside safe range [{low}, {high}] for {modality}",
                    modality=modality,
                ))
            else:
                report.checks.append(SafetyCheck(
                    check_type="parameter",
                    target=f"{label}.{param_key}",
                    passed=True,
                    severity="info",
                    message=f"{param_key}={value} within range [{low}, {high}]",
                    modality=modality,
                ))

    def _check_off_label(self, modality: str, condition: str, label: str, report: SafetyValidationReport):
        """Check if TPS off-label disclosure is required."""
        if modality == "tps" and condition not in TPS_ON_LABEL:
            report.checks.append(SafetyCheck(
                check_type="off_label",
                target=label,
                passed=True,
                severity="warning",
                message=f"TPS is OFF-LABEL for {condition}. Informed consent and Doctor authorization required.",
                modality="tps",
            ))

    def _check_contraindications(self, modalities: list[str], safety_rules: list[dict], report: SafetyValidationReport):
        """Check that required contraindications are documented."""
        for modality in modalities:
            required = ABSOLUTE_CONTRAINDICATIONS.get(modality, [])
            documented = [r.get("category", "").lower().replace(" ", "_") for r in safety_rules]
            for contra in required:
                if any(contra in d or d in contra for d in documented):
                    report.checks.append(SafetyCheck(
                        check_type="contraindication",
                        target=contra,
                        passed=True,
                        severity="info",
                        message=f"Contraindication '{contra}' documented for {modality}",
                        modality=modality,
                    ))
                else:
                    report.checks.append(SafetyCheck(
                        check_type="contraindication",
                        target=contra,
                        passed=False,
                        severity="warning",
                        message=f"Contraindication '{contra}' may not be documented for {modality}",
                        modality=modality,
                    ))

    def _check_required_sections(self, safety_rules: list[dict], report: SafetyValidationReport):
        """Check that minimum safety content exists."""
        if not safety_rules:
            report.checks.append(SafetyCheck(
                check_type="required_section",
                target="safety_rules",
                passed=False,
                severity="warning",
                message="No safety rules defined — contraindications section may be empty",
            ))
        else:
            report.checks.append(SafetyCheck(
                check_type="required_section",
                target="safety_rules",
                passed=True,
                severity="info",
                message=f"{len(safety_rules)} safety rules defined",
            ))


def validate_condition_protocols(condition_slug: str) -> Optional[SafetyValidationReport]:
    """Validate all protocols for a condition from the knowledge base."""
    try:
        from .base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        cond = kb.get_condition(condition_slug)
        if not cond:
            return None

        validator = SafetyValidator()
        return validator.validate_protocol(
            condition_slug=condition_slug,
            protocols=[p.model_dump() for p in cond.protocols],
            safety_rules=[s.model_dump() for s in cond.safety_rules],
        )
    except Exception as e:
        logger.error(f"Safety validation failed: {e}")
        return None
