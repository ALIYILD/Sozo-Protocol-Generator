"""Tests for PubMed client — uses mocking to avoid network calls.
Skips gracefully when Biopython is not installed."""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock


def test_pubmed_client_initializes():
    """PubMedClient() instantiates without raising even without Biopython."""
    from sozo_generator.evidence.pubmed_client import PubMedClient

    client = PubMedClient()
    assert client is not None


def test_classify_rct_publication_type():
    """_classify_pub_types(['Randomized Controlled Trial']) returns HIGH evidence level."""
    from sozo_generator.evidence.pubmed_client import PubMedClient
    from sozo_generator.core.enums import EvidenceLevel

    client = PubMedClient()
    evidence_type, evidence_level = client._classify_pub_types(["Randomized Controlled Trial"])
    assert evidence_level == EvidenceLevel.HIGH


def test_classify_review_publication_type():
    """_classify_pub_types(['Systematic Review']) returns HIGHEST evidence level."""
    from sozo_generator.evidence.pubmed_client import PubMedClient
    from sozo_generator.core.enums import EvidenceLevel

    client = PubMedClient()
    evidence_type, evidence_level = client._classify_pub_types(["Systematic Review"])
    assert evidence_level == EvidenceLevel.HIGHEST


def test_classify_unknown_publication_type_defaults_to_medium():
    """Unknown pub type defaults to MEDIUM evidence level."""
    from sozo_generator.evidence.pubmed_client import PubMedClient
    from sozo_generator.core.enums import EvidenceLevel

    client = PubMedClient()
    evidence_type, evidence_level = client._classify_pub_types(["Unknown Type"])
    assert evidence_level == EvidenceLevel.MEDIUM


def test_search_without_biopython_returns_empty(tmp_path):
    """When Biopython is not installed, search returns empty list gracefully."""
    from sozo_generator.evidence.pubmed_client import PubMedClient

    client = PubMedClient(cache_dir=tmp_path, force_refresh=True)
    if not client._has_entrez:
        results = client.search("tDCS Parkinson's disease", max_results=5)
        assert results == []
    else:
        pytest.skip("Biopython is installed — this test is for missing-Bio path")


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
