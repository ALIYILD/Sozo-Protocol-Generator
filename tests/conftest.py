"""Shared pytest fixtures for sozo_generator tests."""
import os
import sys
from pathlib import Path
import pytest

# Default relaxed deployment profile before any code imports auth_config / create_app.
os.environ.setdefault("SOZO_ENV", "development")

# Ensure src/ is on the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def parkinsons_condition():
    from sozo_generator.conditions.generators.parkinsons import build_parkinsons_condition
    return build_parkinsons_condition()


@pytest.fixture(scope="session")
def depression_condition():
    from sozo_generator.conditions.generators.depression import build_depression_condition
    return build_depression_condition()


@pytest.fixture(scope="session")
def registry():
    from sozo_generator.conditions.registry import get_registry
    import sozo_generator.conditions.registry as reg_module
    # Reset singleton to get fresh instance
    reg_module._registry = None
    return reg_module.get_registry()


@pytest.fixture(scope="session")
def all_conditions(registry):
    return [registry.get(slug) for slug in registry.list_slugs()]


@pytest.fixture(scope="session")
def tmp_output(tmp_path_factory):
    return tmp_path_factory.mktemp("outputs")
