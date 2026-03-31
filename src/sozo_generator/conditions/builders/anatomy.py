"""Builder for neuroanatomy sections."""
from ...schemas.condition import ConditionSchema
from ...schemas.documents import SectionContent


def build_anatomy_section(condition: ConditionSchema) -> SectionContent:
    region_rows = []
    for region_abbr in condition.key_brain_regions:
        desc = condition.brain_region_descriptions.get(region_abbr, "")
        region_rows.append({"Region": region_abbr, "Description": desc})

    return SectionContent(
        section_id="neuroanatomy",
        title="Key Brain Structures Involved",
        content=(
            f"The following brain regions are most relevant to {condition.display_name} "
            f"pathophysiology and stimulation targeting:"
        ),
        tables=[{
            "headers": ["Brain Region / Abbreviation", "Functional Role & Relevance"],
            "rows": [[r["Region"], r["Description"]] for r in region_rows],
            "caption": f"Key neuroanatomical targets for {condition.display_name} neuromodulation",
        }] if region_rows else [],
        is_placeholder=not bool(condition.key_brain_regions),
    )
