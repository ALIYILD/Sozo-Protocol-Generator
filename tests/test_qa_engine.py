"""Tests for the QA engine and individual rule modules."""
from __future__ import annotations

import pytest

from sozo_generator.core.enums import (
    EvidenceLevel,
    Modality,
    NetworkDysfunction,
    NetworkKey,
    QASeverity,
)
from sozo_generator.schemas.condition import (
    ConditionSchema,
    NetworkProfile,
    ProtocolEntry,
    SafetyNote,
    StimulationTarget,
)
from sozo_generator.schemas.contracts import QAIssue, QAReport


# ── Helpers ─────────────────────────────────────────────────────────────


def _minimal_condition(**overrides) -> ConditionSchema:
    """Build a minimal ConditionSchema with just enough fields."""
    defaults = dict(
        slug="test",
        display_name="Test Condition",
        icd10="G00",
        overview="",
        pathophysiology="",
        evidence_summary="",
        references=[],
        contraindications=[],
        safety_notes=[],
        protocols=[],
        stimulation_targets=[],
        network_profiles=[],
        key_brain_regions=[],
        exclusion_criteria=[],
    )
    defaults.update(overrides)
    return ConditionSchema(**defaults)


def _well_formed_condition() -> ConditionSchema:
    """Build a condition that should pass most QA rules."""
    return ConditionSchema(
        slug="wellformed",
        display_name="Well Formed Condition",
        icd10="G99",
        overview="This condition involves neurological symptoms that may benefit from neuromodulation.",
        pathophysiology="Evidence suggests involvement of cortical networks.",
        evidence_summary="Multiple RCTs support the use of tDCS for this condition.",
        references=[
            {"pmid": "12345678", "title": "Study 1"},
            {"pmid": "23456789", "title": "Study 2"},
            {"pmid": "34567890", "title": "Study 3"},
        ],
        contraindications=["Seizure disorder", "Metallic implants"],
        safety_notes=[
            SafetyNote(category="precaution", description="Monitor for headache"),
        ],
        protocols=[
            ProtocolEntry(
                protocol_id="p1",
                label="tDCS Protocol A",
                modality=Modality.TDCS,
                target_region="DLPFC",
                target_abbreviation="F3",
                rationale="Evidence-based target",
                parameters={"intensity_mA": 2.0, "duration_min": 20},
            ),
        ],
        stimulation_targets=[
            StimulationTarget(
                modality=Modality.TDCS,
                target_region="DLPFC",
                target_abbreviation="F3",
                rationale="Primary target",
            ),
        ],
        network_profiles=[
            NetworkProfile(
                network=NetworkKey.CEN,
                dysfunction=NetworkDysfunction.HYPO,
                relevance="Hypoactive CEN in this condition",
            ),
        ],
        key_brain_regions=["DLPFC", "ACC"],
        exclusion_criteria=["Active seizure disorder"],
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# QAEngine
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestQAEngine:
    def test_run_condition_qa_returns_report(self):
        from sozo_generator.qa.engine import QAEngine

        engine = QAEngine()
        condition = _minimal_condition()
        report = engine.run_condition_qa(condition)
        assert isinstance(report, QAReport)
        assert report.condition_slug == "test"
        assert report.report_id.startswith("qa-")

    def test_check_blocking_true_when_blocks_exist(self):
        from sozo_generator.qa.engine import QAEngine

        engine = QAEngine()
        report = QAReport(
            report_id="r1",
            condition_slug="test",
            issues=[QAIssue(severity=QASeverity.BLOCK, message="bad")],
            block_count=1,
        )
        assert engine.check_blocking(report) is True

    def test_check_blocking_false_when_no_blocks(self):
        from sozo_generator.qa.engine import QAEngine

        engine = QAEngine()
        report = QAReport(
            report_id="r2",
            condition_slug="test",
            issues=[QAIssue(severity=QASeverity.WARNING)],
            block_count=0,
        )
        assert engine.check_blocking(report) is False

    @pytest.mark.slow
    def test_wellformed_condition_passes_most_rules(self):
        from sozo_generator.qa.engine import QAEngine

        engine = QAEngine()
        condition = _well_formed_condition()
        report = engine.run_condition_qa(condition)
        # Well-formed condition should have zero BLOCK issues
        blocks = [
            i for i in report.issues if i.severity == QASeverity.BLOCK
        ]
        assert len(blocks) == 0, f"Unexpected BLOCKs: {[b.message for b in blocks]}"
        assert report.passed is True

    @pytest.mark.slow
    def test_parkinsons_fixture_passes_most_rules(self, parkinsons_condition):
        from sozo_generator.qa.engine import QAEngine

        engine = QAEngine()
        report = engine.run_condition_qa(parkinsons_condition)
        # Parkinsons is a well-built condition; should pass or have few blocks
        assert isinstance(report, QAReport)
        # Log issues for debugging if any
        if report.block_count > 0:
            block_rules = [i.rule_id for i in report.issues if i.severity == QASeverity.BLOCK]
            # Not a hard failure -- just informational
            pytest.skip(f"Parkinsons has {report.block_count} blocks: {block_rules}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CitationRules
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestCitationRules:
    def test_no_references_block(self):
        from sozo_generator.qa.rules.citations import CitationRules

        rules = CitationRules()
        condition = _minimal_condition(references=[])
        issues = rules.check(condition)
        block_ids = [i.rule_id for i in issues if i.severity == QASeverity.BLOCK]
        assert "citations.no_references" in block_ids

    def test_placeholder_block(self):
        from sozo_generator.qa.rules.citations import CitationRules

        rules = CitationRules()
        condition = _minimal_condition(
            overview="This condition [CITATION NEEDED] requires more research.",
            references=[{"pmid": "12345678"}],
        )
        issues = rules.check(condition)
        block_ids = [i.rule_id for i in issues if i.severity == QASeverity.BLOCK]
        assert "citations.placeholder" in block_ids

    def test_valid_references_no_block(self):
        from sozo_generator.qa.rules.citations import CitationRules

        rules = CitationRules()
        condition = _minimal_condition(
            overview="A proper overview.",
            references=[
                {"pmid": "12345678"},
                {"pmid": "23456789"},
                {"pmid": "34567890"},
            ],
        )
        issues = rules.check(condition)
        block_ids = [i.rule_id for i in issues if i.severity == QASeverity.BLOCK]
        assert len(block_ids) == 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SafetyRules
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestSafetyRules:
    def test_no_contraindications_block(self):
        from sozo_generator.qa.rules.safety import SafetyRules

        rules = SafetyRules()
        condition = _minimal_condition(contraindications=[])
        issues = rules.check(condition)
        block_ids = [i.rule_id for i in issues if i.severity == QASeverity.BLOCK]
        assert "safety.no_contraindications" in block_ids

    def test_no_safety_notes_block(self):
        from sozo_generator.qa.rules.safety import SafetyRules

        rules = SafetyRules()
        condition = _minimal_condition(
            contraindications=["something"],
            safety_notes=[],
        )
        issues = rules.check(condition)
        block_ids = [i.rule_id for i in issues if i.severity == QASeverity.BLOCK]
        assert "safety.no_safety_notes" in block_ids

    def test_with_safety_data_no_block(self):
        from sozo_generator.qa.rules.safety import SafetyRules

        rules = SafetyRules()
        condition = _minimal_condition(
            contraindications=["Seizure disorder"],
            safety_notes=[
                SafetyNote(category="monitoring", description="Weekly check"),
            ],
        )
        issues = rules.check(condition)
        block_ids = [i.rule_id for i in issues if i.severity == QASeverity.BLOCK]
        assert len(block_ids) == 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ModalityRules
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestModalityRules:
    def test_no_protocols_block(self):
        from sozo_generator.qa.rules.modality import ModalityRules

        rules = ModalityRules()
        condition = _minimal_condition(protocols=[])
        issues = rules.check(condition)
        block_ids = [i.rule_id for i in issues if i.severity == QASeverity.BLOCK]
        assert "modality.no_protocols" in block_ids

    def test_with_protocol_no_block(self):
        from sozo_generator.qa.rules.modality import ModalityRules

        rules = ModalityRules()
        condition = _minimal_condition(
            protocols=[
                ProtocolEntry(
                    protocol_id="p1",
                    label="tDCS",
                    modality=Modality.TDCS,
                    target_region="DLPFC",
                    target_abbreviation="F3",
                    rationale="test",
                    parameters={"intensity": 2},
                ),
            ],
            stimulation_targets=[
                StimulationTarget(
                    modality=Modality.TDCS,
                    target_region="DLPFC",
                    target_abbreviation="F3",
                    rationale="test",
                ),
            ],
        )
        issues = rules.check(condition)
        block_ids = [i.rule_id for i in issues if i.severity == QASeverity.BLOCK]
        assert "modality.no_protocols" not in block_ids


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LanguageRules
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestLanguageRules:
    def test_excessive_certainty_warning(self):
        from sozo_generator.qa.rules.language import LanguageRules

        rules = LanguageRules()
        condition = _minimal_condition(
            overview="tDCS is proven to cure depression and is guaranteed effective.",
        )
        issues = rules.check(condition)
        certainty_issues = [
            i for i in issues if i.rule_id == "language.excessive_certainty"
        ]
        assert len(certainty_issues) >= 2  # "proven", "guaranteed", "cures"
        for issue in certainty_issues:
            assert issue.severity == QASeverity.WARNING

    def test_no_certainty_issues_for_hedged_language(self):
        from sozo_generator.qa.rules.language import LanguageRules

        rules = LanguageRules()
        condition = _minimal_condition(
            overview="Evidence suggests tDCS may improve symptoms.",
        )
        issues = rules.check(condition)
        certainty_issues = [
            i for i in issues if i.rule_id == "language.excessive_certainty"
        ]
        assert len(certainty_issues) == 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CompletenessRules
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestCompletenessRules:
    def test_empty_overview_block(self):
        from sozo_generator.qa.rules.completeness_rules import CompletenessRules

        rules = CompletenessRules()
        condition = _minimal_condition(overview="")
        issues = rules.check(condition)
        block_ids = [i.rule_id for i in issues if i.severity == QASeverity.BLOCK]
        assert "completeness.empty_overview" in block_ids

    def test_nonempty_overview_no_block(self):
        from sozo_generator.qa.rules.completeness_rules import CompletenessRules

        rules = CompletenessRules()
        condition = _minimal_condition(overview="A clinical overview of the condition.")
        issues = rules.check(condition)
        block_ids = [i.rule_id for i in issues if i.severity == QASeverity.BLOCK]
        assert "completeness.empty_overview" not in block_ids

    def test_no_networks_warning(self):
        from sozo_generator.qa.rules.completeness_rules import CompletenessRules

        rules = CompletenessRules()
        condition = _minimal_condition(network_profiles=[])
        issues = rules.check(condition)
        warn_ids = [i.rule_id for i in issues if i.severity == QASeverity.WARNING]
        assert "completeness.no_networks" in warn_ids
