"""
SOZO QA — Figure/visual completeness checker.
Verifies expected visual files exist for a condition.
"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Per-condition figure templates (formatted with condition slug)
_CONDITION_FIGURE_TEMPLATES: list[str] = [
    "{slug}_brain_map.png",
    "{slug}_network_diagram.png",
    "{slug}_symptom_flow.png",
    "{slug}_patient_journey.png",
]

# Shared legend files expected to exist in the visuals directory
_SHARED_LEGENDS: list[str] = [
    "evidence_legend.png",
    "network_legend.png",
    "confidence_legend.png",
]


class FigureChecker:
    """Checks that expected visual / figure files exist for a condition."""

    def check_condition_figures(
        self, condition_slug: str, visuals_dir: Path
    ) -> dict:
        """
        Check figure completeness for a single condition.

        Returns a dict with keys:
            condition, expected, found, missing, passed
        """
        # Build the full expected file list
        condition_figures = [
            tmpl.format(slug=condition_slug)
            for tmpl in _CONDITION_FIGURE_TEMPLATES
        ]
        expected: list[str] = condition_figures + _SHARED_LEGENDS

        found: list[str] = []
        missing: list[str] = []

        if not visuals_dir.exists():
            logger.warning(
                "Figure check: visuals directory does not exist: %s", visuals_dir
            )
            missing = list(expected)
            return {
                "condition": condition_slug,
                "expected": expected,
                "found": found,
                "missing": missing,
                "passed": False,
            }

        for filename in expected:
            file_path = visuals_dir / filename
            if file_path.exists():
                found.append(filename)
            else:
                logger.warning(
                    "Figure check: missing figure '%s' for condition '%s'",
                    filename,
                    condition_slug,
                )
                missing.append(filename)

        passed = len(missing) == 0

        return {
            "condition": condition_slug,
            "expected": expected,
            "found": found,
            "missing": missing,
            "passed": passed,
        }
