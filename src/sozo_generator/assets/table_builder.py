"""Structured CanonicalTable builders for the SOZO long-document pipeline.

Each method on TableBuilder constructs a fully-populated CanonicalTable from
a ConditionSchema (or a fragment of one). All fields fall back to "N/A" or
"—" when the underlying condition data is absent or None.
"""
from __future__ import annotations

from typing import Optional

from sozo_generator.schemas.canonical import CanonicalTable
from sozo_generator.schemas.condition import ConditionSchema


def _v(value, fallback: str = "N/A") -> str:
    """Return str(value) if value is truthy, else fallback."""
    if value is None:
        return fallback
    s = str(value).strip()
    return s if s else fallback


def _join(items, sep: str = ", ", fallback: str = "N/A") -> str:
    """Join a list of items into a string, returning fallback if empty."""
    if not items:
        return fallback
    parts = [str(i).strip() for i in items if str(i).strip()]
    return sep.join(parts) if parts else fallback


# Evidence level → short display label
_EVIDENCE_LABELS = {
    "highest": "Highest",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
    "very_low": "Very Low",
    "missing": "—",
}


def _ev_label(level) -> str:
    if level is None:
        return "—"
    val = level.value if hasattr(level, "value") else str(level)
    return _EVIDENCE_LABELS.get(val.lower(), _v(val))


# Evidence level → numeric score used for sorting / encoding
_EVIDENCE_SCORES = {
    "very_low": 1,
    "low": 2,
    "medium": 3,
    "high": 4,
    "highest": 5,
    "missing": 0,
}


def _ev_score(level) -> int:
    if level is None:
        return 0
    val = level.value if hasattr(level, "value") else str(level)
    return _EVIDENCE_SCORES.get(val.lower(), 0)


