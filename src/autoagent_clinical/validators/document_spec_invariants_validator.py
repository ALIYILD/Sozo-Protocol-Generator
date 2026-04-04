"""
Structure-native checks on DocumentSpec (blueprint alignment, identity, tree shape).

Findings use taxonomy codes distinct from markdown-oriented validators so reports
can separate ``document_spec_invariants`` from prose/markdown issues.

* ``document_invariant_mode`` — ``relaxed`` (default, aligns with canonical assembly
  slugs) or ``strict`` (full :class:`DocumentDefinition` with alias resolution).
"""
from __future__ import annotations

import re
from typing import Any

from ..schemas import FailureTaxonomy, Severity, ValidationFinding, ValidatorReport

# Top-level section_ids commonly emitted for evidence_based_protocol (fellow) today.
_RELAXED_REQUIRED_EBP: tuple[str, ...] = (
    "document_control",
    "inclusion_exclusion",
    "clinical_overview",
    "pathophysiology",
    "brain_anatomy",
    "phenotypes",
    "safety",
    "assessments",
    "responder_criteria",
    "evidence_summary",
    "references",
)

# Map DocumentDefinition section_id -> acceptable emitted section_ids (strict mode).
_STRICT_SECTION_ALIASES: dict[tuple[str, str], tuple[str, ...]] = {
    ("evidence_based_protocol", "overview"): ("clinical_overview", "overview"),
    ("evidence_based_protocol", "anatomy"): ("brain_anatomy", "anatomy"),
    ("evidence_based_protocol", "responder"): ("responder_criteria", "responder"),
    ("evidence_based_protocol", "inclusion_exclusion"): ("inclusion_exclusion",),
    ("evidence_based_protocol", "evidence_summary"): ("evidence_summary",),
    ("evidence_based_protocol", "references"): ("references",),
    ("evidence_based_protocol", "pathophysiology"): ("pathophysiology",),
    ("evidence_based_protocol", "phenotypes"): ("phenotypes",),
    ("evidence_based_protocol", "assessments"): ("assessments",),
    ("evidence_based_protocol", "safety"): ("safety",),
}


def _walk_spec_sections(
    sections: list[Any],
    depth: int = 0,
) -> list[tuple[int, Any]]:
    rows: list[tuple[int, Any]] = []
    for sec in sections:
        rows.append((depth, sec))
        rows.extend(_walk_spec_sections(sec.subsections, depth + 1))
    return rows


