"""Builder for clinical phenotype classification sections."""
from ...schemas.condition import ConditionSchema
from ...schemas.documents import SectionContent


def build_phenotype_section(condition: ConditionSchema) -> SectionContent:
    phenotype_rows = []
    for ph in condition.phenotypes:
        phenotype_rows.append([
            ph.label,
            ph.description,
            ", ".join(ph.key_features[:3]),
            ", ".join(n.value.upper() for n in ph.primary_networks),
            ", ".join(m.value.upper() for m in ph.preferred_modalities),
        ])

    return SectionContent(
        section_id="phenotypes",
        title=f"Clinical Phenotypes of {condition.display_name}",
        content=(
            f"{condition.display_name} presents with distinct clinical phenotypes that guide "
            "neuromodulation target selection. Phenotype identification is the first step "
            "in the FNON Five-Level Clinical Decision Pathway."
        ),
        tables=[{
            "headers": ["Phenotype", "Description", "Key Features", "Primary Network(s)", "Preferred Modality(ies)"],
            "rows": phenotype_rows,
            "caption": f"Clinical phenotype classification for {condition.display_name}",
        }] if phenotype_rows else [],
        is_placeholder=not bool(condition.phenotypes),
        review_flags=["No phenotypes defined — clinical review required"] if not condition.phenotypes else [],
    )
