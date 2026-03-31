"""Builder for responder tracking sections."""
from ...schemas.condition import ConditionSchema
from ...schemas.documents import SectionContent


def build_responder_section(condition: ConditionSchema) -> SectionContent:
    criteria_content = "\n".join(f"• {c}" for c in condition.responder_criteria) if condition.responder_criteria else "[REVIEW REQUIRED: Responder criteria not defined]"

    return SectionContent(
        section_id="responder_tracking",
        title="Response Tracking & Classification",
        content=(
            "Response classification follows the SOZO Operational Response Definition. "
            "Assessment occurs at Week 4, Week 8–10, and end-of-block. "
            "Response must be maintained across consistent medication states."
        ),
        subsections=[
            SectionContent(
                section_id="responder_criteria",
                title="Responder Criteria",
                content=criteria_content,
                is_placeholder=not bool(condition.responder_criteria),
            ),
            SectionContent(
                section_id="response_classification",
                title="Response Classification",
                tables=[{
                    "headers": ["Category", "Definition", "Clinical Action"],
                    "rows": [
                        ["Responder", ">=30% improvement in primary outcome measure AND clinically meaningful functional change", "Continue protocol; plan maintenance schedule"],
                        ["Partial Responder", "15-29% improvement OR improvement in secondary but not primary outcome", "Reassess phenotype; consider protocol adjustment at Week 8"],
                        ["Non-Responder", "<15% improvement across all domains at Week 4 AND Week 8", "Initiate FNON Non-Responder Pathway — Level 5 reassessment"],
                    ],
                    "caption": "SOZO response classification framework",
                }],
            ),
            SectionContent(
                section_id="non_responder_pathway",
                title="Non-Responder Pathway (Level 5 — FNON)",
                content=condition.non_responder_pathway or (
                    "For non-responders, initiate Level 5 FNON reassessment:\n"
                    "1. Repeat 6-Network Bedside Assessment\n"
                    "2. Re-evaluate phenotype classification\n"
                    "3. Identify secondary/tertiary network targets\n"
                    "4. Adjust tDCS montage and/or TPS target\n"
                    "5. Consider adjunct modality addition (taVNS, CES)\n"
                    "6. Doctor review mandatory before protocol change"
                ),
            ),
        ],
    )