def _section_index_by_id(sections_tree: list[Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for _, sec in _walk_spec_sections(sections_tree):
        sid = (sec.section_id or "").strip()
        if sid and sid not in out:
            out[sid] = sec
    return out


def _flatten_definition_sections(specs: list[Any], tier: Any) -> list[Any]:
    out: list[Any] = []
    for sp in specs:
        if sp.tier is not None and sp.tier != tier:
            continue
        out.append(sp)
        out.extend(_flatten_definition_sections(sp.subsections, tier))
    return out


def _top_level_def_ids_for_order(defn: Any, tier: Any) -> list[str]:
    return [
        s.section_id
        for s in defn.sections
        if s.required
        and (s.tier is None or s.tier == tier)
    ]


def _section_non_empty(sec: Any) -> bool:
    if (sec.content or "").strip():
        return True
    if sec.tables:
        return True
    if sec.subsections:
        return any(_section_non_empty(s) for s in sec.subsections)
    return False


def _protocols_branch_present(by_id: dict[str, Any]) -> bool:
    if "protocols" in by_id:
        return True
    return any(k.startswith("protocols_") for k in by_id)


def _networks_evidence_in_spec(spec: Any) -> bool:
    blob = " ".join(
        ((sec.title or "") + " " + (sec.content or "")).lower()
        for _, sec in _walk_spec_sections(spec.sections)
    )
    return "fnon" in blob or "network profile" in blob or "six-network" in blob


def _resolve_required_node(
    doc_type_value: str,
    rid: str,
    by_id: dict[str, Any],
    spec: Any,
) -> Any | None:
    if rid in by_id:
        return by_id[rid]
    for alt in _STRICT_SECTION_ALIASES.get((doc_type_value, rid), ()):
        if alt in by_id:
            return by_id[alt]
    if rid == "protocols" and _protocols_branch_present(by_id):
        # Return first protocols_* for emptiness/placeholder checks
        for key in sorted(by_id):
            if key.startswith("protocols_"):
                return by_id[key]
    if rid == "networks" and _networks_evidence_in_spec(spec):
        return by_id.get("networks") or by_id.get("clinical_overview")
    return None


def _title_matches_condition(spec: Any) -> bool:
    title_l = (spec.title or "").lower()
    slug_bits = re.findall(r"[a-z]{4,}", (spec.condition_slug or "").replace("_", " "))
    name_bits = re.findall(
        r"[a-z]{4,}",
        (spec.condition_name or "").lower().replace("'", ""),
    )
    title_bits = set(re.findall(r"[a-z]{4,}", title_l.replace("'", "")))
    if any(b in title_bits for b in slug_bits):
        return True
    if any(b in title_bits for b in name_bits):
        return True
    return False


def run_document_spec_invariants_validation(
    document_spec: dict[str, Any] | None,
    *,
    case_inputs: dict[str, Any],
) -> ValidatorReport:
    findings: list[ValidationFinding] = []

    if document_spec is None:
        return ValidatorReport(
            validator_id="document_spec_invariants",
            findings=[],
        )

    if case_inputs.get("skip_document_spec_invariants"):
        return ValidatorReport(
            validator_id="document_spec_invariants",
            findings=[],
        )

    try:
        from sozo_generator.schemas.definitions import get_document_definition
        from sozo_generator.schemas.documents import DocumentSpec

        spec = DocumentSpec.model_validate(document_spec)
    except Exception:  # noqa: BLE001
        return ValidatorReport(
            validator_id="document_spec_invariants",
            findings=[],
        )

    mode = str(case_inputs.get("document_invariant_mode", "relaxed")).lower()
    if mode not in ("relaxed", "strict"):
        mode = "relaxed"

    try:
        defn = get_document_definition(spec.document_type)
    except ValueError:
        findings.append(
            ValidationFinding(
                code=FailureTaxonomy.SECTION_ORDER_OR_DEPTH_ANOMALY.value,
                severity=Severity.LOW,
                message=f"No document definition for doc_type={spec.document_type!r}.",
                reasons=["Skipping blueprint section-requirement checks."],
            )
        )
        return ValidatorReport(
            validator_id="document_spec_invariants",
            findings=findings,
        )

    if spec.tier not in defn.applicable_tiers:
        findings.append(
            ValidationFinding(
                code=FailureTaxonomy.SPEC_IDENTITY_MISMATCH.value,
                severity=Severity.MEDIUM,
                message=(
                    f"DocumentSpec tier {spec.tier!r} is not in applicable_tiers "
                    f"{[t.value for t in defn.applicable_tiers]} for {spec.document_type.value}."
                ),
                reasons=[],
            )
        )

    tier = spec.tier
    by_id = _section_index_by_id(spec.sections)
    dt_val = spec.document_type.value
    required_check_ids: list[str] = []

    # ── Required sections (relaxed vs strict) ───────────────────────────
    if mode == "relaxed" and dt_val == "evidence_based_protocol":
        required_check_ids = list(
            case_inputs.get("relaxed_required_section_ids") or _RELAXED_REQUIRED_EBP
        )
        if not _protocols_branch_present(by_id):
            findings.append(
                ValidationFinding(
                    code=FailureTaxonomy.MISSING_REQUIRED_SECTION.value,
                    severity=Severity.HIGH,
                    message="Missing stimulation protocol branch (no `protocols` or `protocols_*` section).",
                    reasons=["Canonical EBP must include at least one protocols_* block."],
                    locator="protocols_*",
                )
            )
    elif mode == "relaxed":
        extra = case_inputs.get("relaxed_required_section_ids")
        required_check_ids = list(extra) if isinstance(extra, list) else []
    else:
        flat_def = _flatten_definition_sections(defn.sections, tier)
        required_check_ids = [s.section_id for s in flat_def if s.required]
        if mode == "strict" and dt_val == "evidence_based_protocol":
            if "networks" in required_check_ids and not _resolve_required_node(
                dt_val, "networks", by_id, spec
            ):
                findings.append(
                    ValidationFinding(
                        code=FailureTaxonomy.MISSING_REQUIRED_SECTION.value,
                        severity=Severity.MEDIUM,
                        message=(
                            "Strict mode: expected `networks` or FNON/network prose "
                            "in section titles/content."
                        ),
                        reasons=[],
                        locator="networks",
                    )
                )
                required_check_ids = [r for r in required_check_ids if r != "networks"]

    for rid in required_check_ids:
        if mode == "strict":
            node = _resolve_required_node(dt_val, rid, by_id, spec)
        else:
            node = by_id.get(rid)

        if node is None:
            findings.append(
                ValidationFinding(
                    code=FailureTaxonomy.MISSING_REQUIRED_SECTION.value,
                    severity=Severity.HIGH,
                    message=f"Missing required section `{rid}` for {spec.document_type.value} ({mode}).",
                    reasons=["See document definition / relaxed emit list."],
                    locator=rid,
                )
            )
            continue

        if getattr(node, "is_placeholder", False):
            findings.append(
                ValidationFinding(
                    code=FailureTaxonomy.PLACEHOLDER_OR_EMPTY_SECTION.value,
                    severity=Severity.MEDIUM,
                    message=f"Required section `{rid}` is still marked placeholder.",
                    reasons=["Placeholder sections should be resolved before release builds."],
                    locator=rid,
                )
            )
        elif not _section_non_empty(node):
            findings.append(
                ValidationFinding(
                    code=FailureTaxonomy.PLACEHOLDER_OR_EMPTY_SECTION.value,
                    severity=Severity.HIGH,
                    message=f"Required section `{rid}` has no content, tables, or subsections.",
                    reasons=["Empty shells fail structure-native quality gates."],
                    locator=rid,
                )
            )

    min_refs = case_inputs.get("min_document_references")
    if min_refs is None:
        min_refs = 3 if defn.requires_evidence_appendix else 1
    min_refs = int(min_refs)
    if len(spec.references) < min_refs:
        findings.append(
            ValidationFinding(
                code=FailureTaxonomy.INSUFFICIENT_REFERENCES.value,
                severity=Severity.MEDIUM,
                message=(
                    f"Expected at least {min_refs} reference entries; "
                    f"found {len(spec.references)}."
                ),
                reasons=[],
            )
        )

    if (spec.condition_slug or spec.condition_name) and not _title_matches_condition(spec):
        findings.append(
            ValidationFinding(
                code=FailureTaxonomy.SPEC_IDENTITY_MISMATCH.value,
                severity=Severity.MEDIUM,
                message="Document title tokens do not align with condition_slug / condition_name.",
                reasons=[
                    f"condition_slug={spec.condition_slug!r}, "
                    f"condition_name={spec.condition_name!r}, title={spec.title!r}",
                ],
            )
        )

    # Order: compare relaxed canonical template when relaxed EBP; else definition ids
    actual_top = [s.section_id for s in spec.sections]
    if mode == "relaxed" and spec.document_type.value == "evidence_based_protocol":
        template = list(
            case_inputs.get("relaxed_section_order_template")
            or (
                "document_control",
                "inclusion_exclusion",
                "clinical_overview",
                "pathophysiology",
                "brain_anatomy",
                "phenotypes",
                "protocols_tdcs",
                "protocols_tps",
                "safety",
                "assessments",
                "responder_criteria",
                "followup",
                "evidence_summary",
                "references",
            )
        )
        present_ord = [i for i in template if i in actual_top]
        if len(present_ord) >= 2:
            idx_map = {sid: i for i, sid in enumerate(actual_top)}
            for a, b in zip(present_ord, present_ord[1:]):
                if a in idx_map and b in idx_map and idx_map[a] > idx_map[b]:
                    findings.append(
                        ValidationFinding(
                            code=FailureTaxonomy.SECTION_ORDER_OR_DEPTH_ANOMALY.value,
                            severity=Severity.LOW,
                            message=(
                                f"Top-level order vs canonical template: `{b}` before `{a}`."
                            ),
                            reasons=[],
                        )
                    )
                    break
    else:
        expected_top = _top_level_def_ids_for_order(defn, tier)
        present = [i for i in expected_top if i in actual_top]
        if len(present) >= 2:
            idx_map = {sid: i for i, sid in enumerate(actual_top)}
            for a, b in zip(present, present[1:]):
                if a in idx_map and b in idx_map and idx_map[a] > idx_map[b]:
                    findings.append(
                        ValidationFinding(
                            code=FailureTaxonomy.SECTION_ORDER_OR_DEPTH_ANOMALY.value,
                            severity=Severity.LOW,
                            message=(
                                f"Top-level section order diverges from definition: "
                                f"`{b}` appears before `{a}`."
                            ),
                            reasons=[],
                        )
                    )
                    break

    depths = [d for d, _ in _walk_spec_sections(spec.sections)]
    max_depth = max(depths) if depths else 0
    max_allowed = int(case_inputs.get("max_section_depth", 10))
    if max_depth > max_allowed:
        findings.append(
            ValidationFinding(
                code=FailureTaxonomy.SECTION_ORDER_OR_DEPTH_ANOMALY.value,
                severity=Severity.MEDIUM,
                message=f"Section tree max depth {max_depth} exceeds limit {max_allowed}.",
                reasons=[],
            )
        )

    return ValidatorReport(
        validator_id="document_spec_invariants",
        findings=findings,
    )
