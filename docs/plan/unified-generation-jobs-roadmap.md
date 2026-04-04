# Unified generation jobs — roadmap (subagent synthesis)

This plan distills parallel codebase reviews (graph/DB, checkpointer, audit). Phases are ordered by dependency; each phase can ship as its own PR.

## Phase 0 — Correlation & observability (done / in flight)

- Treat **`thread_id` = `request_id`** as the canonical graph run id (already true).
- **Governance audit:** emit `audit_log` rows from the graph API path (not only `node_history` + JSON files). *Started:* `POST /api/graph/generate` logs `entity_type=graph_run`, `action=generation_started`, `entity_id=thread_id`.
- **State schema:** optional `output.protocol_id` on `OutputState` for future REST linkage.

## Phase 1 — Single logical “job” record

- Add **`protocol_id` + `thread_id` FK-style columns** on `GraphRun` (or a new `generation_jobs` table) once protocol rows exist for graph runs.
- When creating or attaching a REST protocol from a run, **write `protocol_id` into graph state `output`** and return it from `GET /api/graph/status`.
- **Unify storage strategy:** resolve SQLite (protocol routes) vs Postgres (`graph_runs`) split (migrate one direction or document a sync boundary).

## Phase 2 — Durable checkpoints

- Replace **`MemorySaver`** in `server._get_checkpointer()` with **DB-backed saver** (`PostgresSaver` / `SqliteSaver` per LangGraph version), shared across workers.
- Run LangGraph checkpoint **schema migrations** in deploy docs/CI.
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
