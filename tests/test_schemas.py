"""Tests for condition schema validation."""
import pytest


def test_condition_schema_has_required_fields(parkinsons_condition):
    """Slug, display_name, and icd10 are non-empty strings."""
    assert isinstance(parkinsons_condition.slug, str) and parkinsons_condition.slug != ""
    assert isinstance(parkinsons_condition.display_name, str) and parkinsons_condition.display_name != ""
    assert isinstance(parkinsons_condition.icd10, str) and parkinsons_condition.icd10 != ""


def test_network_profiles_non_empty(parkinsons_condition):
    """Parkinson's condition must have at least one network profile."""
    assert len(parkinsons_condition.network_profiles) >= 1


def test_phenotypes_have_key_features(parkinsons_condition):
    """Each phenotype has slug, label, and a key_features list."""
    for phenotype in parkinsons_condition.phenotypes:
        assert isinstance(phenotype.slug, str) and phenotype.slug != ""
        assert isinstance(phenotype.label, str) and phenotype.label != ""
        assert isinstance(phenotype.key_features, list)


def test_assessment_tools_have_scale_key(parkinsons_condition):
    """Each assessment tool has scale_key and name."""
    for tool in parkinsons_condition.assessment_tools:
        assert isinstance(tool.scale_key, str) and tool.scale_key != ""
        assert isinstance(tool.name, str) and tool.name != ""


def test_protocols_have_id_and_label(parkinsons_condition):
    """Each protocol has protocol_id and label."""
    for protocol in parkinsons_condition.protocols:
        assert isinstance(protocol.protocol_id, str) and protocol.protocol_id != ""
        assert isinstance(protocol.label, str) and protocol.label != ""


def test_stimulation_targets_have_region(parkinsons_condition):
    """Each stimulation target has target_region and modality."""
    for target in parkinsons_condition.stimulation_targets:
        assert isinstance(target.target_region, str) and target.target_region != ""
        assert target.modality is not None


def test_network_profile_severity_is_string(parkinsons_condition):
    """NetworkProfile.severity must be a string."""
    for profile in parkinsons_condition.network_profiles:
        assert isinstance(profile.severity, str)


def test_schema_serializes_to_json(parkinsons_condition):
    """ConditionSchema.model_dump_json() works without error."""
    json_str = parkinsons_condition.model_dump_json()
    assert isinstance(json_str, str)
    assert len(json_str) > 0
