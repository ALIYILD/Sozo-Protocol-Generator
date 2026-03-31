import logging
import time
from pathlib import Path
from typing import Optional
from Bio import Entrez
from ..core.settings import get_settings
from ..core.enums import EvidenceType, EvidenceLevel
from ..schemas.evidence import ArticleMetadata
from .cache import EvidenceCache
from ..core.utils import clean_abstract, current_date_str

logger = logging.getLogger(__name__)

PUBTYPE_TO_ENUM: dict[str, tuple[EvidenceType, EvidenceLevel]] = {
    "Systematic Review": (EvidenceType.SYSTEMATIC_REVIEW, EvidenceLevel.HIGHEST),
    "Meta-Analysis": (EvidenceType.META_ANALYSIS, EvidenceLevel.HIGHEST),
    "Practice Guideline": (EvidenceType.CLINICAL_PRACTICE_GUIDELINE, EvidenceLevel.HIGHEST),
    "Guideline": (EvidenceType.CLINICAL_PRACTICE_GUIDELINE, EvidenceLevel.HIGHEST),
    "Randomized Controlled Trial": (EvidenceType.RCT, EvidenceLevel.HIGH),
    "Clinical Trial": (EvidenceType.CONTROLLED_TRIAL, EvidenceLevel.HIGH),
    "Review": (EvidenceType.NARRATIVE_REVIEW, EvidenceLevel.MEDIUM),
    "Consensus Development Conference": (EvidenceType.CONSENSUS_STATEMENT, EvidenceLevel.MEDIUM),
    "Case Reports": (EvidenceType.CASE_REPORT, EvidenceLevel.VERY_LOW),
}

LEVEL_SCORES = {
    EvidenceLevel.HIGHEST: 5,
    EvidenceLevel.HIGH: 4,
    EvidenceLevel.MEDIUM: 3,
    EvidenceLevel.LOW: 2,
    EvidenceLevel.VERY_LOW: 1,
}


