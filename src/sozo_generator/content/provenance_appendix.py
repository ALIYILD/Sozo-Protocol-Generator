"""Evidence provenance appendix builder."""
import logging
from ..schemas.documents import SectionContent

logger = logging.getLogger(__name__)


def build_provenance_appendix(dossier) -> SectionContent:
    """Build an evidence provenance appendix section from an EvidenceDossier."""
    rows = []
    try:
        claims = dossier.claims[:20]
        for claim in claims:
            try:
                pmids = ", ".join(claim.supporting_pmids[:3]) if claim.supporting_pmids else "None"
                rows.append([
                    claim.category.value.replace("_", " ").title(),
                    claim.confidence.value.replace("_", " ").title(),
                    claim.evidence_level.value if hasattr(claim, "evidence_level") and claim.evidence_level else "N/A",
                    pmids,
                    "Yes" if getattr(claim, "requires_review", False) else "No",
                ])
            except Exception as e:
                logger.warning(f"Could not serialize claim: {e}")
    except Exception as e:
        logger.warning(f"Could not read dossier claims: {e}")

    condition_name = getattr(dossier, "condition_name", "Unknown")
    generated_at = getattr(dossier, "generated_at", "")
    total_sources = getattr(dossier, "total_sources", 0)

    return SectionContent(
        section_id="provenance_appendix",
        title="Evidence Provenance Appendix",
        content=(
            f"Evidence dossier for {condition_name}. "
            f"Generated: {generated_at}. "
            f"Total sources: {total_sources}."
        ),
        tables=[{
            "headers": ["Clinical Domain", "Confidence", "Evidence Level", "Key PMIDs", "Review Required"],
            "rows": rows,
            "caption": "Evidence provenance by clinical domain",
        }] if rows else [],
    )
