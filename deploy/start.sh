#!/usr/bin/env bash
# SOZO unified container entrypoint.
# - Ensures OPS_PASSWORD_HASH is present (Caddy basic_auth for /ops)
# - Falls back to a random hash if not provided so the container still boots
#   (ops area will be inaccessible until the secret is set + machine restarted)
# - Hands off to supervisord which runs FastAPI + Streamlit + Caddy.

set -euo pipefail

if [[ -z "${OPS_PASSWORD_HASH:-}" ]]; then
  echo "[sozo-start] WARNING: OPS_PASSWORD_HASH not set."
  echo "[sozo-start]   Set it with:  flyctl secrets set OPS_PASSWORD_HASH='<bcrypt-hash>'"
  echo "[sozo-start]   Generate with: caddy hash-password --plaintext '<your-password>'"
  # Random unusable hash so Caddy config still parses
  export OPS_PASSWORD_HASH='$2a$14$unreachableplaceholderhashaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
fi

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/sozo.conf
