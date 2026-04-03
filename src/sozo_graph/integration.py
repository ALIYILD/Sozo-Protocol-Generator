"""Bridge between LangGraph nodes and existing Sozo services.

Each function is called by a LangGraph node and delegates to the
appropriate existing service module. This eliminates parallel
implementations and ensures the graph uses the same battle-tested
code paths as the CLI and Streamlit UI.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. Condition Resolution
# ---------------------------------------------------------------------------

def resolve_condition(slug: str) -> dict:
    """Resolve condition slug to full ConditionSchema via condition registry.

    Returns a dict suitable for populating ConditionState, including
    the serialised schema_dict for downstream nodes.

    Raises ConditionNotFoundError (via registry) if slug is unknown.
    """
    from sozo_generator.conditions.registry import get_registry

    registry = get_registry()

    if not registry.exists(slug):
        return {
            "slug": slug,
            "display_name": "",
            "icd10": "",
            "schema_dict": {},
            "resolution_source": "registry_miss",
            "condition_valid": False,
        }

    schema = registry.get(slug)
    return {
        "slug": schema.slug,
        "display_name": schema.display_name,
        "icd10": schema.icd10,
        "schema_dict": schema.model_dump(),
        "resolution_source": "registry",
        "condition_valid": True,
    }


# ---------------------------------------------------------------------------
# 2. Evidence Pipeline
# ---------------------------------------------------------------------------

def run_evidence_pipeline(
    condition_slug: str,
    condition_name: str,
    schema_dict: dict,
) -> dict:
    """Run the full PRISMA evidence pipeline and return results for EvidenceState.

    Delegates to ResearchPipeline which orchestrates:
      MultiSourceSearch -> fuzzy dedup -> screening -> extraction -> scoring

    Args:
        condition_slug: e.g. "parkinsons"
        condition_name: e.g. "Parkinson's Disease"
        schema_dict: serialised ConditionSchema dict

    Returns:
        dict matching EvidenceState fields.
    """
    from sozo_generator.schemas.condition import ConditionSchema
    from sozo_generator.evidence.research_pipeline import ResearchPipeline
    from sozo_generator.core.settings import get_settings

    schema = ConditionSchema(**schema_dict)
    settings = get_settings()

    pipeline = ResearchPipeline(
        use_pubmed=True,
        use_crossref=getattr(settings, "use_crossref", True),
        use_semantic_scholar=getattr(settings, "use_semantic_scholar", True),
        persist_dir=getattr(settings, "pipeline_logs_dir", None),
    )

    # Determine target modality from condition's stimulation targets
    target_modality: Optional[str] = None
    if schema.stimulation_targets:
        target_modality = schema.stimulation_targets[0].modality.value

    result = pipeline.run(condition=schema, target_modality=target_modality)

    # Serialise top articles for state transport
    serialized_articles = []
    for article, ev_score in pipeline.get_top_evidence(n=50):
        serialized_articles.append({
            "pmid": article.pmid,
            "doi": article.doi,
            "title": article.title,
            "authors": article.authors,
            "journal": article.journal,
            "year": article.year,
            "abstract": article.abstract,
            "evidence_type": article.evidence_type.value,
            "evidence_level": article.evidence_level.value,
            "score": article.score,
            "evidence_grade": ev_score.final_grade if ev_score else "D",
            "quality_score": (
                ev_score.quality.composite_score
                if ev_score and ev_score.quality else 0
            ),
            "relevance_score": (
                ev_score.relevance.composite_score
                if ev_score and ev_score.relevance else 0
            ),
        })

    # Grade distribution
    grade_a = sum(1 for a in serialized_articles if a.get("evidence_grade") == "A")
    grade_b = sum(1 for a in serialized_articles if a.get("evidence_grade") == "B")
    grade_c = sum(1 for a in serialized_articles if a.get("evidence_grade") == "C")
    grade_d = sum(1 for a in serialized_articles if a.get("evidence_grade") == "D")

    evidence_sufficient = (grade_a + grade_b) >= 1

    # Reconstruct search queries for audit (best-effort)
    search_queries: list[str] = []
    try:
        plan = pipeline._query_planner.plan_condition(
            schema.slug, schema.display_name, schema.icd10,
        )
        search_queries = [q.query_string for q in plan.queries[:5]]
    except Exception:
        pass

    prisma = result.prisma_counts.__dict__ if result.prisma_counts else {}

    return {
        "search_queries": search_queries,
        "source_counts": (
            result.search_result.source_counts if result.search_result else {}
        ),
        "raw_article_count": result.total_identified,
        "unique_article_count": result.total_after_dedup,
        "screened_article_count": result.total_after_screening,
        "articles": serialized_articles,
        "evidence_summary": {
            "total_articles": len(serialized_articles),
            "grade_distribution": {
                "A": grade_a, "B": grade_b, "C": grade_c, "D": grade_d,
            },
        },
        "evidence_sufficient": evidence_sufficient,
        "evidence_gaps": result.errors or [],
        "prisma_counts": prisma,
        "pipeline_log_path": result.pipeline_log_path,
    }


# ---------------------------------------------------------------------------
# 3. Safety Evaluation
# ---------------------------------------------------------------------------

def evaluate_safety(
    condition_data: dict,
    patient_context: dict,
    target_modalities: list[str],
) -> dict:
    """Evaluate safety using contraindications, off-label rules, and drug interactions.

    Uses:
      - Hard contraindication map (inline, mirroring safety_policy_engine)
      - sozo_generator.safety.drug_interactions.get_interactions_for_drug_class
      - sozo_generator.knowledge.safety.SafetyValidator (when available)

    Args:
        condition_data: ConditionState dict (slug, schema_dict, etc.)
        patient_context: PatientContextState dict or empty dict
        target_modalities: list of modality slugs (e.g. ["tdcs", "tps"])

    Returns:
        dict matching SafetyState fields.
    """
    from sozo_generator.safety.drug_interactions import (
        get_interactions_for_drug_class,
    )

    # --- Hard contraindications per modality ---
    _HARD = {
        "tdcs": [
            "metallic_cranial_implant", "open_wound_at_electrode_site",
            "unstable_epilepsy",
        ],
        "tps": [
            "metallic_cranial_implant", "cochlear_implant",
            "increased_intracranial_pressure", "active_bleeding_disorder",
        ],
        "tavns": [
            "active_ear_infection", "vagotomy_history",
            "cardiac_arrhythmia_uncontrolled",
        ],
        "ces": [
            "metallic_cranial_implant", "cardiac_pacemaker",
        ],
        "all": [
            "pregnancy_first_trimester", "active_psychosis",
            "severe_skin_disease_at_site",
        ],
    }

    _OFF_LABEL = {
        "tps": "TPS is CE-marked ONLY for Alzheimer's disease. All other conditions are off-label.",
        "tdcs": "tDCS is CE-marked but off-label for most neuropsychiatric indications.",
        "tavns": "taVNS is CE-marked for epilepsy; off-label for neuropsychiatric conditions.",
    }
    _TPS_APPROVED = {"alzheimers"}

    patient_contras = set(
        c.lower().replace(" ", "_") for c in patient_context.get("contraindications", [])
    )

    blocking: list[str] = []
    warnings: list[str] = []
    consent_requirements: list[str] = ["Informed consent for neuromodulation treatment"]
    off_label_flags: list[str] = []
    modality_restrictions: list[dict] = []
    contraindications_found: list[dict] = []
    condition_slug = condition_data.get("slug", "")

    for modality in target_modalities:
        mod = modality.lower()
        hard = _HARD.get(mod, []) + _HARD.get("all", [])
        for ci in hard:
            if ci in patient_contras:
                blocking.append(f"{mod}: {ci}")
                contraindications_found.append({
                    "modality": mod,
                    "contraindication": ci,
                })

        # Doctor auth for TPS
        if mod == "tps":
            consent_requirements.append("Doctor authorization required for TPS")

        # Off-label
        if mod in _OFF_LABEL:
            if mod == "tps" and condition_slug not in _TPS_APPROVED:
                off_label_flags.append(_OFF_LABEL[mod])
                consent_requirements.append(f"Off-label consent required for {mod.upper()}")
            elif mod != "tps":
                off_label_flags.append(_OFF_LABEL[mod])

    # --- Drug interaction checking ---
    medications = [m.lower() for m in patient_context.get("current_medications", [])]
    for med in medications:
        interactions = get_interactions_for_drug_class(med)
        for ix in interactions:
            affected_here = [
                m for m in ix.modalities_affected
                if m.lower() in [t.lower() for t in target_modalities]
            ]
            if not affected_here:
                continue

            if ix.severity == "contraindicated":
                blocking.append(
                    f"{ix.drug_class} contraindicated with "
                    f"{', '.join(affected_here)}"
                )
            elif ix.severity == "major":
                warnings.append(
                    f"Major interaction: {ix.drug_class} with "
                    f"{', '.join(affected_here)} -- {ix.recommendation[:120]}"
                )
            else:
                warnings.append(
                    f"{ix.severity.capitalize()} interaction: {ix.drug_class} "
                    f"with {', '.join(affected_here)}"
                )

    # --- Knowledge-base safety validation (best-effort) ---
    try:
        from sozo_generator.knowledge.safety import SafetyValidator

        schema_dict = condition_data.get("schema_dict", {})
        protocols = schema_dict.get("protocols", [])
        safety_rules = schema_dict.get("safety_rules", [])
        if protocols:
            sv = SafetyValidator()
            report = sv.validate_protocol(
                condition_slug=condition_slug,
                protocols=(
                    [p if isinstance(p, dict) else p for p in protocols]
                ),
                safety_rules=safety_rules,
            )
            for check in report.checks:
                if not check.passed and check.severity == "block":
                    blocking.append(f"{check.check_type}: {check.message}")
                elif not check.passed and check.severity == "warning":
                    warnings.append(check.message)
    except Exception as exc:
        logger.debug("Knowledge-base safety validation skipped: %s", exc)

    safety_cleared = len(blocking) == 0

    return {
        "contraindications_found": contraindications_found,
        "modality_restrictions": modality_restrictions,
        "consent_requirements": consent_requirements,
        "off_label_flags": off_label_flags,
        "safety_cleared": safety_cleared,
        "blocking_contraindications": blocking,
        "proceed_with_warnings": warnings,
    }


# ---------------------------------------------------------------------------
# 4. Protocol Composition
# ---------------------------------------------------------------------------

def compose_protocol_sections(
    condition_data: dict,
    evidence_data: dict,
    safety_data: dict,
    protocol_data: dict,
) -> dict:
    """Compose protocol sections using the GenerationService's canonical path.

    First attempts the knowledge-base canonical assembler. Falls back to
    LLM composition (matching the existing protocol_composer node logic)
    and finally to data-driven fallback.

    Returns:
        dict with "composed_sections" key (list of section dicts).
    """
    slug = condition_data.get("slug", "")
    tier = protocol_data.get("tier", "fellow")

    # --- Attempt 1: Canonical assembler via GenerationService ---
    try:
        from sozo_generator.generation.service import GenerationService

        service = GenerationService(with_visuals=False, with_qa=False)
        if service.can_route_canonical(slug, "evidence_based_protocol"):
            result = service.generate_canonical(
                condition=slug,
                doc_type="evidence_based_protocol",
                tier=tier,
            )
            if result.success and result.output_path:
                logger.info(
                    "Canonical composition succeeded for %s: %s",
                    slug, result.output_path,
                )
                # We don't get individual sections back from canonical path,
                # but we can note it was canonical for the renderer
                return {
                    "composed_sections": [{
                        "section_id": "canonical_document",
                        "title": f"Evidence-Based Protocol -- {condition_data.get('display_name', slug)}",
                        "content": f"[Canonical document rendered at {result.output_path}]",
                        "cited_evidence_ids": [],
                        "confidence": "high",
                        "generation_method": "canonical_assembler",
                        "claims": [],
                    }],
                    "doc_type": "evidence_based_protocol",
                    "_canonical_output_path": result.output_path,
                }
    except Exception as exc:
        logger.debug("Canonical composition unavailable: %s", exc)

    # --- Attempt 2: LLM composition (same as existing protocol_composer) ---
    try:
        from sozo_generator.core.settings import get_settings
        settings = get_settings()

        if settings.anthropic_api_key:
            return _llm_compose(condition_data, evidence_data, safety_data, protocol_data)
    except Exception as exc:
        logger.warning("LLM composition failed: %s", exc)

    # --- Attempt 3: Data-driven fallback ---
    return _data_driven_compose(condition_data, protocol_data)


def _llm_compose(
    condition_data: dict,
    evidence_data: dict,
    safety_data: dict,
    protocol_data: dict,
) -> dict:
    """LLM-based section composition (mirrors protocol_composer node)."""
    import json as _json

    import anthropic
    from sozo_generator.core.settings import get_settings

    settings = get_settings()
    articles = evidence_data.get("articles", [])
    base_sequence = protocol_data.get("base_sequence", {})

    evidence_pool = []
    for a in articles[:30]:
        evidence_pool.append({
            "id": a.get("pmid") or a.get("doi") or "",
            "title": a.get("title", ""),
            "authors": a.get("authors", [])[:3],
            "year": a.get("year"),
            "grade": a.get("evidence_grade", "D"),
            "abstract_excerpt": (a.get("abstract") or "")[:300],
        })

    user_message = _json.dumps({
        "condition": {
            "slug": condition_data.get("slug"),
            "display_name": condition_data.get("display_name"),
            "icd10": condition_data.get("icd10"),
        },
        "base_sequence_summary": {
            "phases": len(base_sequence.get("phases", [])),
            "modalities": base_sequence.get("all_modalities", []),
            "total_duration_min": base_sequence.get("total_duration_min"),
        },
        "evidence_pool": evidence_pool,
        "safety_flags": {
            "off_label_flags": safety_data.get("off_label_flags", []),
            "consent_requirements": safety_data.get("consent_requirements", []),
            "warnings": safety_data.get("proceed_with_warnings", []),
        },
        "sections_to_compose": [
            {"section_id": "overview", "title": "Clinical Overview"},
            {"section_id": "pathophysiology", "title": "Pathophysiology & Rationale"},
            {"section_id": "stimulation_protocol", "title": "Stimulation Protocol"},
            {"section_id": "safety_monitoring", "title": "Safety & Monitoring"},
            {"section_id": "outcome_measures", "title": "Outcome Measures"},
        ],
    }, default=str)

    # Reuse the system prompt from the existing composer node
    from sozo_graph.nodes.protocol_composer import COMPOSER_SYSTEM_PROMPT

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=COMPOSER_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = response.content[0].text
    import re
    try:
        parsed = _json.loads(raw_text)
    except _json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            parsed = _json.loads(match.group())
        else:
            raise ValueError("LLM response is not valid JSON")

    sections = parsed.get("sections", [])
    return {"composed_sections": sections}


def _data_driven_compose(condition_data: dict, protocol_data: dict) -> dict:
    """Fallback: build sections from condition schema data."""
    schema_dict = condition_data.get("schema_dict", {})
    sections = [
        {
            "section_id": "overview",
            "title": "Clinical Overview",
            "content": schema_dict.get(
                "overview", "[REVIEW REQUIRED: No overview available]"
            ),
            "cited_evidence_ids": [],
            "confidence": "medium",
            "generation_method": "data_driven",
            "claims": [],
        },
        {
            "section_id": "pathophysiology",
            "title": "Pathophysiology & Rationale",
            "content": schema_dict.get("pathophysiology", "[REVIEW REQUIRED]"),
            "cited_evidence_ids": [],
            "confidence": "medium",
            "generation_method": "data_driven",
            "claims": [],
        },
    ]
    return {"composed_sections": sections}


# ---------------------------------------------------------------------------
# 5. Evidence Grounding Validation
# ---------------------------------------------------------------------------

def validate_evidence_grounding(
    protocol_data: dict,
    evidence_data: dict,
) -> dict:
    """Validate all citations in composed protocol sections.

    Uses the same grounding checks as the existing grounding_validator node:
      - Verify cited evidence IDs exist in the evidence pool
      - Check claims have evidence references
      - Scan for prohibited language

    Returns:
        dict with "grounding_score" (float) and "grounding_issues" (list).
    """
    composed = protocol_data.get("composed_sections", [])
    articles = evidence_data.get("articles", [])

    if not composed:
        return {
            "grounding_score": 0.0,
            "grounding_issues": [
                {"severity": "block", "message": "No sections composed"}
            ],
        }

    # Build set of known evidence IDs
    valid_ids: set[str] = set()
    for a in articles:
        if a.get("pmid"):
            valid_ids.add(a["pmid"])
        if a.get("doi"):
            valid_ids.add(a["doi"])

    all_issues: list[dict] = []
    total_citations = 0
    verified_citations = 0

    for section in composed:
        section_id = section.get("section_id", "unknown")
        cited = section.get("cited_evidence_ids", [])
        total_citations += len(cited)

        for eid in cited:
            if eid in valid_ids:
                verified_citations += 1
            else:
                all_issues.append({
                    "severity": "warning",
                    "section_id": section_id,
                    "message": f"Citation '{eid}' not found in evidence pool",
                })

        # Claims without evidence
        for claim in section.get("claims", []):
            if not claim.get("evidence_ids"):
                all_issues.append({
                    "severity": "block",
                    "section_id": section_id,
                    "message": (
                        f"Claim '{claim.get('claim_text', '')[:60]}' "
                        f"has no evidence IDs"
                    ),
                })

        # Prohibited language
        content = section.get("content", "").lower()
        prohibited = [
            "proven to cure", "guaranteed", "100% effective",
            "fda-approved for neuromodulation",
        ]
        for phrase in prohibited:
            if phrase in content:
                all_issues.append({
                    "severity": "block",
                    "section_id": section_id,
                    "message": f"Prohibited language: '{phrase}'",
                })

    grounding_score = (
        verified_citations / total_citations if total_citations > 0 else 0.0
    )

    return {
        "grounding_score": round(grounding_score, 3),
        "grounding_issues": all_issues,
    }


# ---------------------------------------------------------------------------
# 6. QA Checks
# ---------------------------------------------------------------------------

def run_qa_checks(
    protocol_data: dict,
    condition_slug: str,
    condition_schema_dict: dict,
) -> dict:
    """Run QA engine checks on the generated protocol.

    Delegates to sozo_generator.qa.engine.QAEngine for condition-level
    validation.  Falls back gracefully if QA dependencies are missing.

    Returns:
        dict with "qa_passed" (bool) and "qa_issues" (list[str]).
    """
    try:
        from sozo_generator.qa.engine import QAEngine
        from sozo_generator.schemas.condition import ConditionSchema

        schema = ConditionSchema(**condition_schema_dict)
        engine = QAEngine()
        report = engine.check_condition(schema)

        return {
            "qa_passed": report.passed,
            "qa_issues": [
                f"[{i.severity.value}] {i.message}" for i in report.issues[:20]
            ],
        }
    except AttributeError:
        # check_condition may not exist -- try run_condition_qa
        try:
            from sozo_generator.qa.engine import QAEngine
            from sozo_generator.schemas.condition import ConditionSchema

            schema = ConditionSchema(**condition_schema_dict)
            engine = QAEngine()
            report = engine.run_condition_qa(schema)

            return {
                "qa_passed": report.passed,
                "qa_issues": [
                    f"[{i.severity.value}] {i.message}" for i in report.issues[:20]
                ],
            }
        except Exception as exc:
            logger.warning("QA engine fallback failed: %s", exc)
            return {"qa_passed": None, "qa_issues": [f"QA unavailable: {exc}"]}
    except Exception as exc:
        logger.warning("QA checks skipped: %s", exc)
        return {"qa_passed": None, "qa_issues": [f"QA skipped: {exc}"]}


# ---------------------------------------------------------------------------
# 7. Document Rendering
# ---------------------------------------------------------------------------

def render_output(
    protocol_data: dict,
    condition_data: dict,
    evidence_data: dict,
    review_data: dict,
    request_id: str,
    state_version: str,
) -> dict:
    """Render final document output (JSON + DOCX + PRISMA summary).

    Delegates to:
      - sozo_generator.docx.renderer.DocumentRenderer
      - sozo_generator.schemas.documents.DocumentSpec

    Returns:
        dict with "output_paths" and "output_formats".
    """
    import json as _json
    from pathlib import Path

    from sozo_generator.core.settings import get_settings

    settings = get_settings()
    slug = condition_data.get("slug", "unknown")
    output_dir = settings.output_dir / "protocols" / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    output_paths: dict[str, str] = {}

    # --- 1. Protocol JSON ---
    protocol_json_path = output_dir / f"{slug}_protocol.json"
    protocol_json = {
        "request_id": request_id,
        "condition": {
            "slug": slug,
            "display_name": condition_data.get("display_name"),
            "icd10": condition_data.get("icd10"),
        },
        "base_sequence": protocol_data.get("base_sequence"),
        "sections": protocol_data.get("composed_sections"),
        "grounding_score": protocol_data.get("grounding_score"),
        "evidence_summary": evidence_data.get("evidence_summary"),
        "review": {
            "status": review_data.get("status"),
            "reviewer_id": review_data.get("reviewer_id"),
            "approval_stamp": review_data.get("approval_stamp"),
            "revision_number": review_data.get("revision_number"),
        },
        "version": state_version,
    }
    protocol_json_path.write_text(
        _json.dumps(protocol_json, indent=2, default=str)
    )
    output_paths["json"] = str(protocol_json_path)

    # --- 2. PRISMA summary ---
    try:
        prisma_counts = evidence_data.get("prisma_counts", {})
        if prisma_counts:
            prisma_path = output_dir / f"{slug}_prisma.txt"
            lines = [
                f"PRISMA Summary for {condition_data.get('display_name', slug)}",
                f"Records identified: {prisma_counts.get('records_identified', 0)}",
                f"After dedup: {prisma_counts.get('records_after_dedup', 0)}",
                f"Screened: {prisma_counts.get('records_screened', 0)}",
                f"Included: {prisma_counts.get('studies_included', 0)}",
            ]
            prisma_path.write_text("\n".join(lines))
            output_paths["prisma"] = str(prisma_path)
    except Exception as exc:
        logger.debug("PRISMA summary skipped: %s", exc)

    # --- 3. DOCX rendering ---
    try:
        from sozo_generator.schemas.documents import DocumentSpec, SectionContent
        from sozo_generator.core.enums import DocumentType, Tier

        sections = []
        for s in protocol_data.get("composed_sections", []):
            sections.append(SectionContent(
                section_id=s.get("section_id", ""),
                title=s.get("title", ""),
                content=s.get("content", ""),
                evidence_pmids=s.get("cited_evidence_ids", []),
                confidence_label=s.get("confidence"),
            ))

        tier_str = protocol_data.get("tier", "fellow")
        spec = DocumentSpec(
            document_type=DocumentType.EVIDENCE_BASED_PROTOCOL,
            tier=Tier(tier_str) if tier_str in ("fellow", "partners") else Tier.FELLOW,
            condition_slug=slug,
            condition_name=condition_data.get("display_name", slug),
            title=f"Evidence-Based Protocol -- {condition_data.get('display_name', slug)}",
            sections=sections,
            references=condition_data.get("schema_dict", {}).get("references", []),
            build_id=request_id,
        )

        from sozo_generator.docx.renderer import DocumentRenderer
        renderer = DocumentRenderer(output_dir=str(output_dir))
        docx_path = renderer.render(spec)
        output_paths["docx"] = str(docx_path)

    except Exception as exc:
        logger.warning("DOCX rendering failed: %s", exc)

    return {
        "output_paths": output_paths,
        "output_formats": list(output_paths.keys()),
    }


# ---------------------------------------------------------------------------
# 8. Audit Hash
# ---------------------------------------------------------------------------

def compute_audit_hash(data: dict) -> str:
    """SHA-256 hash for audit trail integrity verification."""
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, default=str).encode()
    ).hexdigest()