class PubMedClient:
    """Client for querying PubMed via NCBI Entrez API."""

    def __init__(
        self,
        email: Optional[str] = None,
        api_key: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        force_refresh: bool = False,
    ):
        settings = get_settings()
        Entrez.email = email or settings.ncbi_email
        if api_key or settings.ncbi_api_key:
            Entrez.api_key = api_key or settings.ncbi_api_key
        self.cache = EvidenceCache(cache_dir or settings.cache_dir)
        self.force_refresh = force_refresh
        self._request_delay = 0.34 if Entrez.api_key else 1.0  # NCBI rate limits

    def search(
        self,
        query: str,
        max_results: int = 30,
        publication_types: Optional[list[str]] = None,
        years_back: int = 10,
    ) -> list[ArticleMetadata]:
        """Search PubMed and return structured ArticleMetadata records."""
        cache_key = f"search|{query}|{max_results}|{years_back}"
        if not self.force_refresh:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for query: {query[:60]}")
                return [ArticleMetadata(**a) for a in cached]

        logger.info(f"PubMed search: {query[:80]}")
        pmids = self._esearch(query, max_results, years_back)
        if not pmids:
            logger.info(f"No results for query: {query[:60]}")
            return []

        articles = self._efetch(pmids)
        filtered = self._filter_by_pub_types(articles, publication_types)

        # Cache raw dicts
        self.cache.set(cache_key, [a.model_dump() for a in filtered])
        return filtered

    def _esearch(self, query: str, max_results: int, years_back: int) -> list[str]:
        """Run ESearch and return list of PMIDs."""
        from datetime import datetime
        min_year = datetime.now().year - years_back
        full_query = f"({query}) AND ({min_year}[PDAT]:3000[PDAT])"

        try:
            handle = Entrez.esearch(
                db="pubmed",
                term=full_query,
                retmax=max_results,
                sort="relevance",
                usehistory="n",
            )
            record = Entrez.read(handle)
            handle.close()
            time.sleep(self._request_delay)
            return record.get("IdList", [])
        except Exception as e:
            logger.error(f"ESearch failed: {e}")
            return []

    def _efetch(self, pmids: list[str]) -> list[ArticleMetadata]:
        """Fetch article details for a list of PMIDs."""
        if not pmids:
            return []

        # Fetch in batches of 20
        all_articles: list[ArticleMetadata] = []
        batch_size = 20
        for i in range(0, len(pmids), batch_size):
            batch = pmids[i : i + batch_size]
            try:
                handle = Entrez.efetch(
                    db="pubmed",
                    id=",".join(batch),
                    rettype="xml",
                    retmode="xml",
                )
                records = Entrez.read(handle)
                handle.close()
                time.sleep(self._request_delay)

                for article_set in records.get("PubmedArticle", []):
                    parsed = self._parse_article(article_set)
                    if parsed:
                        all_articles.append(parsed)
            except Exception as e:
                logger.warning(f"EFetch batch {i} failed: {e}")

        return all_articles

    def _parse_article(self, article_set: dict) -> Optional[ArticleMetadata]:
        """Parse a PubMed XML article record into ArticleMetadata."""
        try:
            medline = article_set.get("MedlineCitation", {})
            article = medline.get("Article", {})
            pmid = str(medline.get("PMID", ""))

            # Title
            title = str(article.get("ArticleTitle", ""))

            # Abstract
            abstract_obj = article.get("Abstract", {})
            abstract_texts = abstract_obj.get("AbstractText", [])
            if isinstance(abstract_texts, list):
                abstract = " ".join(str(t) for t in abstract_texts)
            else:
                abstract = str(abstract_texts)
            abstract = clean_abstract(abstract)

            # Journal
            journal_info = article.get("Journal", {})
            journal = str(journal_info.get("Title", ""))

            # Year
            pub_date = journal_info.get("JournalIssue", {}).get("PubDate", {})
            year_str = str(pub_date.get("Year", pub_date.get("MedlineDate", "")[:4]))
            year = int(year_str) if year_str.isdigit() else None

            # Authors
            author_list = article.get("AuthorList", [])
            authors = []
            for a in author_list:
                last = str(a.get("LastName", ""))
                initials = str(a.get("Initials", ""))
                if last:
                    authors.append(f"{last} {initials}".strip())

            # Publication types
            pub_types_raw = [str(pt) for pt in article.get("PublicationTypeList", [])]
            evidence_type, evidence_level = self._classify_pub_types(pub_types_raw)
            score = LEVEL_SCORES.get(evidence_level, 3)

            # DOI
            location_list = article_set.get("PubmedData", {}).get("ArticleIdList", [])
            doi = ""
            for loc in location_list:
                if str(loc.attributes.get("IdType", "")) == "doi":
                    doi = str(loc)
                    break

            return ArticleMetadata(
                pmid=pmid,
                doi=doi or None,
                title=title,
                authors=authors,
                journal=journal,
                year=year,
                abstract=abstract if len(abstract) > 50 else None,
                evidence_type=evidence_type,
                evidence_level=evidence_level,
                score=score,
                cached_at=current_date_str(),
            )
        except Exception as e:
            logger.debug(f"Article parse error: {e}")
            return None

    def _classify_pub_types(self, pub_types: list[str]) -> tuple[EvidenceType, EvidenceLevel]:
        """Map PubMed publication type strings to internal enums."""
        for pt in pub_types:
            for key, (etype, elevel) in PUBTYPE_TO_ENUM.items():
                if key.lower() in pt.lower():
                    return etype, elevel
        return EvidenceType.NARRATIVE_REVIEW, EvidenceLevel.MEDIUM

    def _filter_by_pub_types(
        self,
        articles: list[ArticleMetadata],
        allowed_types: Optional[list[str]],
    ) -> list[ArticleMetadata]:
        if not allowed_types:
            return articles
        allowed_lower = [t.lower() for t in allowed_types]
        return [
            a for a in articles
            if a.evidence_type.value in [t.replace(" ", "_").lower() for t in allowed_types]
            or a.evidence_level in [EvidenceLevel.HIGHEST, EvidenceLevel.HIGH]
        ]
