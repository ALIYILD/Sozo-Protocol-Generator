"""Citation management for document sections."""
import logging
from ..schemas.documents import SectionContent
from ..core.utils import format_authors

logger = logging.getLogger(__name__)


def format_citation_inline(article) -> str:
    """Return inline citation string from an ArticleMetadata object."""
    authors = format_authors(article.authors, max_authors=2)
    year = article.year or "n.d."
    if article.pmid and not str(article.pmid).startswith("placeholder"):
        return f"({authors}, {year}; PMID: {article.pmid})"
    return f"({authors}, {year})"


def format_reference_entry(article, index: int) -> str:
    """Return full reference list entry from an ArticleMetadata object."""
    authors = ", ".join(article.authors[:6])
    if len(article.authors) > 6:
        authors += " et al."
    year = article.year or "n.d."
    line = f"{index}. {authors} ({year}). {article.title}."
    if article.journal:
        line += f" {article.journal}."
    if article.pmid and not str(article.pmid).startswith("placeholder"):
        line += f" PMID: {article.pmid}."
    if article.doi:
        line += f" DOI: {article.doi}."
    return line


def inject_citations(
    sections: list,
    dossier=None,
) -> list:
    """Inject evidence PMIDs into sections from a dossier if available."""
    if not dossier:
        return sections
    try:
        claim_map = {c.category.value: c for c in dossier.claims}
    except Exception:
        return sections

    for section in sections:
        if section.section_id in claim_map:
            claim = claim_map[section.section_id]
            try:
                section.evidence_pmids = claim.supporting_pmids[:5]
                section.confidence_label = claim.confidence.value
            except Exception:
                pass
    return sections
