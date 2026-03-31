"""Builder for protocol sections."""
from ...schemas.condition import ConditionSchema
from ...schemas.documents import SectionContent
from ...core.enums import Modality


def build_protocols_section(condition: ConditionSchema) -> SectionContent:
    tdcs_rows = []
    tps_rows = []
    tavns_rows = []
    ces_rows = []

    for p in condition.protocols:
        row = [
            p.protocol_id,
            p.label,
            p.target_region,
            p.parameters.get("intensity", "Per protocol"),
            p.parameters.get("duration", "Per protocol"),
            p.evidence_level.value,
            "OFF-LABEL" if p.off_label else "Approved",
        ]
        if p.modality == Modality.TDCS:
            tdcs_rows.append(row)
        elif p.modality == Modality.TPS:
            tps_rows.append(row)
        elif p.modality == Modality.TAVNS:
            tavns_rows.append(row)
        elif p.modality == Modality.CES:
            ces_rows.append(row)

    headers = ["ID", "Protocol Label", "Target Region", "Intensity", "Duration", "Evidence", "Status"]
    subsections = []

    if tdcs_rows:
        subsections.append(SectionContent(
            section_id="tdcs_protocols",
            title="tDCS Protocols",
            content="tDCS protocols apply low-intensity direct current to modulate cortical excitability at the targeted network node.",
            tables=[{"headers": headers, "rows": tdcs_rows, "caption": "tDCS protocol summary"}],
        ))
    if tps_rows:
        subsections.append(SectionContent(
            section_id="tps_protocols",
            title="TPS Protocols (NEUROLITH)",
            content="ALL TPS applications for this condition are OFF-LABEL and require explicit Doctor authorization and documented patient consent.",
            tables=[{"headers": headers, "rows": tps_rows, "caption": "TPS protocol summary — OFF-LABEL"}],
            review_flags=["TPS off-label consent required for all entries"],
        ))
    if tavns_rows:
        subsections.append(SectionContent(
            section_id="tavns_protocols",
            title="taVNS Protocols",
            tables=[{"headers": headers, "rows": tavns_rows, "caption": "taVNS protocol summary"}],
        ))
    if ces_rows:
        subsections.append(SectionContent(
            section_id="ces_protocols",
            title="CES Protocols (Alpha-Stim)",
            tables=[{"headers": headers, "rows": ces_rows, "caption": "CES protocol summary"}],
        ))

    return SectionContent(
        section_id="protocols",
        title="Neuromodulation Protocols",
        content=(
            f"The following protocols are recommended for {condition.display_name} based on "
            "available evidence and SOZO FNON framework. All protocols require clinician assessment "
            "before initiation. Off-label applications require explicit informed consent."
        ),
        subsections=subsections,
        is_placeholder=not bool(condition.protocols),
        review_flags=["No protocols defined — clinical review required"] if not condition.protocols else [],
    )


def build_inclusion_exclusion_section(condition: ConditionSchema) -> SectionContent:
    inclusion_content = "\n".join(f"• {c}" for c in condition.inclusion_criteria) if condition.inclusion_criteria else "[REVIEW REQUIRED]"
    exclusion_content = "\n".join(f"• {c}" for c in condition.exclusion_criteria) if condition.exclusion_criteria else "[REVIEW REQUIRED]"
    contra_content = "\n".join(f"• {c}" for c in condition.contraindications) if condition.contraindications else "[REVIEW REQUIRED]"

    return SectionContent(
        section_id="inclusion_exclusion",
        title="Inclusion and Exclusion Criteria",
        subsections=[
            SectionContent(section_id="inclusion", title="Inclusion Criteria", content=inclusion_content),
            SectionContent(section_id="exclusion", title="Exclusion Criteria", content=exclusion_content),
            SectionContent(section_id="contraindications", title="Absolute Contraindications", content=contra_content),
        ],
        is_placeholder=not bool(condition.inclusion_criteria),
    )
