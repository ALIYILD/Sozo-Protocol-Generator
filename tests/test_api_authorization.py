"""Authorization rules for protected /api routes (roles + authentication)."""
from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from sozo_auth.tokens import create_access_token


def _bearer(role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token('test-user', role)}"}


@pytest.fixture
def client():
    from sozo_api.server import app

    return TestClient(app)


class TestProtocolsRouterAuth:
    def test_list_requires_authentication(self, client: TestClient):
        r = client.get("/api/protocols/")
        assert r.status_code == 403

    def test_list_allows_readonly(self, client: TestClient):
        r = client.get("/api/protocols/", headers=_bearer("readonly"))
        assert r.status_code == 200

    def test_create_requires_clinician(self, client: TestClient):
        body = {
            "condition_slug": "depression",
            "modality": "tdcs",
            "tier": "fellow",
            "doc_type": "evidence_based_protocol",
        }
        r = client.post("/api/protocols/", json=body, headers=_bearer("readonly"))
        assert r.status_code == 403

        r2 = client.post("/api/protocols/", json=body, headers=_bearer("clinician"))
        assert r2.status_code != 403

    def test_status_transition_requires_reviewer(self, client: TestClient):
        import uuid

        pid = str(uuid.uuid4())
        r = client.post(
            f"/api/protocols/{pid}/transition",
            json={"target_status": "approved", "notes": "sign-off"},
            headers=_bearer("clinician"),
        )
        assert r.status_code == 403


class TestPatientsRouterAuth:
    def test_requires_clinician_not_readonly(self, client: TestClient):
        r = client.get("/api/patients/", headers=_bearer("readonly"))
        assert r.status_code == 403

        r2 = client.get("/api/patients/", headers=_bearer("clinician"))
        assert r2.status_code != 403


class TestReviewsRouterAuth:
    def test_queue_requires_reviewer(self, client: TestClient):
        r = client.get("/api/reviews/queue", headers=_bearer("clinician"))
        assert r.status_code == 403

        r2 = client.get("/api/reviews/queue", headers=_bearer("reviewer"))
        assert r2.status_code == 200


class TestAuditRouterAuth:
    def test_events_requires_view_audit_permission(self, client: TestClient):
        r = client.get("/api/audit/events", headers=_bearer("clinician"))
        assert r.status_code == 403

        r2 = client.get("/api/audit/events", headers=_bearer("admin"))
        assert r2.status_code == 200

        r3 = client.get("/api/audit/events", headers=_bearer("operator"))
        assert r3.status_code == 200


class TestInlineRoutesRoles:
    def test_cockpit_requires_operator_or_admin(self, client: TestClient):
        r = client.get("/api/cockpit/overview", headers=_bearer("clinician"))
        assert r.status_code == 403
        r2 = client.get("/api/cockpit/overview", headers=_bearer("operator"))
        assert r2.status_code == 200

    def test_evidence_staleness_requires_operator_or_admin(self, client: TestClient):
        r = client.get("/api/evidence/staleness", headers=_bearer("clinician"))
        assert r.status_code == 403
        r2 = client.get("/api/evidence/staleness", headers=_bearer("admin"))
        assert r2.status_code == 200

    def test_visuals_render_requires_clinician(self, client: TestClient):
        r = client.post("/api/visuals/render", json={}, headers=_bearer("readonly"))
        assert r.status_code == 403

    def test_graph_generate_requires_clinician(self, client: TestClient):
        r = client.post(
            "/api/graph/generate",
            json={"doc_type": "evidence_based_protocol", "tier": "fellow"},
            headers=_bearer("readonly"),
        )
        assert r.status_code == 403

    def test_graph_review_requires_reviewer(self, client: TestClient):
        r = client.post(
            "/api/graph/review",
            json={
                "thread_id": "00000000-0000-0000-0000-000000000000",
                "decision": "approve",
                "reviewer_id": "r1",
            },
            headers=_bearer("clinician"),
        )
        assert r.status_code == 403


class TestPublicReferenceRoutes:
    def test_health_and_knowledge_unauthenticated(self, client: TestClient):
        assert client.get("/api/health").status_code == 200
        assert client.get("/api/knowledge/conditions").status_code == 200
        assert client.get("/api/visuals/types").status_code == 200
