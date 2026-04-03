#!/usr/bin/env bash
# Docker full-stack smoke test for Sozo
# Usage: ./scripts/docker-smoke-test.sh
#
# Prerequisites: docker compose up -d (db, redis, api, migrate at minimum)

set -euo pipefail

API_BASE="${API_BASE:-http://localhost:8000}"
TIMEOUT=5
OK=0
FAIL=0

check() {
    local name="$1"
    local cmd="$2"
    local expected="$3"

    printf "  %-40s " "$name"
    result=$(eval "$cmd" 2>/dev/null || echo "CURL_FAILED")

    if echo "$result" | grep -q "$expected"; then
        echo "OK"
        OK=$((OK + 1))
    else
        echo "FAIL"
        echo "    Expected: $expected"
        echo "    Got:      $(echo "$result" | head -1 | cut -c1-120)"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== Sozo Docker Smoke Test ==="
echo "API: $API_BASE"
echo ""

# ── Health ──────────────────────────────────────────────
echo "1. Health checks"
check "API health" \
    "curl -sf --max-time $TIMEOUT $API_BASE/api/health" \
    '"status":"ok"'

# ── Knowledge ──────────────────────────────────────────
echo ""
echo "2. Knowledge endpoints"
check "List conditions" \
    "curl -sf --max-time $TIMEOUT $API_BASE/api/knowledge/conditions" \
    '"conditions"'

check "Get condition (parkinsons)" \
    "curl -sf --max-time $TIMEOUT $API_BASE/api/knowledge/conditions/parkinsons" \
    '"condition"'

# ── Evidence ───────────────────────────────────────────
echo ""
echo "3. Evidence endpoints"
check "Evidence staleness" \
    "curl -sf --max-time $TIMEOUT $API_BASE/api/evidence/staleness" \
    '"overall_health"'

# ── Safety ─────────────────────────────────────────────
echo ""
echo "4. Safety endpoints"
check "Safety check" \
    "curl -sf --max-time 10 -X POST $API_BASE/api/safety/check -H 'Content-Type: application/json' -d '{\"demographics\":{\"age\":55,\"sex\":\"male\"},\"medications\":[],\"medical_history\":[],\"modalities\":[\"tdcs\"]}'" \
    '"safety_cleared"'

# ── Graph pipeline ─────────────────────────────────────
echo ""
echo "5. Graph pipeline endpoints"
check "Graph generate (depression)" \
    "curl -sf --max-time 120 -X POST $API_BASE/api/graph/generate -H 'Content-Type: application/json' -d '{\"condition_slug\":\"depression\",\"prompt\":\"Generate tDCS protocol for depression\"}'" \
    '"thread_id"'

# ── Cockpit ────────────────────────────────────────────
echo ""
echo "6. Cockpit endpoints"
check "Cockpit overview" \
    "curl -sf --max-time $TIMEOUT $API_BASE/api/cockpit/overview" \
    '"overview"'

# ── OpenAPI ────────────────────────────────────────────
echo ""
echo "7. Documentation"
check "OpenAPI schema" \
    "curl -sf --max-time $TIMEOUT $API_BASE/openapi.json" \
    '"paths"'

# ── Summary ────────────────────────────────────────────
echo ""
echo "================================="
echo "Results: $OK passed, $FAIL failed"
echo "================================="

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
