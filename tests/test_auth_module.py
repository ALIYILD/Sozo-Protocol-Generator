"""Tests for the auth module: passwords, tokens, and RBAC."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from sozo_auth.config import auth_config
from sozo_auth.passwords import hash_password, validate_password_strength, verify_password
from sozo_auth.tokens import create_access_token, create_token_pair, decode_token
from sozo_auth.rbac import ROLE_PERMISSIONS, Permission, has_permission


# ── Password hashing + verification ──────────────────────────────────────


class TestPasswordHashing:
    def test_hash_and_verify_round_trip(self):
        plain = "SecureP@ssw0rd!"
        hashed = hash_password(plain)
        assert hashed != plain
        assert verify_password(plain, hashed) is True

    def test_wrong_password_fails_verification(self):
        hashed = hash_password("CorrectPassword1!")
        assert verify_password("WrongPassword1!", hashed) is False

    def test_hash_is_different_each_time(self):
        """Bcrypt uses random salts, so hashes should differ."""
        h1 = hash_password("SamePassword1!")
        h2 = hash_password("SamePassword1!")
        assert h1 != h2


# ── Password strength validation ─────────────────────────────────────────


class TestPasswordStrength:
    def test_strong_password_passes(self):
        issues = validate_password_strength("Str0ng!P@ssword")
        assert issues == []

    def test_too_short_password(self):
        issues = validate_password_strength("Sh0rt!")
        assert any("at least" in i for i in issues)

    def test_missing_uppercase(self):
        issues = validate_password_strength("no_uppercase_12345!")
        assert any("uppercase" in i for i in issues)

    def test_missing_lowercase(self):
        issues = validate_password_strength("NO_LOWERCASE_12345!")
        assert any("lowercase" in i for i in issues)

    def test_missing_digit(self):
        issues = validate_password_strength("NoDigitsHere!!!")
        assert any("digit" in i for i in issues)

    def test_missing_special_character(self):
        issues = validate_password_strength("NoSpecialChars123")
        assert any("special" in i for i in issues)

    def test_all_issues_for_weak_password(self):
        issues = validate_password_strength("abc")
        assert len(issues) >= 3  # Too short, missing uppercase, digit, special


# ── Token creation + decoding ─────────────────────────────────────────────


class TestTokenCreation:
    def test_access_token_round_trip(self):
        token = create_access_token("user123", "clinician")
        payload = decode_token(token)
        assert payload.sub == "user123"
        assert payload.role == "clinician"
        assert payload.jti is not None

    def test_token_pair_returns_both_tokens(self):
        pair = create_token_pair("user456", "admin")
        assert pair.access_token
        assert pair.refresh_token
        assert pair.token_type == "bearer"

    def test_refresh_token_has_no_role(self):
        pair = create_token_pair("user789", "reviewer")
        payload = decode_token(pair.refresh_token)
        # Refresh token defaults to readonly since no role is set
        assert payload.role == "readonly"

    def test_access_token_has_expiry(self):
        token = create_access_token("user123", "admin")
        payload = decode_token(token)
        assert payload.exp > datetime.now(timezone.utc)


# ── Expired token ────────────────────────────────────────────────────────


class TestExpiredToken:
    def test_expired_token_raises_error(self):
        """Manually create a token that expired in the past."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "user_expired",
            "role": "clinician",
            "exp": now - timedelta(hours=1),
            "iat": now - timedelta(hours=2),
            "jti": "expired-jti",
            "type": "access",
        }
        token = jwt.encode(payload, auth_config.secret_key, algorithm=auth_config.algorithm)
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_token(token)


# ── RBAC: role permissions ────────────────────────────────────────────────


class TestRBAC:
    def test_admin_has_all_permissions(self):
        admin_perms = ROLE_PERMISSIONS["admin"]
        for perm in Permission:
            assert perm in admin_perms, f"Admin missing permission: {perm.value}"

    def test_readonly_has_only_view_protocols(self):
        readonly_perms = ROLE_PERMISSIONS["readonly"]
        assert readonly_perms == {Permission.VIEW_PROTOCOLS}

    def test_clinician_can_create_protocols(self):
        assert has_permission("clinician", Permission.CREATE_PROTOCOLS) is True

    def test_clinician_cannot_manage_users(self):
        assert has_permission("clinician", Permission.MANAGE_USERS) is False

    def test_reviewer_can_approve_protocols(self):
        assert has_permission("reviewer", Permission.APPROVE_PROTOCOLS) is True

    def test_operator_can_manage_system(self):
        assert has_permission("operator", Permission.MANAGE_SYSTEM) is True

    def test_operator_cannot_create_protocols(self):
        assert has_permission("operator", Permission.CREATE_PROTOCOLS) is False

    def test_unknown_role_has_no_permissions(self):
        assert has_permission("nonexistent_role", Permission.VIEW_PROTOCOLS) is False


# ── has_permission function ──────────────────────────────────────────────


class TestHasPermission:
    def test_returns_bool(self):
        result = has_permission("admin", Permission.VIEW_PROTOCOLS)
        assert isinstance(result, bool)
        assert result is True

    def test_all_roles_have_view_protocols(self):
        for role in ("admin", "clinician", "reviewer", "operator", "readonly"):
            assert has_permission(role, Permission.VIEW_PROTOCOLS) is True
