"""Review flag detection and injection."""
import logging
from ..schemas.documents import SectionContent
from ..core.utils import has_placeholder

logger = logging.getLogger(__name__)


def detect_and_tag_review_flags(sections: list) -> list:
    """Scan all sections and return list of review flag strings found."""
    flags = []
    for section in sections:
        if section.is_placeholder:
            flags.append(f"Section '{section.title}' is a placeholder — content required")
        if has_placeholder(section.content):
            flags.append(f"Placeholder text detected in section '{section.title}'")
        for subsection in section.subsections:
            sub_flags = detect_and_tag_review_flags([subsection])
            flags.extend(sub_flags)
    return flags


def scan_for_placeholders(sections: list) -> list:
    """Scan sections for placeholder text and return flags."""
    flags = []
    for section in sections:
        if section.is_placeholder or has_placeholder(section.content):
            flags.append(f"Placeholder text in section: {section.title}")
        for sub in section.subsections:
            if sub.is_placeholder or has_placeholder(sub.content):
                flags.append(f"Placeholder text in subsection: {sub.title}")
    return flags


def scan_for_missing_sections(
    sections: list,
    required_section_ids: list,
) -> list:
    """Check if required sections are present."""
    present_ids = {s.section_id for s in sections}
    for s in sections:
        present_ids.update(sub.section_id for sub in s.subsections)
    missing = [sid for sid in required_section_ids if sid not in present_ids]
    return [f"Missing required section: {sid}" for sid in missing]
