from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from sozo_auth.tokens import create_access_token


def _bearer(role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token('test-user', role)}"}


@pytest.fixture
def client() -> TestClient:
    from sozo_api.server import app

    return TestClient(app)


def test_documents_generate_requires_clinician(client: TestClient):
    r = client.post(
        "/api/v1/documents/generate",
        json={"condition_slug": "migraine", "dry_run": True, "validate_only": True},
        headers=_bearer("readonly"),
    )
    assert r.status_code == 403

    r2 = client.post(
        "/api/v1/documents/generate",
        json={"condition_slug": "migraine", "dry_run": True, "validate_only": True},
        headers=_bearer("clinician"),
    )
    assert r2.status_code == 200
    payload = r2.json()
    assert "build_id" in payload
    assert payload["condition_slug"] == "migraine"
    assert isinstance(payload.get("results"), list)

