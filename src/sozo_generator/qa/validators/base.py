"""Base class for all canonical document validators."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from sozo_generator.schemas.canonical import (
    CanonicalDocument,
    QAValidationIssue,
    QAValidationResult,
)
from sozo_generator.schemas.canonical import _now_iso


class BaseDocumentValidator(ABC):
    """Base class for all canonical document validators."""

    validator_id: str = "base_validator"
    description: str = ""

    @abstractmethod
    def validate(self, document: CanonicalDocument) -> QAValidationResult:
        """Run validation. Returns QAValidationResult."""

    def _issue(
        self,
        severity: str,
        category: str,
        message: str,
        location: str = "",
        context: Optional[dict] = None,
        auto_fixable: bool = False,
    ) -> QAValidationIssue:
        """Helper to create a QAValidationIssue."""
        return QAValidationIssue(
            validator_id=self.validator_id,
            severity=severity,  # type: ignore[arg-type]
            category=category,
            message=message,
            location=location,
            context=context or {},
            auto_fixable=auto_fixable,
        )

    def _result(
        self,
        document_id: str,
        condition_slug: str,
        issues: list[QAValidationIssue],
        duration_seconds: float = 0.0,
    ) -> QAValidationResult:
        """Helper to create a QAValidationResult from issues list."""
        passed = not any(i.severity == "block" for i in issues)
        return QAValidationResult(
            validator_id=self.validator_id,
            document_id=document_id,
            condition_slug=condition_slug,
            passed=passed,
            issues=issues,
            duration_seconds=duration_seconds,
        )
