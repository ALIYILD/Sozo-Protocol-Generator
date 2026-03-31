"""Tests for PubMed client — uses mocking to avoid network calls."""
import pytest
from unittest.mock import patch, MagicMock


def test_pubmed_client_initializes():
    """PubMedClient() instantiates without raising an error."""
    from sozo_generator.evidence.pubmed_client import PubMedClient

    client = PubMedClient()
    assert client is not None


def test_classify_rct_publication_type():
    """_classify_pub_types(['Randomized Controlled Trial']) returns HIGH evidence level."""
    from sozo_generator.evidence.pubmed_client import PubMedClient
    from sozo_generator.core.enums import EvidenceLevel

    client = PubMedClient()
    evidence_type, evidence_level = client._classify_pub_types(["Randomized Controlled Trial"])
    assert evidence_level == EvidenceLevel.HIGH, (
        f"Expected HIGH for RCT, got {evidence_level}"
    )


def test_classify_review_publication_type():
    """_classify_pub_types(['Systematic Review']) returns HIGHEST evidence level."""
    from sozo_generator.evidence.pubmed_client import PubMedClient
    from sozo_generator.core.enums import EvidenceLevel

    client = PubMedClient()
    evidence_type, evidence_level = client._classify_pub_types(["Systematic Review"])
    assert evidence_level == EvidenceLevel.HIGHEST, (
        f"Expected HIGHEST for Systematic Review, got {evidence_level}"
    )


def test_classify_unknown_publication_type_defaults_to_medium():
    """Unknown pub type defaults to MEDIUM evidence level."""
    from sozo_generator.evidence.pubmed_client import PubMedClient
    from sozo_generator.core.enums import EvidenceLevel

    client = PubMedClient()
    evidence_type, evidence_level = client._classify_pub_types(["Unknown Type"])
    assert evidence_level == EvidenceLevel.MEDIUM, (
        f"Expected MEDIUM for unknown pub type, got {evidence_level}"
    )


def test_search_returns_list(monkeypatch, tmp_path):
    """search() with mocked Entrez returns a list (may be empty if cache misses)."""
    from sozo_generator.evidence.pubmed_client import PubMedClient
    from sozo_generator.schemas.evidence import ArticleMetadata

    # Build a minimal mock for Entrez.esearch that returns no PMIDs
    mock_search_handle = MagicMock()
    mock_search_record = {"IdList": []}

    def mock_esearch(**kwargs):
        return mock_search_handle

    def mock_read(handle):
        return mock_search_record

    monkeypatch.setattr("Bio.Entrez.esearch", mock_esearch)
    monkeypatch.setattr("Bio.Entrez.read", mock_read)

    client = PubMedClient(cache_dir=tmp_path, force_refresh=True)
    results = client.search("tDCS Parkinson's disease", max_results=5)

    assert isinstance(results, list), f"Expected list, got {type(results)}"


def test_search_returns_articles_from_cache(tmp_path):
    """search() returns ArticleMetadata objects when cache is populated."""
    from sozo_generator.evidence.pubmed_client import PubMedClient
    from sozo_generator.schemas.evidence import ArticleMetadata
    from sozo_generator.core.enums import EvidenceLevel
    from sozo_generator.evidence.cache import EvidenceCache

    # Pre-populate cache with one article
    cache = EvidenceCache(tmp_path)
    article_data = [
        ArticleMetadata(
            pmid="99999999",
            title="Cached tDCS article",
            evidence_level=EvidenceLevel.HIGH,
        ).model_dump()
    ]
    cache_key = "search|tDCS cached test|10|10"
    cache.set(cache_key, article_data)

    client = PubMedClient(cache_dir=tmp_path, force_refresh=False)
    results = client.search("tDCS cached test", max_results=10, years_back=10)

    assert isinstance(results, list)
    assert len(results) == 1
    assert isinstance(results[0], ArticleMetadata)
    assert results[0].pmid == "99999999"
