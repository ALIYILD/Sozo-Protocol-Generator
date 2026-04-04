# Agent roster (subagents) — Sozo Protocol Generator

This repo uses **specialized context** via `.cursor/rules/*.mdc` (file-scoped) plus this map. Open or edit files under a domain to pull in the matching rule automatically.

| Subagent (domain) | Primary paths | Focus |
|-------------------|---------------|--------|
| **autoagent** | `src/autoagent_clinical/`, `tests/test_autoagent*.py`, `scripts/autoagent_metrics_summary.py` | Benchmark YAML, validators/evaluators, harnesses, CI gates, reports |
| **generator** | `src/sozo_generator/` | `GenerationService`, canonical assembly, DOCX, CLI, condition generators |
| **api-auth** | `src/sozo_api/`, `src/sozo_auth/` | FastAPI routes, CORS, JWT/RBAC, security tests |
| **graph** | `src/sozo_graph/` | LangGraph nodes, state, intake contracts, condition resolution |
| **frontend** | `frontend/src/` | Vite/React, API client, auth guards, protocol/evidence UI |

**Always-on:** `.cursor/rules/sozo-core.mdc`, `sozo-review-crosscutting.mdc`

## Coordination

- **Lab vs prod:** AutoAgent is an internal benchmark lab, not a clinical gate alone. Changes to `GenerationService` or document schemas should consider **`src/autoagent_clinical/`** impact and **`CONTRIBUTING.md`** CI expectations.
- **Contracts:** Graph outputs and API payloads favor explicit tests (`tests/test_graph_intake_contract.py`, `tests/test_api_*.py`).
- **Live generation:** Pytest marker `live_generation` + env `SOZO_AUTOAGENT_LIVE=1`; default CI stays mock-first.

## Full-codebase review snapshot (subagents)

_Last synthesized pass: structural / security posture — re-run mental checklist on any major PR._

### API & auth (`sozo_api`, `sozo_auth`)

- **IDOR risk:** Many routes enforce JWT + role but not **resource ownership** (protocols, patients, graph `thread_id`, generation `task_id`). Harden with tenant/user binding on read/write.
- **JWT model:** Identity from claims only; no server-side session/invalidation until expiry (logout/blacklist gap). Refresh route should validate token **`type`** and rotation policy.
- **Defaults:** Weak `SOZO_AUTH_SECRET_KEY` when env is not production-like — must be set in real deploys.
- **Leaks:** `/api/health` and several `HTTPException(detail=str(e))` paths may expose internal errors — prefer generic client messages.
- **Reviews:** Body-supplied `reviewer_id` vs authenticated principal can disagree — bind audit identity to `current_user`.
- **SQL:** Parameterized queries / allowlisted `ORDER BY` observed — keep that pattern for new code.

### Generator & graph (`sozo_generator`, `sozo_graph`)

- **Errors:** Broad `except Exception` and string `error` fields — consider typed errors for API surfaces.
- **Coupling:** `sozo_graph/integration.py` fans into generator, private pipeline APIs, and `GenerationService` — high change risk.
- **Sync I/O:** Graph and generation paths are **synchronous** (LLM, evidence, FS) — watch API timeouts and worker offload.
- **Duplication:** `protocol_composer` node vs `integration._llm_compose` — two parallel composition paths to keep aligned.
- **Semantics:** Stubs/docs mismatches (e.g. resolver doc vs behavior); clinician_review “edited” path may not apply overrides — verify product intent.

### Frontend (`frontend/src`)

- **Tokens in `localStorage`:** XSS yields bearer + refresh — mitigate with CSP, short access TTL, **httpOnly** refresh (requires BFF/cookie pattern) if threat model requires it. **Refresh** helper exists but **401 path** may not attempt silent refresh before logout.
- **No global ErrorBoundary** — add for production resilience.
- **CI:** `.github/workflows/frontend-ci.yml` runs `npm ci`, `npm run build`, `npm test`.

### AutoAgent-Clinical

- Validators vs evaluators are **paired by design** (not accidental duplication).
- Workflow path filters: changes **only** outside `autoagent_clinical`/listed paths **do not** trigger AutoAgent CI — intentional for speed; run manually or broaden filters if needed.

## Applying “all” specialists

All rule files are active when their **globs** match opened/attached files. For a cross-cutting task, attach files from each area or temporarily open a file per domain so every relevant rule loads.
