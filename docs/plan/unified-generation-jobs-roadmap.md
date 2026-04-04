# Unified generation jobs — roadmap (subagent synthesis)

This plan distills parallel codebase reviews (graph/DB, checkpointer, audit). Phases are ordered by dependency; each phase can ship as its own PR.

## Phase 0 — Correlation & observability (done / in flight)

- Treat **`thread_id` = `request_id`** as the canonical graph run id (already true).
- **Governance audit:** emit `audit_log` rows from the graph API path (not only `node_history` + JSON files). *Started:* `POST /api/graph/generate` logs `entity_type=graph_run`, `action=generation_started`, `entity_id=thread_id`.
- **State schema:** optional `output.protocol_id` on `OutputState` for future REST linkage.

## Phase 1 — Single logical “job” record

- **Applied:** `graph_runs.protocol_id` (nullable FK → `protocols.id`), Alembic `003_graph_run_protocol_id`; `GraphRunRepository` reads/writes from `output.protocol_id`; render nodes **merge** `output` so `protocol_id` survives `document_renderer` / `protocol_reporter`.
- **API:** `POST /api/graph/link-protocol` merges into checkpoint + DB; optional **`protocol_id`** on `POST /api/graph/review`; **`GET /api/graph/status/{thread_id}`** returns top-level **`protocol_id`** and **`output.protocol_id`** (DB fallback if checkpoint lacks it); **`POST /api/graph/generate`** response includes **`protocol_id`** when present in state.
- **Unify storage strategy:** SQLite (`protocols.py`) vs Postgres (`graph_runs`) split remains — linking assumes a **`protocols`** row exists in the **same** DB as `graph_runs` when the FK is enforced.

## Phase 2 — Durable checkpoints

- **Applied (dev default):** `sozo_api.graph_checkpointer.get_graph_checkpointer()` uses **`SqliteSaver`** at `outputs/langgraph_checkpoints.db` (or `SOZO_GRAPH_CHECKPOINT_SQLITE`). Set **`SOZO_GRAPH_CHECKPOINTER=memory`** for ephemeral checkpoints (tests default this in `conftest.py`).
- **Production:** prefer **Postgres** checkpoint backend + shared DB across **workers/instances** when you scale past one process.
- Align product errors: unknown thread vs **checkpoint missing after restart**.

## Phase 3 — Audit as single compliance path

- Route **all** significant actions through `audit_service.log_event` (or formally deprecate duplicate `protocols.py` audit table with a migration plan).
- Extend **`/api/audit/events` filters** with `thread_id` / `build_id` when present in `details`.
- On graph milestones (review submitted, approved, failed), emit events with **`details.thread_id`** and **`protocol_id`** when known.

## Phase 4 — Clinical UX & evaluation

- **Evidence → section** traceability in SPA; golden-set evaluation harness for generated protocols.
- **One vertical** polished end-to-end (single condition/modality) before broadening features.

## Subagent references (files)

- Graph/API: `src/sozo_api/server.py`, `src/sozo_graph/unified_graph.py`, `src/sozo_db/models/graph_run.py`, `src/sozo_db/repositories/graph_run_repo.py`
- Checkpointer: `src/sozo_api/server.py` (`_get_checkpointer`), `src/sozo_graph/unified_graph.py` (`build_unified_graph`)
- Audit: `src/sozo_api/routes/audit_service.py`, `src/sozo_api/routes/audit.py`, `src/sozo_graph/unified_graph.py` (`audit_logger_node`)

## Ownership

Engineering leads each phase; Phase 1–3 are platform prerequisites for regulated deployments. Phase 4 is product differentiation.
