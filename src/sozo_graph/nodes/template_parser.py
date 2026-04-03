"""
template_parser — parses uploaded DOCX/PDF into structured sections.

Type: Deterministic
Wraps: sozo_generator.template_profiles.builder.build_template_profile
"""
from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from ..audit.logger import audited_node
from ..state import SozoGraphState

logger = logging.getLogger(__name__)


@audited_node("template_parser")
def template_parser(state: SozoGraphState) -> dict:
    """Parse an uploaded template file into a structured profile."""
    decisions = []
    intake = state.get("intake", {})

    uploaded_file = intake.get("uploaded_file")
    uploaded_filename = intake.get("uploaded_filename", "unknown.docx")

    if not uploaded_file:
        decisions.append("No uploaded file — skipping template parsing")
        return {
            "intake": {
                **intake,
                "parse_error": "No file uploaded",
                "parse_warnings": [],
            },
            "_decisions": decisions,
        }

    # Write to temp file for the builder
    suffix = Path(uploaded_filename).suffix or ".docx"
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(uploaded_file if isinstance(uploaded_file, bytes) else uploaded_file.read())
            tmp_path = tmp.name

        from sozo_generator.template_profiles.builder import build_template_profile
        profile = build_template_profile(tmp_path)

        # Extract useful fields
        inferred_condition = None
        inferred_doc_type = profile.inferred_doc_type

        # Try to infer condition from profile name or section content
        if profile.name:
            name_lower = profile.name.lower()
            from sozo_graph.nodes.prompt_normalizer import AVAILABLE_CONDITIONS
            _ALIASES = {
                "parkinsons": ["parkinson", "parkinson's"],
                "alzheimers": ["alzheimer", "alzheimer's"],
                "stroke_rehab": ["stroke"],
                "chronic_pain": ["pain"],
                "long_covid": ["long covid", "post-covid"],
            }
            for slug in AVAILABLE_CONDITIONS:
                aliases = _ALIASES.get(slug, []) + [slug, slug.replace("_", " ")]
                if any(alias in name_lower for alias in aliases):
                    inferred_condition = slug
                    break

        section_count = len(profile.section_map) if hasattr(profile, "section_map") else 0
        decisions.append(
            f"Parsed template '{uploaded_filename}': "
            f"{section_count} sections, "
            f"inferred_doc_type={inferred_doc_type}, "
            f"inferred_condition={inferred_condition}"
        )

        parse_warnings = []
        if not inferred_condition:
            parse_warnings.append("Could not infer condition from template — will need manual selection or prompt")
        if section_count == 0:
            parse_warnings.append("No sections detected in template")

        return {
            "intake": {
                **intake,
                "template_profile": profile.model_dump() if hasattr(profile, "model_dump") else {},
                "normalized_request": {
                    "condition_slug": inferred_condition or "",
                    "condition_display": "",
                    "modality_preferences": [],
                    "personalization_requested": False,
                    "eeg_data_referenced": False,
                    "uncertainty_flags": parse_warnings,
                    "raw_prompt": f"Template upload: {uploaded_filename}",
                },
                "parse_warnings": parse_warnings,
                "parse_error": None,
            },
            "_decisions": decisions,
        }

    except Exception as e:
        logger.error("Template parsing failed: %s", e)
        decisions.append(f"Parse error: {e}")
        return {
            "intake": {
                **intake,
                "parse_error": str(e),
                "parse_warnings": [f"Template parsing failed: {e}"],
                "normalized_request": {
                    "condition_slug": "",
                    "condition_display": "",
                    "uncertainty_flags": [f"Template parse error: {e}"],
                    "raw_prompt": f"Template upload: {uploaded_filename} (FAILED)",
                },
            },
            "_decisions": decisions,
        }
    finally:
        # Clean up temp file
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass
