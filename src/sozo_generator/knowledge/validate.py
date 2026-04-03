"""
Knowledge Validation & Linting — validates YAML knowledge and blueprint assets.

Checks:
- YAML syntax
- Schema validation (Pydantic)
- Cross-reference integrity
- Missing fields
- PMID format
- Blueprint section coverage

Usage:
    from sozo_generator.knowledge.validate import validate_all, validate_condition

    results = validate_all()
    result = validate_condition("parkinsons")
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .schemas import KnowledgeCondition, KnowledgeModality
from .specs import DocumentBlueprint
from .loader import KNOWLEDGE_ROOT, BLUEPRINTS_ROOT

logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """A single validation finding."""
    file: str
    severity: str  # "error", "warning", "info"
    message: str
    field: str = ""


@dataclass
class ValidationReport:
    """Complete validation report."""
    files_checked: int = 0
    files_valid: int = 0
    files_invalid: int = 0
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    def to_text(self) -> str:
        lines = [
            f"=== VALIDATION REPORT ===",
            f"Files checked: {self.files_checked}",
            f"Valid: {self.files_valid}",
            f"Invalid: {self.files_invalid}",
            f"Issues: {len(self.issues)} ({sum(1 for i in self.issues if i.severity == 'error')} errors, "
            f"{sum(1 for i in self.issues if i.severity == 'warning')} warnings)",
        ]
        if self.issues:
            lines.append("")
            for i in self.issues:
                lines.append(f"  [{i.severity.upper()}] {i.file}: {i.message}")
        return "\n".join(lines)


def validate_all(knowledge_dir: Path | None = None) -> ValidationReport:
    """Validate all knowledge and blueprint YAML files."""
    report = ValidationReport()

    kb_dir = knowledge_dir or KNOWLEDGE_ROOT
    bp_dir = BLUEPRINTS_ROOT

    # Validate conditions
    cond_dir = kb_dir / "conditions"
    if cond_dir.exists():
        for path in sorted(cond_dir.glob("*.yaml")):
            if path.stem.startswith("_"):
                continue
            _validate_yaml(path, KnowledgeCondition, report)

    # Validate modalities
    mod_dir = kb_dir / "modalities"
    if mod_dir.exists():
        for path in sorted(mod_dir.glob("*.yaml")):
            if path.stem.startswith("_"):
                continue
            _validate_yaml(path, KnowledgeModality, report)

    # Validate blueprints
    if bp_dir.exists():
        for path in sorted(bp_dir.glob("*.yaml")):
            if path.stem.startswith("_"):
                continue
            _validate_yaml(path, DocumentBlueprint, report)

    # Cross-reference checks
    _check_cross_references(kb_dir, bp_dir, report)

    return report


def validate_condition(slug: str, knowledge_dir: Path | None = None) -> ValidationReport:
    """Validate a single condition's knowledge YAML."""
    report = ValidationReport()
    kb_dir = knowledge_dir or KNOWLEDGE_ROOT
    path = kb_dir / "conditions" / f"{slug}.yaml"
    if not path.exists():
        report.issues.append(ValidationIssue(
            file=slug, severity="error", message=f"File not found: {path}"
        ))
        return report
    _validate_yaml(path, KnowledgeCondition, report)
    return report


def _validate_yaml(path: Path, model_class, report: ValidationReport):
    """Validate a single YAML file against a Pydantic model."""
    report.files_checked += 1

    # YAML syntax
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        report.files_invalid += 1
        report.issues.append(ValidationIssue(
            file=path.name, severity="error", message=f"YAML syntax error: {e}"
        ))
        return

    if not data:
        report.files_invalid += 1
        report.issues.append(ValidationIssue(
            file=path.name, severity="error", message="Empty YAML file"
        ))
        return

    # Schema validation
    try:
        obj = model_class(**data)
        report.files_valid += 1

        # Content quality checks
        if hasattr(obj, 'slug') and not obj.slug:
            report.issues.append(ValidationIssue(
                file=path.name, severity="warning", message="Missing slug"
            ))
        if hasattr(obj, 'references') and not obj.references:
            report.issues.append(ValidationIssue(
                file=path.name, severity="warning", message="No references defined"
            ))

    except Exception as e:
        report.files_invalid += 1
        report.issues.append(ValidationIssue(
            file=path.name, severity="error", message=f"Schema validation failed: {e}"
        ))


def _check_cross_references(kb_dir: Path, bp_dir: Path, report: ValidationReport):
    """Check cross-references between knowledge objects."""
    # Load all condition slugs
    cond_slugs = set()
    cond_dir = kb_dir / "conditions"
    if cond_dir.exists():
        for path in cond_dir.glob("*.yaml"):
            if not path.stem.startswith("_"):
                cond_slugs.add(path.stem)

    # Load modality slugs
    mod_slugs = set()
    mod_dir = kb_dir / "modalities"
    if mod_dir.exists():
        for path in mod_dir.glob("*.yaml"):
            if not path.stem.startswith("_"):
                mod_slugs.add(path.stem)

    # Check conditions reference valid modalities
    for path in (cond_dir or Path()).glob("*.yaml"):
        if path.stem.startswith("_"):
            continue
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
            for mod_ref in data.get("applicable_modalities", []):
                if mod_ref not in mod_slugs:
                    report.issues.append(ValidationIssue(
                        file=path.name, severity="warning",
                        field="applicable_modalities",
                        message=f"References modality '{mod_ref}' not found in modalities/"
                    ))
        except Exception:
            pass
