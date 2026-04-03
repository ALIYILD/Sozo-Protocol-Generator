"""Tests for PMID validation across all schema models."""
import pytest

from sozo_generator.schemas.validators import validate_pmid, validate_pmid_list
from sozo_generator.schemas.evidence import ArticleMetadata, EvidenceClaim
from sozo_generator.schemas.contracts import EvidenceItem, ClaimCitationLink
from sozo_generator.schemas.condition import AssessmentTool
from sozo_generator.core.enums import (
    ClaimCategory,
    ConfidenceLabel,
    EvidenceLevel,
)


# ── validate_pmid unit tests ────────────────────────────────────────────────


class TestValidatePmid:
    def test_valid_8_digit(self):
        assert validate_pmid("12345678") == "12345678"

    def test_valid_7_digit(self):
        assert validate_pmid("1234567") == "1234567"

    def test_valid_1_digit(self):
        assert validate_pmid("1") == "1"

    def test_valid_9_digit(self):
        assert validate_pmid("123456789") == "123456789"

    def test_none_returns_none(self):
        assert validate_pmid(None) is None

    def test_empty_string_returns_none(self):
        assert validate_pmid("") is None

    def test_whitespace_returns_none(self):
        assert validate_pmid("   ") is None

    def test_strips_whitespace(self):
        assert validate_pmid(" 12345678 ") == "12345678"

    def test_rejects_non_numeric(self):
        with pytest.raises(ValueError, match="Invalid PMID"):
            validate_pmid("abc123")

    def test_rejects_mixed_alpha_numeric(self):
        with pytest.raises(ValueError, match="Invalid PMID"):
            validate_pmid("PMID12345")

    def test_rejects_10_digits(self):
        with pytest.raises(ValueError, match="Invalid PMID"):
            validate_pmid("1234567890")

    def test_rejects_negative(self):
        with pytest.raises(ValueError, match="Invalid PMID"):
            validate_pmid("-12345")

    def test_rejects_decimal(self):
        with pytest.raises(ValueError, match="Invalid PMID"):
            validate_pmid("123.456")


# ── validate_pmid_list unit tests ───────────────────────────────────────────


class TestValidatePmidList:
    def test_filters_empty_strings(self):
        assert validate_pmid_list(["12345678", "", "87654321"]) == [
            "12345678",
            "87654321",
        ]

    def test_empty_list(self):
        assert validate_pmid_list([]) == []

    def test_all_valid(self):
        result = validate_pmid_list(["11111111", "22222222", "33333333"])
        assert len(result) == 3

    def test_strips_whitespace(self):
        assert validate_pmid_list([" 12345 ", "  67890  "]) == ["12345", "67890"]

    def test_filters_whitespace_only(self):
        assert validate_pmid_list(["", "  ", "12345678"]) == ["12345678"]


# ── ArticleMetadata integration ─────────────────────────────────────────────


class TestArticleMetadataPmid:
    def test_valid_pmid(self):
        a = ArticleMetadata(title="Test", pmid="19343477")
        assert a.pmid == "19343477"

    def test_none_pmid(self):
        a = ArticleMetadata(title="Test", pmid=None)
        assert a.pmid is None

    def test_empty_pmid_becomes_none(self):
        a = ArticleMetadata(title="Test", pmid="")
        assert a.pmid is None

    def test_invalid_pmid_raises(self):
        with pytest.raises(Exception, match="Invalid PMID"):
            ArticleMetadata(title="Test", pmid="not_a_pmid")

    def test_no_pmid_field(self):
        a = ArticleMetadata(title="Test")
        assert a.pmid is None


# ── EvidenceItem integration ────────────────────────────────────────────────


class TestEvidenceItemPmid:
    def test_valid_pmid(self):
        ei = EvidenceItem(pmid="99999999")
        assert ei.pmid == "99999999"

    def test_invalid_raises(self):
        with pytest.raises(Exception, match="Invalid PMID"):
            EvidenceItem(pmid="bad")


# ── ClaimCitationLink integration ───────────────────────────────────────────


class TestClaimCitationLinkPmids:
    def test_filters_empty_pmids(self):
        ccl = ClaimCitationLink(
            claim_id="c1",
            claim_text="some claim",
            category=ClaimCategory.PATHOPHYSIOLOGY,
            confidence=ConfidenceLabel.HIGH,
            pmids=["12345678", "", "87654321"],
        )
        assert ccl.pmids == ["12345678", "87654321"]

    def test_empty_list(self):
        ccl = ClaimCitationLink(
            claim_id="c2",
            claim_text="test",
            category=ClaimCategory.SAFETY,
            confidence=ConfidenceLabel.MEDIUM,
            pmids=[],
        )
        assert ccl.pmids == []


# ── AssessmentTool integration ──────────────────────────────────────────────


class TestAssessmentToolPmid:
    def test_valid_evidence_pmid(self):
        at = AssessmentTool(
            scale_key="phq9",
            name="PHQ-9",
            abbreviation="PHQ-9",
            evidence_pmid="11556941",
        )
        assert at.evidence_pmid == "11556941"

    def test_none_evidence_pmid(self):
        at = AssessmentTool(
            scale_key="test",
            name="Test",
            abbreviation="T",
        )
        assert at.evidence_pmid is None

    def test_invalid_evidence_pmid_raises(self):
        with pytest.raises(Exception, match="Invalid PMID"):
            AssessmentTool(
                scale_key="test",
                name="Test",
                abbreviation="T",
                evidence_pmid="invalid",
            )
