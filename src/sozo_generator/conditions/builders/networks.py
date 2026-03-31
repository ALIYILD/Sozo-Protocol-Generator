"""Builder for FNON network sections."""
from ...schemas.condition import ConditionSchema
from ...schemas.documents import SectionContent
from ...core.enums import NetworkDysfunction


NETWORK_DISPLAY_NAMES = {
    "dmn": "Default Mode Network (DMN)",
    "cen": "Central Executive Network (CEN/FPN)",
    "sn": "Salience Network (SN)",
    "smn": "Sensorimotor Network (SMN)",
    "limbic": "Limbic / Emotional Network",
    "attention": "Attention Networks (DAN/VAN)",
}

DYSFUNCTION_LABELS = {
    NetworkDysfunction.HYPO: "HYPO-active",
    NetworkDysfunction.NORMAL: "Within normal range",
    NetworkDysfunction.HYPER: "HYPER-active",
}


def build_networks_section(condition: ConditionSchema) -> SectionContent:
    network_rows = []
    for np in condition.network_profiles:
        network_rows.append([
            NETWORK_DISPLAY_NAMES.get(np.network.value, np.network.value),
            DYSFUNCTION_LABELS.get(np.dysfunction, np.dysfunction.value),
            "Primary" if np.primary else "Secondary",
            np.relevance,
        ])

    return SectionContent(
        section_id="networks",
        title="Brain Network Involvement — FNON Framework",
        content=(
            f"{condition.fnon_rationale}\n\n"
            "The Functional Network-Oriented Neuromodulation (FNON) framework identifies "
            "dysfunctional large-scale brain networks as stimulation targets, rather than "
            "isolated symptom-based regions. Core principle: Do NOT stimulate symptoms — "
            "stimulate dysfunctional NETWORKS."
        ),
        tables=[{
            "headers": ["Network", "Dysfunction Pattern", "Priority", "Relevance to Condition"],
            "rows": network_rows,
            "caption": f"FNON network involvement profile for {condition.display_name}",
        }] if network_rows else [],
        is_placeholder=not bool(condition.network_profiles),
    )


def build_symptom_network_section(condition: ConditionSchema) -> SectionContent:
    rows = []
    for symptom, networks in condition.symptom_network_mapping.items():
        modalities = condition.symptom_modality_mapping.get(symptom, [])
        rows.append([
            symptom,
            ", ".join(n.value.upper() for n in networks),
            ", ".join(m.value.upper() for m in modalities),
        ])

    return SectionContent(
        section_id="symptom_network_mapping",
        title="Symptom–Network–Modality Mapping",
        content="The following table maps clinical symptom clusters to their hypothesized network disruptions and recommended neuromodulation modalities:",
        tables=[{
            "headers": ["Symptom Cluster", "Implicated Network(s)", "Recommended Modality(ies)"],
            "rows": rows,
            "caption": "Symptom-to-network-to-modality mapping for treatment targeting",
        }] if rows else [],
        is_placeholder=not bool(condition.symptom_network_mapping),
    )
