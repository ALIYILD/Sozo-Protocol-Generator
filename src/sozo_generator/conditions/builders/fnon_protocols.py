"""FNON (Functional Network-Oriented Neuromodulation) variant builder.

Generates FT (FNON TPS) and F (FNON tDCS) protocol variants for Partners tier.
These are algorithmically derived from base protocols with network-oriented framing.
"""
from __future__ import annotations

from typing import Optional

from ...schemas.condition import ConditionSchema
from ...schemas.documents import SectionContent
from ...core.enums import Modality, NetworkKey


# Network descriptions for FNON framing
_NETWORK_LABELS = {
    NetworkKey.SMN: "Sensorimotor Network (SMN)",
    NetworkKey.CEN: "Central Executive Network (CEN)",
    NetworkKey.DMN: "Default Mode Network (DMN)",
    NetworkKey.LIMBIC: "Limbic/Emotional Network",
    NetworkKey.SN: "Salience Network (SN)",
    NetworkKey.ATTENTION: "Attention Networks (DAN/VAN)",
}


def build_fnon_tps_variants(condition: ConditionSchema) -> Optional[SectionContent]:
    """Generate FNON TPS protocol variants (FT1-FTn) from base TPS protocols.

    Each base TPS protocol gets an FNON variant with network-oriented framing,
    phenotype-specific targeting, and multimodal combination guidance.
    """
    tps_protocols = [p for p in condition.protocols if p.modality == Modality.TPS]
    if not tps_protocols:
        return None

    subsections = []
    for i, protocol in enumerate(tps_protocols, start=1):
        ft_id = f"FT{i}"
        networks = [_NETWORK_LABELS.get(n, n.value) for n in protocol.network_targets]
        networks_str = ", ".join(networks) if networks else "Multi-network"
        phenotypes_str = ", ".join(protocol.phenotype_slugs).upper() if protocol.phenotype_slugs else "All phenotypes"

        # Build FNON-specific parameter table
        rows = [
            ["FNON Variant ID", ft_id],
            ["Base Protocol", f"{protocol.protocol_id}: {protocol.label}"],
            ["Primary Network Target(s)", networks_str],
            ["Target Phenotype(s)", phenotypes_str],
            ["FNON Rationale", f"Network-oriented targeting of {networks_str} dysfunction via {protocol.target_region}"],
        ]
        # Include base parameters
        for key, val in protocol.parameters.items():
            label = key.replace("_", " ").title()
            rows.append([label, str(val)])

        # S-O-Z-O stage assignment
        sozo_rows = [
            ["S — Stabilise", f"Establish baseline with {protocol.protocol_id} targeting {protocol.target_abbreviation}"],
            ["O — Optimise", f"Combine with tDCS protocol targeting same network ({networks_str})"],
            ["Z — Zone", "Adjust pulse count and energy based on Week 4 response assessment"],
            ["O — Outcome", "Formal outcome evaluation at Week 8-10 with network reassessment"],
        ]

        # Evidence combination table
        combo_rows = []
        # Find matching tDCS protocols targeting same networks
        for tdcs_p in condition.protocols:
            if tdcs_p.modality == Modality.TDCS and any(n in tdcs_p.network_targets for n in protocol.network_targets):
                combo_rows.append([
                    f"{ft_id} + {tdcs_p.protocol_id}",
                    f"Combined {protocol.target_abbreviation} TPS + {tdcs_p.target_abbreviation} tDCS for {networks_str} rebalancing",
                    "TPS 2-3×/week + tDCS daily (non-overlapping days)",
                    phenotypes_str,
                    f"{protocol.evidence_level.value} + {tdcs_p.evidence_level.value}",
                ])

        tables = [
            {
                "headers": ["Parameter", "Value"],
                "rows": rows,
                "caption": f"FNON TPS variant {ft_id} — network-oriented parameters",
            },
            {
                "headers": ["S-O-Z-O Stage", "Application"],
                "rows": sozo_rows,
                "caption": f"S-O-Z-O sequencing for {ft_id}",
            },
        ]

        if combo_rows:
            tables.append({
                "headers": ["Combination", "Rationale", "Timing", "Indication", "Evidence"],
                "rows": combo_rows,
                "caption": f"Evidence-based combinations for {ft_id}",
            })

        subsections.append(SectionContent(
            section_id=f"fnon_{ft_id.lower()}",
            title=f"{ft_id}: FNON {protocol.label}",
            content=(
                f"Network-oriented variant of {protocol.protocol_id} ({protocol.label}). "
                f"Targets {networks_str} dysfunction via {protocol.target_region}. "
                f"{protocol.rationale}"
            ),
            tables=tables,
            callout_boxes=[{
                "text": f"FNON Protocol {ft_id}: All TPS applications are OFF-LABEL. "
                        "Requires Doctor authorisation, informed consent, and documented "
                        "network dysfunction assessment (6-Network Bedside Assessment).",
                "box_type": "offlabel",
            }],
        ))

    return SectionContent(
        section_id="fnon_tps_variants",
        title="FNON TPS Protocols — Network-Oriented",
        content=(
            "The following protocols apply TPS within the Functional Network-Oriented "
            "Neuromodulation (FNON) framework. Each variant targets specific dysfunctional "
            f"networks identified in {condition.display_name} via the 6-Network Bedside Assessment. "
            "FNON principle: Do NOT stimulate symptoms — stimulate dysfunctional NETWORKS."
        ),
        subsections=subsections,
    )