class TableBuilder:
    """Builds structured CanonicalTable objects from condition/protocol data."""

    # ------------------------------------------------------------------
    # Protocol parameters
    # ------------------------------------------------------------------

    def build_protocol_parameters_table(
        self,
        condition: ConditionSchema,
        modality: Optional[str] = None,
    ) -> CanonicalTable:
        """Build a protocol parameters table.

        Columns: Protocol | Modality | Target | Frequency | Intensity | Sessions | Evidence Level
        Rows: one per condition.protocols entry (filtered by modality when given).
        """
        headers = [
            "Protocol",
            "Modality",
            "Target",
            "Frequency",
            "Intensity",
            "Sessions",
            "Evidence Level",
        ]
        rows: list[list[str]] = []

        for proto in condition.protocols:
            mod_val = (
                proto.modality.value
                if hasattr(proto.modality, "value")
                else str(proto.modality)
            )
            if modality and mod_val.lower() != modality.lower():
                continue

            params = proto.parameters or {}
            frequency = _v(
                params.get("frequency") or params.get("freq"), fallback="N/A"
            )
            intensity = _v(
                params.get("intensity")
                or params.get("current")
                or params.get("amplitude"),
                fallback="N/A",
            )
            sessions = _v(proto.session_count, fallback="N/A")

            rows.append(
                [
                    _v(proto.label),
                    mod_val.upper(),
                    _v(proto.target_region),
                    frequency,
                    intensity,
                    sessions,
                    _ev_label(proto.evidence_level),
                ]
            )

        if not rows:
            rows = [["—"] * len(headers)]

        return CanonicalTable(
            title=f"Protocol Parameters — {condition.display_name}",
            headers=headers,
            rows=rows,
            footer=(
                f"All protocols are off-label unless stated otherwise. "
                f"N={len(rows)} protocols shown."
            ),
        )

    # ------------------------------------------------------------------
    # Assessment tools
    # ------------------------------------------------------------------

    def build_assessment_tools_table(
        self,
        condition: ConditionSchema,
    ) -> CanonicalTable:
        """Build an assessment tools table.

        Columns: Scale | Abbreviation | Domains | Timing | Evidence Level
        """
        headers = ["Scale", "Abbreviation", "Domains", "Timing", "Evidence Level"]
        rows: list[list[str]] = []

        for tool in condition.assessment_tools:
            pmid = _v(tool.evidence_pmid, fallback=None)
            ev_label = f"PMID {pmid}" if pmid else "—"
            rows.append(
                [
                    _v(tool.name),
                    _v(tool.abbreviation),
                    _join(tool.domains),
                    _v(tool.timing),
                    ev_label,
                ]
            )

        if not rows:
            rows = [["—"] * len(headers)]

        return CanonicalTable(
            title=f"Assessment Tools — {condition.display_name}",
            headers=headers,
            rows=rows,
        )

    # ------------------------------------------------------------------
    # Contraindications
    # ------------------------------------------------------------------

    def build_contraindications_table(
        self,
        condition: ConditionSchema,
    ) -> CanonicalTable:
        """Build a contraindications/safety notes table.

        Columns: Category | Severity | Contraindication/Note
        Sources: condition.safety_notes + condition.contraindications (plain strings).
        """
        headers = ["Category", "Severity", "Contraindication / Note"]
        rows: list[list[str]] = []

        for note in condition.safety_notes:
            rows.append(
                [
                    _v(note.category).replace("_", " ").title(),
                    _v(note.severity).title(),
                    _v(note.description),
                ]
            )

        for ci in condition.contraindications:
            rows.append(["Contraindication", "Absolute", _v(ci)])

        if not rows:
            rows = [["—"] * len(headers)]

        return CanonicalTable(
            title=f"Contraindications & Safety Notes — {condition.display_name}",
            headers=headers,
            rows=rows,
            footer=(
                "Always conduct a full safety screen prior to treatment. "
                "Consult referring clinician for absolute contraindications."
            ),
        )

    # ------------------------------------------------------------------
    # Stimulation targets
    # ------------------------------------------------------------------

    def build_stimulation_targets_table(
        self,
        condition: ConditionSchema,
    ) -> CanonicalTable:
        """Build a stimulation targets table.

        Columns: Modality | Target Region | Laterality | EEG Positions | Evidence Level | Off-Label
        """
        headers = [
            "Modality",
            "Target Region",
            "Laterality",
            "EEG Positions",
            "Evidence Level",
            "Off-Label",
        ]
        rows: list[list[str]] = []

        for target in condition.stimulation_targets:
            mod_val = (
                target.modality.value
                if hasattr(target.modality, "value")
                else str(target.modality)
            )
            eeg_positions = _join(target.eeg_canonical or [], fallback="N/A")
            off_label = "Yes" if target.off_label else "No"

            rows.append(
                [
                    mod_val.upper(),
                    _v(target.target_region),
                    _v(target.laterality).title(),
                    eeg_positions,
                    _ev_label(target.evidence_level),
                    off_label,
                ]
            )

        if not rows:
            rows = [["—"] * len(headers)]

        return CanonicalTable(
            title=f"Stimulation Targets — {condition.display_name}",
            headers=headers,
            rows=rows,
        )

    # ------------------------------------------------------------------
    # Phenotypes
    # ------------------------------------------------------------------

    def build_phenotype_table(
        self,
        condition: ConditionSchema,
    ) -> CanonicalTable:
        """Build a phenotype summary table.

        Columns: Phenotype | Key Features | Primary Networks | Preferred Modalities
        """
        headers = ["Phenotype", "Key Features", "Primary Networks", "Preferred Modalities"]
        rows: list[list[str]] = []

        for ph in condition.phenotypes:
            net_labels = []
            for n in ph.primary_networks:
                net_labels.append(n.value.upper() if hasattr(n, "value") else str(n).upper())

            mod_labels = []
            for m in ph.preferred_modalities:
                mod_labels.append(m.value.upper() if hasattr(m, "value") else str(m).upper())

            rows.append(
                [
                    _v(ph.label),
                    _join(ph.key_features, sep="; "),
                    _join(net_labels),
                    _join(mod_labels),
                ]
            )

        if not rows:
            rows = [["—"] * len(headers)]

        return CanonicalTable(
            title=f"Clinical Phenotypes — {condition.display_name}",
            headers=headers,
            rows=rows,
        )

    # ------------------------------------------------------------------
    # Network profiles
    # ------------------------------------------------------------------

    def build_network_profiles_table(
        self,
        condition: ConditionSchema,
    ) -> CanonicalTable:
        """Build a network profiles table.

        Columns: Network | Dysfunction | Severity | Clinical Relevance
        """
        headers = ["Network", "Dysfunction", "Severity", "Clinical Relevance"]
        rows: list[list[str]] = []

        for profile in condition.network_profiles:
            net_val = (
                profile.network.value.upper()
                if hasattr(profile.network, "value")
                else str(profile.network).upper()
            )
            dys_val = (
                profile.dysfunction.value
                if hasattr(profile.dysfunction, "value")
                else str(profile.dysfunction)
            )
            rows.append(
                [
                    net_val,
                    dys_val.title(),
                    _v(profile.severity).title(),
                    _v(profile.relevance),
                ]
            )

        if not rows:
            rows = [["—"] * len(headers)]

        return CanonicalTable(
            title=f"Network Profiles (FNON) — {condition.display_name}",
            headers=headers,
            rows=rows,
        )

    # ------------------------------------------------------------------
    # Evidence summary
    # ------------------------------------------------------------------

    def build_evidence_summary_table(
        self,
        condition: ConditionSchema,
    ) -> CanonicalTable:
        """Build a modality-level evidence summary table.

        Columns: Modality | Evidence Level | Key Findings | Paper Count
        Rows grouped by modality from condition.stimulation_targets.
        """
        headers = ["Modality", "Evidence Level", "Key Findings", "Paper Count"]

        # Group by modality; keep best evidence level per modality
        modality_data: dict[str, dict] = {}
        for target in condition.stimulation_targets:
            mod_val = (
                target.modality.value
                if hasattr(target.modality, "value")
                else str(target.modality)
            )
            mod_key = mod_val.upper()
            score = _ev_score(target.evidence_level)
            if mod_key not in modality_data or score > modality_data[mod_key]["score"]:
                modality_data[mod_key] = {
                    "score": score,
                    "level": target.evidence_level,
                    "rationale": target.rationale,
                    "count": 0,
                }
            modality_data[mod_key]["count"] += 1

        rows: list[list[str]] = []
        for mod_key, data in sorted(modality_data.items(), key=lambda x: -x[1]["score"]):
            rows.append(
                [
                    mod_key,
                    _ev_label(data["level"]),
                    _v(data["rationale"])[:120],  # truncate long rationale
                    str(data["count"]),
                ]
            )

        if not rows:
            rows = [["—"] * len(headers)]

        return CanonicalTable(
            title=f"Evidence Summary by Modality — {condition.display_name}",
            headers=headers,
            rows=rows,
            footer="Evidence levels: Highest > High > Medium > Low > Very Low.",
        )

    # ------------------------------------------------------------------
    # Session schedule
    # ------------------------------------------------------------------

    def build_session_schedule_table(
        self,
        condition: ConditionSchema,
        protocol_id: Optional[str] = None,
    ) -> CanonicalTable:
        """Build a session schedule table (Baseline / Acute / Maintenance phases).

        Columns: Phase | Sessions | Frequency | Notes
        Uses protocol session_count if a matching protocol is found.
        """
        headers = ["Phase", "Sessions", "Frequency", "Notes"]

        # Try to find the referenced protocol
        proto = None
        if protocol_id:
            for p in condition.protocols:
                if p.protocol_id == protocol_id:
                    proto = p
                    break
        if proto is None and condition.protocols:
            proto = condition.protocols[0]

        session_total = (proto.session_count or 20) if proto else 20
        params = (proto.parameters or {}) if proto else {}

        # Derive phase breakdown
        baseline_sessions = 1
        acute_sessions = min(session_total, max(session_total - 2, 10))
        maintenance_sessions = max(session_total - acute_sessions - baseline_sessions, 0)

        freq_str = str(
            params.get("frequency") or params.get("freq") or "3×/week"
        )

        rows = [
            [
                "Baseline",
                str(baseline_sessions),
                "Once (initial assessment)",
                "Obtain baseline measures; consent check",
            ],
            [
                "Acute Treatment",
                str(acute_sessions),
                freq_str,
                "Active stimulation; weekly outcome tracking",
            ],
            [
                "Maintenance",
                str(maintenance_sessions) if maintenance_sessions > 0 else "PRN",
                "1–2×/month",
                "Sustain response; re-assess at 4 weeks",
            ],
            [
                "Follow-up",
                "1",
                "At 3 months",
                "Final endpoint assessment; discharge planning",
            ],
        ]

        return CanonicalTable(
            title=f"Session Schedule — {condition.display_name}",
            headers=headers,
            rows=rows,
            footer=(
                f"Based on {session_total}-session protocol. "
                "Adjust per clinical response."
            ),
        )

    # ------------------------------------------------------------------
    # Monitoring & outcomes
    # ------------------------------------------------------------------

    def build_monitoring_outcomes_table(
        self,
        condition: ConditionSchema,
    ) -> CanonicalTable:
        """Build a monitoring and outcomes table.

        Columns: Domain | Measure | Timing | Threshold (Response Criterion)
        Built from condition.assessment_tools + condition.responder_criteria.
        """
        headers = ["Domain", "Measure", "Timing", "Threshold (Response Criterion)"]
        rows: list[list[str]] = []

        # Map assessment tools to rows; pair responder criteria by index when available
        responder_crit = condition.responder_criteria or []

        for idx, tool in enumerate(condition.assessment_tools):
            criterion = responder_crit[idx] if idx < len(responder_crit) else "—"
            domain = _join(tool.domains, sep=" / ") if tool.domains else "General"
            rows.append(
                [
                    domain,
                    f"{_v(tool.name)} ({_v(tool.abbreviation)})",
                    _v(tool.timing).replace("_", " ").title(),
                    _v(criterion),
                ]
            )

        # Append remaining responder criteria not covered by assessment tools
        for criterion in responder_crit[len(condition.assessment_tools):]:
            rows.append(["—", "—", "—", _v(criterion)])

        if not rows:
            rows = [["—"] * len(headers)]

        return CanonicalTable(
            title=f"Monitoring & Outcomes — {condition.display_name}",
            headers=headers,
            rows=rows,
            footer=(
                "Responder criteria per SOZO clinical governance framework. "
                "Non-responders escalated per pathway."
            ),
        )

    # ------------------------------------------------------------------
    # Modality comparison
    # ------------------------------------------------------------------

    def build_modality_comparison_table(
        self,
        condition: ConditionSchema,
    ) -> CanonicalTable:
        """Build a modality comparison table.

        Columns: Modality | Mechanism | Target | Evidence Level | Session Count | Notes
        """
        headers = [
            "Modality",
            "Mechanism",
            "Target",
            "Evidence Level",
            "Session Count",
            "Notes",
        ]

        # Build one row per unique modality using stimulation_targets as primary source
        seen: dict[str, dict] = {}
        for target in condition.stimulation_targets:
            mod_val = (
                target.modality.value
                if hasattr(target.modality, "value")
                else str(target.modality)
            )
            mod_key = mod_val.upper()
            if mod_key not in seen:
                seen[mod_key] = {
                    "target": target.target_region,
                    "rationale": target.rationale,
                    "level": target.evidence_level,
                    "off_label": target.off_label,
                }

        # Overlay session count from protocols
        proto_sessions: dict[str, int] = {}
        for proto in condition.protocols:
            mod_val = (
                proto.modality.value
                if hasattr(proto.modality, "value")
                else str(proto.modality)
            )
            mod_key = mod_val.upper()
            if proto.session_count:
                proto_sessions[mod_key] = proto.session_count

        # Standard mechanism descriptions per modality
        _mechanisms = {
            "TDCS": "Direct current polarisation of cortical neurons",
            "TPS": "Transcranial pulse stimulation — ultrasound neuromodulation",
            "TAVNS": "Auricular vagal nerve stimulation (transcutaneous)",
            "CES": "Cranial electrotherapy stimulation (0.5–100 Hz)",
            "TMS": "Focal magnetic induction — action potential modulation",
            "NFB": "Real-time EEG biofeedback — operant conditioning",
            "ITBS": "Intermittent theta-burst stimulation (a TMS subtype)",
            "VNS": "Implantable vagal nerve stimulation",
            "MULTIMODAL": "Combined neuromodulation approach",
        }

        rows: list[list[str]] = []
        for mod_key, data in sorted(seen.items(), key=lambda x: -_ev_score(x[1]["level"])):
            mechanism = _mechanisms.get(mod_key, "Neuromodulation")
            sessions_str = str(proto_sessions[mod_key]) if mod_key in proto_sessions else "N/A"
            notes = "Off-label" if data["off_label"] else "Approved indication"
            rows.append(
                [
                    mod_key,
                    mechanism,
                    _v(data["target"]),
                    _ev_label(data["level"]),
                    sessions_str,
                    notes,
                ]
            )

        if not rows:
            rows = [["—"] * len(headers)]

        return CanonicalTable(
            title=f"Modality Comparison — {condition.display_name}",
            headers=headers,
            rows=rows,
            landscape=True,
        )

    # ------------------------------------------------------------------
    # Generic dispatch builder
    # ------------------------------------------------------------------

    def build_from_spec(self, spec: dict) -> CanonicalTable:
        """Generic builder dispatched by AssetRegistry renderer.

        spec keys:
            table_type  — one of the method names without 'build_' prefix
            condition   — ConditionSchema instance (required)
            kwargs      — extra keyword arguments forwarded to the method
        """
        condition: ConditionSchema = spec["condition"]
        table_type: str = spec.get("table_type", "")
        kwargs: dict = spec.get("kwargs", {})

        method_name = (
            table_type
            if table_type.startswith("build_")
            else f"build_{table_type}"
        )
        method = getattr(self, method_name, None)
        if method is None:
            return CanonicalTable(
                title=f"Unknown table type: {table_type}",
                headers=["Error"],
                rows=[[f"No method '{method_name}' on TableBuilder"]],
            )
        return method(condition, **kwargs)
