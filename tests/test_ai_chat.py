"""Tests for AI chat engine, intent parser, and document composer."""
from __future__ import annotations

import pytest
from pathlib import Path


# ── Intent parser tests ──────────────────────────────────────────────────

class TestIntentParser:
    def _parse(self, text):
        from sozo_generator.ai.intent_parser import parse_intent_rules
        return parse_intent_rules(text)

    def test_generate_single_condition(self):
        intent = self._parse("Generate documents for Parkinson's disease")
        assert intent.action == "generate"
        assert "parkinsons" in intent.conditions

    def test_generate_multiple_conditions(self):
        intent = self._parse("Create protocols for depression and anxiety")
        assert "depression" in intent.conditions
        assert "anxiety" in intent.conditions

    def test_generate_all_conditions(self):
        intent = self._parse("Generate all 15 conditions")
        assert intent.all_conditions is True

    def test_specific_doc_type(self):
        intent = self._parse("Build evidence-based protocol for ADHD")
        assert "evidence_based_protocol" in intent.doc_types
        assert "adhd" in intent.conditions

    def test_merge_action(self):
        intent = self._parse("Merge handbook and protocol for OCD")
        assert intent.action == "merge"
        assert intent.merge_request is True
        assert "ocd" in intent.conditions

    def test_list_action(self):
        intent = self._parse("List all conditions")
        assert intent.action == "list"

    def test_explain_action(self):
        intent = self._parse("Tell me about Alzheimer's")
        assert intent.action == "explain"
        assert "alzheimers" in intent.conditions

    def test_qa_action(self):
        intent = self._parse("Run QA checks on depression")
        assert intent.action == "qa"
        assert "depression" in intent.conditions

    def test_help_action(self):
        intent = self._parse("help")
        assert intent.action == "help"

    def test_tier_detection_fellow(self):
        intent = self._parse("Generate handbook for TBI, fellow tier")
        assert intent.tier == "fellow"

    def test_tier_detection_partners(self):
        intent = self._parse("Create all docs for MS, partners")
        assert intent.tier == "partners"

    def test_alias_resolution_mdd(self):
        intent = self._parse("Build protocol for MDD")
        assert "depression" in intent.conditions

    def test_alias_resolution_pd(self):
        intent = self._parse("Generate docs for PD")
        assert "parkinsons" in intent.conditions

    def test_alias_post_stroke(self):
        intent = self._parse("Create handbook for post-stroke rehabilitation")
        assert "stroke_rehab" in intent.conditions

    def test_alias_long_covid(self):
        intent = self._parse("Build protocol for long covid brain fog")
        assert "long_covid" in intent.conditions

    def test_alias_fibromyalgia(self):
        intent = self._parse("Generate for fibromyalgia")
        assert "chronic_pain" in intent.conditions

    def test_confidence_high_for_clear_request(self):
        intent = self._parse("Generate all documents for Parkinson's")
        assert intent.confidence >= 0.8

    def test_is_generation_request(self):
        intent = self._parse("Create protocol for PTSD")
        assert intent.is_generation_request is True

    def test_non_generation_request(self):
        intent = self._parse("List document types")
        assert intent.is_generation_request is False

    def test_summary_string(self):
        intent = self._parse("Generate handbook for insomnia")
        summary = intent.summary
        assert "generate" in summary.lower() or "Action: generate" in summary


# ── Chat engine tests ────────────────────────────────────────────────────

class TestChatEngine:
    @pytest.fixture
    def engine(self, tmp_path):
        from sozo_generator.ai.chat_engine import ChatEngine
        return ChatEngine(output_dir=str(tmp_path / "outputs"))

    def test_generate_produces_files(self, engine):
        response = engine.process_message("Generate evidence-based protocol for depression")
        assert response.success is True
        assert len(response.files) > 0
        assert response.action_taken == "generate"

    def test_list_conditions(self, engine):
        response = engine.process_message("List all conditions")
        assert response.success is True
        assert "parkinsons" in response.message.lower() or "Parkinson" in response.message

    def test_explain_condition(self, engine):
        response = engine.process_message("Explain anxiety")
        assert response.success is True
        assert "anxiety" in response.message.lower() or "GAD" in response.message

    def test_help(self, engine):
        response = engine.process_message("help")
        assert response.success is True
        assert "Generate" in response.message

    def test_qa_check(self, engine):
        response = engine.process_message("Run QA on parkinsons")
        assert response.success is True
        assert response.action_taken == "qa"

    def test_unknown_input(self, engine):
        response = engine.process_message("asdfghjkl random gibberish")
        # Should handle gracefully
        assert response.message  # has some response

    def test_merge_produces_file(self, engine):
        response = engine.process_message("Merge handbook and evidence-based protocol for ADHD")
        assert response.success is True
        assert len(response.files) >= 1
        assert response.action_taken == "merge"

    def test_generate_all_conditions(self, engine):
        response = engine.process_message("Build all conditions")
        assert response.success is True
        assert len(response.files) >= 15  # at least 1 per condition


# ── DocComposer tests ────────────────────────────────────────────────────

class TestDocComposer:
    @pytest.fixture
    def composer(self, tmp_path):
        from sozo_generator.ai.doc_composer import DocComposer
        return DocComposer(output_dir=str(tmp_path / "outputs"))

    def test_generate_standard(self, composer, parkinsons_condition):
        outputs = composer.generate_standard(
            parkinsons_condition,
            doc_types=["evidence_based_protocol"],
            tier="fellow",
        )
        assert len(outputs) >= 1
        for path in outputs.values():
            assert Path(path).exists()

    def test_merge_documents(self, composer, parkinsons_condition):
        merged = composer.merge_documents(
            condition=parkinsons_condition,
            doc_types_to_merge=["handbook", "evidence_based_protocol"],
            tier="fellow",
        )
        assert merged.exists()
        assert merged.stat().st_size > 5000

    def test_generate_all_for_condition(self, composer, parkinsons_condition):
        outputs = composer.generate_all_for_condition(
            parkinsons_condition,
            tier="fellow",
        )
        assert len(outputs) >= 1  # at least some docs generated
