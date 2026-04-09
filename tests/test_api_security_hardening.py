"""Production-oriented API security checks: auth, JWT config, CORS."""
from __future__ import annotations

import os

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from pydantic import ValidationError


class TestGraphGenerateRequiresAuth:
    def test_unauthenticated_post_rejected(self):
        from sozo_api.server import app

        client = TestClient(app)
        response = client.post(
            "/api/graph/generate",
            json={"doc_type": "evidence_based_protocol", "tier": "fellow"},
        )
        assert response.status_code in (401, 403)

    def test_legacy_path_requires_auth(self):
        from sozo_api.server import app

        client = TestClient(app)
        response = client.post(
            "/api/generate/graph",
            json={"doc_type": "evidence_based_protocol", "tier": "fellow"},
        )
        assert response.status_code in (401, 403)


class TestAuthConfigProductionSecret:
    def test_fails_when_production_and_secret_placeholder(self, monkeypatch):
        monkeypatch.setenv("SOZO_ENV", "production")
        monkeypatch.setenv("SOZO_AUTH_SECRET_KEY", "CHANGE-ME-IN-PRODUCTION")

        from sozo_auth.config import AuthConfig

        with pytest.raises(ValidationError):
            AuthConfig()

    def test_fails_when_production_and_secret_unset(self, monkeypatch):
        monkeypatch.setenv("SOZO_ENV", "production")
        monkeypatch.delenv("SOZO_AUTH_SECRET_KEY", raising=False)

        from sozo_auth.config import AuthConfig

        with pytest.raises(ValidationError):
            AuthConfig()

    def test_succeeds_when_production_with_custom_secret(self, monkeypatch):
        monkeypatch.setenv("SOZO_ENV", "production")
        monkeypatch.setenv("SOZO_AUTH_SECRET_KEY", "x" * 48)

        from sozo_auth.config import AuthConfig

        cfg = AuthConfig()
        assert len(cfg.secret_key) >= 32


class TestCorsConfiguration:
    def test_production_requires_explicit_origins(self, monkeypatch):
        monkeypatch.setenv("SOZO_ENV", "production")
        monkeypatch.setenv("SOZO_AUTH_SECRET_KEY", "y" * 48)
        monkeypatch.delenv("SOZO_CORS_ORIGINS", raising=False)

        from sozo_api.cors_config import resolve_cors_allow_origins_and_credentials

        with pytest.raises(RuntimeError, match="SOZO_CORS_ORIGINS"):
            resolve_cors_allow_origins_and_credentials()

    def test_production_explicit_origins_enable_credentials(self, monkeypatch):
        monkeypatch.setenv("SOZO_ENV", "production")
        monkeypatch.setenv("SOZO_AUTH_SECRET_KEY", "z" * 48)
        monkeypatch.setenv(
            "SOZO_CORS_ORIGINS",
            "https://app.example.com,https://admin.example.com",
        )

        from sozo_api.cors_config import resolve_cors_allow_origins_and_credentials

        origins, creds = resolve_cors_allow_origins_and_credentials()
        assert origins == [
            "https://app.example.com",
            "https://admin.example.com",
        ]
        assert creds is True

    def test_wildcard_origin_disables_credentials(self, monkeypatch):
        monkeypatch.setenv("SOZO_CORS_ORIGINS", "*")

        from sozo_api.cors_config import resolve_cors_allow_origins_and_credentials

        origins, creds = resolve_cors_allow_origins_and_credentials()
        assert origins == ["*"]
        assert creds is False

    def test_create_app_fails_in_production_without_cors_origins(self, monkeypatch):
        monkeypatch.setenv("SOZO_ENV", "production")
        monkeypatch.setenv("SOZO_AUTH_SECRET_KEY", "b" * 48)
        monkeypatch.delenv("SOZO_CORS_ORIGINS", raising=False)

        from sozo_api.server import create_app

        with pytest.raises(RuntimeError, match="SOZO_CORS_ORIGINS"):
            create_app()

    def test_create_app_fails_in_production_without_jwt_secret(self, monkeypatch):
        monkeypatch.setenv("SOZO_ENV", "production")
        monkeypatch.delenv("SOZO_AUTH_SECRET_KEY", raising=False)

        from sozo_api.server import create_app

        with pytest.raises(ValidationError):
            create_app()


class TestJwtErrorDetailsAreStable:
    def test_invalid_bearer_token_detail_does_not_leak(self):
        from sozo_api.server import app

        client = TestClient(app)
        r = client.get(
            "/api/protocols/",
            headers={"Authorization": "Bearer not-a-jwt"},
        )
        assert r.status_code == 401
        assert r.json().get("detail") == "Invalid token"

    def test_invalid_refresh_token_detail_does_not_leak(self):
        from sozo_api.server import app

        client = TestClient(app)
        r = client.post("/api/auth/refresh", json={"refresh_token": "not-a-jwt"})
        assert r.status_code == 401
        assert r.json().get("detail") == "Invalid refresh token"


class TestRefreshTokenTypeStrictness:
    def test_refresh_rejects_token_without_type_claim(self):
        from datetime import datetime, timedelta, timezone
        import jwt

        from sozo_api.server import app
        from sozo_auth.config import auth_config

        client = TestClient(app)

        now = datetime.now(timezone.utc)
        payload = {
            "sub": "11111111-1111-1111-1111-111111111111",
            "role": "readonly",
            "exp": now + timedelta(days=1),
            "iat": now,
            "jti": "legacy-refresh-no-type",
            # Intentionally omit "type"
        }
        legacy = jwt.encode(payload, auth_config.secret_key, algorithm=auth_config.algorithm)

        r = client.post("/api/auth/refresh", json={"refresh_token": legacy})
        assert r.status_code == 401
        assert r.json().get("detail") == "Refresh token required"
