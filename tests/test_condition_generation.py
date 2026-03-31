"""Tests that all 15 condition generators build without errors."""
import pytest


ALL_SLUGS = [
    "parkinsons", "depression", "anxiety", "adhd", "alzheimers",
    "stroke_rehab", "tbi", "chronic_pain", "ptsd", "ocd",
    "ms", "asd", "long_covid", "tinnitus", "insomnia",
]


@pytest.mark.parametrize("slug", ALL_SLUGS)
def test_all_conditions_build(slug):
    """Each condition builder returns a ConditionSchema with matching slug."""
    from sozo_generator.conditions.generators import CONDITION_BUILDERS
    from sozo_generator.schemas.condition import ConditionSchema

    assert slug in CONDITION_BUILDERS, f"No builder found for slug: {slug}"
    condition = CONDITION_BUILDERS[slug]()
    assert isinstance(condition, ConditionSchema)
    assert condition.slug == slug


@pytest.mark.parametrize("slug", ALL_SLUGS)
def test_all_conditions_have_networks(slug):
    """Each built condition has at least one network profile."""
    from sozo_generator.conditions.generators import CONDITION_BUILDERS

    condition = CONDITION_BUILDERS[slug]()
    assert len(condition.network_profiles) >= 1, (
        f"{slug}: expected at least 1 network profile, got {len(condition.network_profiles)}"
    )


@pytest.mark.parametrize("slug", ALL_SLUGS)
def test_all_conditions_have_phenotypes(slug):
    """Each built condition has at least one phenotype."""
    from sozo_generator.conditions.generators import CONDITION_BUILDERS

    condition = CONDITION_BUILDERS[slug]()
    assert len(condition.phenotypes) >= 1, (
        f"{slug}: expected at least 1 phenotype, got {len(condition.phenotypes)}"
    )


@pytest.mark.parametrize("slug", ALL_SLUGS)
def test_all_conditions_have_protocols(slug):
    """Each built condition has at least one protocol."""
    from sozo_generator.conditions.generators import CONDITION_BUILDERS

    condition = CONDITION_BUILDERS[slug]()
    assert len(condition.protocols) >= 1, (
        f"{slug}: expected at least 1 protocol, got {len(condition.protocols)}"
    )


@pytest.mark.parametrize("slug", ALL_SLUGS)
def test_all_conditions_have_references(slug):
    """Each built condition has at least 3 references."""
    from sozo_generator.conditions.generators import CONDITION_BUILDERS

    condition = CONDITION_BUILDERS[slug]()
    assert len(condition.references) >= 3, (
        f"{slug}: expected at least 3 references, got {len(condition.references)}"
    )


@pytest.mark.parametrize("slug", ALL_SLUGS)
def test_all_conditions_have_display_name(slug):
    """Each built condition has a non-empty display_name."""
    from sozo_generator.conditions.generators import CONDITION_BUILDERS

    condition = CONDITION_BUILDERS[slug]()
    assert isinstance(condition.display_name, str) and condition.display_name != "", (
        f"{slug}: display_name is empty or not a string"
    )


def test_registry_returns_condition_schema(registry):
    """registry.get('parkinsons') returns ConditionSchema, not a dict."""
    from sozo_generator.schemas.condition import ConditionSchema

    condition = registry.get("parkinsons")
    assert isinstance(condition, ConditionSchema), (
        f"Expected ConditionSchema, got {type(condition)}"
    )


def test_registry_lists_15_conditions(registry):
    """registry.list_slugs() returns exactly 15 slugs."""
    slugs = registry.list_slugs()
    assert len(slugs) == 15, f"Expected 15 slugs, got {len(slugs)}: {slugs}"