def build_fnon_tdcs_variants(condition: ConditionSchema) -> Optional[SectionContent]:
    """Generate FNON tDCS protocol variants (F1-Fn) from base tDCS protocols.

    Groups tDCS protocols by primary network target and creates network-oriented
    phenotype-to-protocol mapping sections.
    """
    tdcs_protocols = [p for p in condition.protocols if p.modality == Modality.TDCS]
    if not tdcs_protocols:
        return None

    # Group by primary network
    network_groups: dict[str, list] = {}
    for p in tdcs_protocols:
        primary = p.network_targets[0] if p.network_targets else NetworkKey.SMN
        key = primary.value
        network_groups.setdefault(key, []).append(p)

    subsections = []
    f_idx = 1
    for network_key, protocols in network_groups.items():
        network_enum = NetworkKey(network_key)
        network_label = _NETWORK_LABELS.get(network_enum, network_key)
        f_id = f"F{f_idx}"
        f_idx += 1

        # Protocol listing for this network
        proto_rows = []
        for p in protocols:
            phenotypes = ", ".join(p.phenotype_slugs).upper() if p.phenotype_slugs else "All"
            proto_rows.append([
                p.protocol_id, p.label, p.target_abbreviation,
                p.parameters.get("intensity", "2.0 mA"),
                p.parameters.get("duration", "20 min"),
                p.evidence_level.value, phenotypes,
            ])

        # Non-TPS combination recommendations
        combo_rows = []
        for p in protocols:
            combo_rows.append([
                f"{p.protocol_id} + CES-1",
                f"tDCS {p.target_abbreviation} + CES anxiety/sleep adjunct",
                "tDCS daily + CES daily (same session OK)",
                ", ".join(p.phenotype_slugs).upper() if p.phenotype_slugs else "All",
                p.evidence_level.value,
            ])

        tables = [
            {
                "headers": ["Protocol ID", "Label", "Target", "Intensity", "Duration", "Evidence", "Phenotypes"],
                "rows": proto_rows,
                "caption": f"FNON tDCS protocols targeting {network_label}",
            },
            {
                "headers": ["Combination", "Rationale", "Timing", "Indication", "Evidence"],
                "rows": combo_rows,
                "caption": f"Non-TPS combinations for {network_label} targeting",
            },
        ]

        subsections.append(SectionContent(
            section_id=f"fnon_{f_id.lower()}",
            title=f"{f_id}: {network_label} — tDCS Protocols",
            content=(
                f"FNON network group targeting {network_label} dysfunction. "
                f"This group includes {len(protocols)} tDCS protocol(s) that address "
                f"{network_label} hypoactivation or hyperactivation patterns."
            ),
            tables=tables,
        ))

    return SectionContent(
        section_id="fnon_tdcs_variants",
        title="FNON tDCS Protocols — Network-Oriented",
        content=(
            "The following tDCS protocol groups are organised by primary network target "
            "within the FNON framework. Each group addresses a specific dysfunctional "
            "network identified via the 6-Network Bedside Assessment."
        ),
        subsections=subsections,
    )
