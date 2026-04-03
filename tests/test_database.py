"""Tests for SQLite database and upload extraction pipeline."""
import pytest
from pathlib import Path


class TestSozoDB:
    @pytest.fixture
    def db(self, tmp_path):
        from sozo_api.db.database import SozoDB
        db = SozoDB(tmp_path / "test.db")
        db.init_schema()
        return db

    def test_init_schema(self, db):
        stats = db.stats()
        assert stats["users"] == 0
        assert stats["protocols"] == 0

    def test_create_user(self, db):
        user = db.create_user("dr@sozo.com", "Dr. Smith", "password123", "clinician")
        assert user["id"].startswith("user-")
        assert user["role"] == "clinician"

    def test_authenticate(self, db):
        db.create_user("dr@sozo.com", "Dr. Smith", "secret123")
        user = db.authenticate("dr@sozo.com", "secret123")
        assert user is not None
        assert user["name"] == "Dr. Smith"

    def test_auth_wrong_password(self, db):
        db.create_user("dr@sozo.com", "Dr. Smith", "secret123")
        assert db.authenticate("dr@sozo.com", "wrong") is None

    def test_create_protocol(self, db):
        proto = db.create_protocol(
            name="PD Protocol",
            condition_slug="parkinsons",
            tier="fellow",
            doc_type="evidence_based_protocol",
            source="generated",
            schema_json={"condition": "parkinsons", "protocols": []},
        )
        assert proto["id"].startswith("proto-")
        assert proto["status"] == "draft"

    def test_get_protocol(self, db):
        proto = db.create_protocol("Test", "depression", "fellow", "handbook", "generated", {"test": True})
        loaded = db.get_protocol(proto["id"])
        assert loaded is not None
        assert loaded["schema_json"]["test"] is True

    def test_list_protocols(self, db):
        db.create_protocol("P1", "parkinsons", "fellow", "handbook", "generated", {})
        db.create_protocol("P2", "depression", "fellow", "handbook", "generated", {})
        db.create_protocol("P3", "parkinsons", "partners", "handbook", "generated", {})

        all_protos = db.list_protocols()
        assert len(all_protos) == 3

        pd_protos = db.list_protocols(condition="parkinsons")
        assert len(pd_protos) == 2

    def test_upsert_evidence(self, db):
        ev_id = db.upsert_evidence("32180044", "tDCS in PD: Systematic Review", evidence_level="highest")
        assert ev_id == "ev-32180044"

        # Upsert same PMID returns same ID
        ev_id2 = db.upsert_evidence("32180044", "Different title")
        assert ev_id2 == ev_id

    def test_attach_evidence(self, db):
        proto = db.create_protocol("Test", "parkinsons", "fellow", "ebp", "generated", {})
        db.upsert_evidence("32180044", "tDCS Review")
        db.attach_evidence(proto["id"], "ev-32180044", "protocols_tdcs")

        evidence = db.get_protocol_evidence(proto["id"])
        assert len(evidence) == 1
        assert evidence[0]["pmid"] == "32180044"

    def test_create_review(self, db):
        user = db.create_user("dr@sozo.com", "Dr. Smith", "pass")
        proto = db.create_protocol("Test", "parkinsons", "fellow", "ebp", "generated", {})
        rev_id = db.create_review(proto["id"], user["id"], "approve", "Looks good")

        # Protocol should now be approved
        loaded = db.get_protocol(proto["id"])
        assert loaded["status"] == "approved"

    def test_audit_log(self, db):
        db.create_user("dr@sozo.com", "Dr. Smith", "pass")
        log = db.get_audit_log()
        assert len(log) >= 1
        assert log[0]["action"] == "create_user"

    def test_upload_lifecycle(self, db):
        up_id = db.create_upload("test.docx", "docx", 1024)
        upload = db.get_upload(up_id)
        assert upload["extraction_status"] == "pending"

        db.update_upload_extraction(up_id, "extracted", {"condition": "parkinsons"})
        updated = db.get_upload(up_id)
        assert updated["extraction_status"] == "extracted"
        assert updated["extracted_schema"]["condition"] == "parkinsons"


class TestProtocolExtractor:
    def test_extract_docx(self):
        """Test extraction from the test fixture DOCX."""
        from sozo_api.upload.extractor import ProtocolExtractor
        fixture = Path("tests/fixtures/reviewed_parkinsons.docx")
        if not fixture.exists():
            pytest.skip("Test fixture not available")

        extractor = ProtocolExtractor()
        result = extractor.extract(str(fixture))
        assert result.success or result.raw_text  # At least got text
        assert len(result.chunks) >= 1

    def test_extract_txt(self, tmp_path):
        """Test extraction from plain text."""
        from sozo_api.upload.extractor import ProtocolExtractor

        txt_file = tmp_path / "protocol.txt"
        txt_file.write_text("""
        Parkinson's Disease tDCS Protocol

        This protocol uses transcranial direct current stimulation (tDCS)
        targeting bilateral M1 at 2 mA for 20 minutes.

        Contraindications include metal implants and active epilepsy.

        References: PMID: 32180044, PMID: 20801741
        """)

        extractor = ProtocolExtractor()
        result = extractor.extract(str(txt_file))
        assert result.success
        assert result.assembled_schema["condition"]["slug"] == "parkinsons"
        assert len(result.assembled_schema["modalities"]) >= 1
        assert len(result.assembled_schema["references"]) >= 1

    def test_extract_detects_condition(self, tmp_path):
        from sozo_api.upload.extractor import ProtocolExtractor

        txt = tmp_path / "dep.txt"
        txt.write_text("Major Depressive Disorder treatment protocol using tDCS targeting L-DLPFC at 2mA.")

        result = ProtocolExtractor().extract(str(txt))
        assert result.assembled_schema["condition"]["slug"] == "depression"

    def test_extract_detects_pmids(self, tmp_path):
        from sozo_api.upload.extractor import ProtocolExtractor

        txt = tmp_path / "refs.txt"
        txt.write_text("Evidence from PMID: 12345678 and PMID: 87654321 supports this approach for Parkinson's.")

        result = ProtocolExtractor().extract(str(txt))
        pmids = [r["pmid"] for r in result.assembled_schema.get("references", [])]
        assert "12345678" in pmids
        assert "87654321" in pmids

    def test_unsupported_file_type(self, tmp_path):
        from sozo_api.upload.extractor import ProtocolExtractor

        f = tmp_path / "test.xyz"
        f.write_text("data")
        result = ProtocolExtractor().extract(str(f))
        assert not result.success
        assert "Unsupported" in result.error

    def test_empty_file(self, tmp_path):
        from sozo_api.upload.extractor import ProtocolExtractor

        f = tmp_path / "empty.txt"
        f.write_text("")
        result = ProtocolExtractor().extract(str(f))
        assert not result.success
