"""PersonalizationEngine -- 4-layer protocol adaptation for individual patients.

Layer 1 (Rules/Deterministic): Safety constraints
Layer 2 (Evidence-Weighted):   Protocol selection via phenotype + evidence scoring
Layer 3 (EEG-Driven):          Target refinement using EEG biomarkers (V2)
Layer 4 (Explanation):          Human-readable rationale generation
"""

from __future__ import annotations

import logging
from typing import Optional

from sozo_generator.safety.drug_interactions import (
    DRUG_INTERACTIONS,
    DrugInteraction,
    get_interactions_for_drug_class,
)
from sozo_generator.scoring.confidence import (
    ConfidenceBand,
    ConfidenceScorer,
    DataCompletenessInput,
    EvidenceStrengthInput,
    PhenotypeMatchInput,
)

from .eeg_analyzer import EEGAnalyzer, EEGAnalysisResult
from .models import PersonalizationRequest, PersonalizationResult, ProtocolCandidate
from .phenotype_matcher import PhenotypeMatcher
from .protocol_ranker import ProtocolRanker

logger = logging.getLogger(__name__)

# ── Universal contraindication keywords ─────────────────────────────────
# These terms, when found in patient medical_history, block specific modalities.

UNIVERSAL_CONTRAINDICATIONS: list[dict] = [
    {
        "term": "cardiac pacemaker",
        "blocks": ["tdcs", "tps", "tavns", "ces"],
        "reason": "Electrical/mechanical stimulation is contraindicated with implanted cardiac pacemakers.",
    },
    {
        "term": "cochlear implant",
        "blocks": ["tps"],
        "reason": "Transcranial pulse stimulation is contraindicated near cochlear implants.",
    },
    {
        "term": "deep brain stimulator",
        "blocks": ["tdcs", "tps"],
        "reason": "Existing intracranial stimulation devices are contraindicated with tDCS/TPS.",
    },
    {
        "term": "metallic cranial implant",
        "blocks": ["tdcs", "tps"],
        "reason": "Metallic implants in the skull may distort current flow and create hotspots.",
    },
    {
        "term": "skull plate",
        "blocks": ["tdcs", "tps"],
        "reason": "Skull plates may distort current distribution and increase risk.",
    },
    {
        "term": "unstable epilepsy",
        "blocks": ["tdcs", "tps"],
        "reason": "Uncontrolled seizure disorder is an absolute contraindication for excitatory stimulation.",
    },
    {
        "term": "pregnancy",
        "blocks": ["tdcs", "tps", "ces"],
        "restricts": ["tavns"],
        "reason": "Insufficient safety data for transcranial stimulation during pregnancy.",
    },
    {
        "term": "intracranial lesion",
        "blocks": ["tdcs", "tps"],
        "reason": "Active intracranial lesion alters current distribution unpredictably.",
    },
    {
        "term": "raised intracranial pressure",
        "blocks": ["tps"],
        "reason": "TPS mechanical forces may worsen raised ICP.",
    },
]

# ── Age restriction thresholds ──────────────────────────────────────────

PEDIATRIC_AGE_THRESHOLD = 18
GERIATRIC_AGE_THRESHOLD = 80


class PersonalizationEngine:
    """Four-layer personalization engine for neuromodulation protocols.

    Orchestrates safety checking, phenotype matching, protocol ranking,
    EEG-driven refinement, confidence scoring, and explanation generation.

    Parameters
    ----------
    condition_schema : dict
        A ConditionSchema serialised to dict (or the raw YAML/JSON content).
        Must include ``slug``, ``phenotypes``, ``protocols``,
        ``contraindications``, ``exclusion_criteria``, etc.
    phenotype_matcher : PhenotypeMatcher, optional
        Custom phenotype matcher instance.
    protocol_ranker : ProtocolRanker, optional
        Custom protocol ranker instance.
    eeg_analyzer : EEGAnalyzer, optional
        Custom EEG analyzer instance.
    confidence_scorer : ConfidenceScorer, optional
        Custom confidence scorer instance.
    """

    def __init__(
        self,
        condition_schema: dict,
        *,
        phenotype_matcher: Optional[PhenotypeMatcher] = None,
        protocol_ranker: Optional[ProtocolRanker] = None,
        eeg_analyzer: Optional[EEGAnalyzer] = None,
        confidence_scorer: Optional[ConfidenceScorer] = None,
    ) -> None:
        self.condition = condition_schema
        self.matcher = phenotype_matcher or PhenotypeMatcher()
        self.ranker = protocol_ranker or ProtocolRanker()
        self.eeg_analyzer = eeg_analyzer or EEGAnalyzer()
        self.confidence_scorer = confidence_scorer or ConfidenceScorer()

    # ================================================================== #
    # Main entry point                                                    #
    # ================================================================== #

    def personalize(self, request: PersonalizationRequest) -> PersonalizationResult:
        """Run the full 4-layer personalization pipeline.

        Parameters
        ----------
        request : PersonalizationRequest
            Complete patient data and condition context.

        Returns
        -------
        PersonalizationResult
            Full result including safety checks, ranked protocols, EEG
            adjustments, explanation, and confidence scoring.
        """
        trace: list[dict] = []

        # ── Layer 1: Safety ─────────────────────────────────────────────
        logger.info("Layer 1: Running safety checks for %s", request.condition_slug)
        safety = self._layer1_safety(request)
        trace.append({"layer": 1, "name": "safety", "output": {
            "blocked": safety["blocked_modalities"],
            "restricted": safety["restricted_modalities"],
            "warnings": safety["safety_warnings"],
            "interaction_count": len(safety["medication_interactions"]),
        }})

        # ── Layer 2: Protocol Selection ─────────────────────────────────
        logger.info("Layer 2: Matching phenotype and ranking protocols")
        selection = self._layer2_selection(request, safety)
        trace.append({"layer": 2, "name": "selection", "output": {
            "matched_phenotype": selection["matched_phenotype"],
            "phenotype_confidence": selection["phenotype_confidence"],
            "candidate_count": len(selection["ranked_protocols"]),
        }})

        # ── Layer 3: EEG Refinement ─────────────────────────────────────
        logger.info("Layer 3: EEG-driven refinement")
        eeg_result = self._layer3_eeg(request, selection)
        trace.append({"layer": 3, "name": "eeg_refinement", "output": {
            "adjustments": len(eeg_result.get("eeg_adjustments", [])),
            "target_refined": eeg_result.get("target_refinement") is not None,
        }})

        # ── Layer 4: Explanation ────────────────────────────────────────
        logger.info("Layer 4: Generating explanation and confidence score")
        explanation_result = self._layer4_explanation(
            request, safety, selection, eeg_result,
        )
        trace.append({"layer": 4, "name": "explanation", "output": {
            "confidence_score": explanation_result["confidence_score"],
            "confidence_band": explanation_result["confidence_band"],
        }})

        # ── Assemble result ─────────────────────────────────────────────
        ranked = selection["ranked_protocols"]
        recommended = ranked[0] if ranked else None

        # Apply EEG adjustments to the recommended protocol
        if recommended and eeg_result.get("target_refinement"):
            refinement = eeg_result["target_refinement"]
            recommended = ProtocolCandidate(
                modality=recommended.modality,
                target=refinement.get("suggested_target", recommended.target),
                montage={
                    **recommended.montage,
                    "eeg_refined_target": refinement.get("suggested_target"),
                    "eeg_laterality": refinement.get("laterality"),
                },
                parameters=recommended.parameters,
                schedule=recommended.schedule,
                phenotype_slug=recommended.phenotype_slug,
                evidence_level=recommended.evidence_level,
                score=recommended.score,
                rationale=(
                    recommended.rationale + " "
                    + refinement.get("rationale", "")
                ),
            )

        result = PersonalizationResult(
            condition_slug=request.condition_slug,
            safety_cleared=safety["safety_cleared"],
            blocked_modalities=safety["blocked_modalities"],
            restricted_modalities=safety["restricted_modalities"],
            safety_warnings=safety["safety_warnings"],
            medication_interactions=safety["medication_interactions"],
            matched_phenotype=selection["matched_phenotype"],
            phenotype_confidence=selection["phenotype_confidence"],
            ranked_protocols=ranked,
            recommended_protocol=recommended,
            eeg_adjustments=eeg_result.get("eeg_adjustments", []),
            target_refinement=eeg_result.get("target_refinement"),
            explanation=explanation_result["explanation"],
            confidence_score=explanation_result["confidence_score"],
            confidence_band=explanation_result["confidence_band"],
            decision_trace=trace,
        )

        logger.info(
            "Personalization complete: condition=%s, cleared=%s, "
            "recommended=%s, confidence=%s (%.3f)",
            result.condition_slug,
            result.safety_cleared,
            result.recommended_protocol.modality if result.recommended_protocol else "none",
            result.confidence_band,
            result.confidence_score,
        )

        return result

    # ================================================================== #
    # Layer 1: Safety (Rules / Deterministic)                             #
    # ================================================================== #

    def _layer1_safety(self, request: PersonalizationRequest) -> dict:
        """Check contraindications, drug interactions, and age restrictions.

        Returns
        -------
        dict with keys: safety_cleared, blocked_modalities,
        restricted_modalities, safety_warnings, medication_interactions.
        """
        blocked: set[str] = set()
        restricted: set[str] = set()
        warnings: list[str] = []
        interactions: list[dict] = []

        # ── 1a. Universal contraindications vs medical_history ──────────
        history_lower = [h.lower() for h in request.medical_history]
        for contra in UNIVERSAL_CONTRAINDICATIONS:
            term = contra["term"].lower()
            if any(term in h for h in history_lower):
                for mod in contra.get("blocks", []):
                    blocked.add(mod)
                for mod in contra.get("restricts", []):
                    restricted.add(mod)
                warnings.append(
                    f"[CONTRAINDICATION] {contra['reason']} "
                    f"(matched: '{contra['term']}')"
                )

        # ── 1b. Condition-level contraindications ───────────────────────
        condition_contras: list[str] = self.condition.get("contraindications", [])
        for cc in condition_contras:
            cc_lower = cc.lower()
            if any(cc_lower in h or h in cc_lower for h in history_lower):
                warnings.append(
                    f"[CONDITION CONTRAINDICATION] Patient history matches "
                    f"condition exclusion: '{cc}'"
                )

        # ── 1c. Condition exclusion criteria ────────────────────────────
        exclusion_criteria: list[str] = self.condition.get("exclusion_criteria", [])
        for exc in exclusion_criteria:
            exc_lower = exc.lower()
            if any(exc_lower in h or h in exc_lower for h in history_lower):
                warnings.append(
                    f"[EXCLUSION CRITERION] Patient matches exclusion: '{exc}'"
                )

        # ── 1d. Medication interactions ─────────────────────────────────
        for med in request.medications:
            drug_name = med.get("name", "").lower()
            drug_class = med.get("drug_class", "").lower()

            # Search by class and by name
            found: list[DrugInteraction] = []
            if drug_class:
                found.extend(get_interactions_for_drug_class(drug_class))
            if drug_name:
                found.extend(get_interactions_for_drug_class(drug_name))

            # Deduplicate
            seen_ids: set[int] = set()
            for interaction in found:
                iid = id(interaction)
                if iid in seen_ids:
                    continue
                seen_ids.add(iid)

                interaction_dict = {
                    "drug": med.get("name", drug_class),
                    "drug_class": interaction.drug_class,
                    "severity": interaction.severity,
                    "modalities_affected": interaction.modalities_affected,
                    "mechanism": interaction.mechanism,
                    "recommendation": interaction.recommendation,
                }
                interactions.append(interaction_dict)

                if interaction.severity == "contraindicated":
                    for mod in interaction.modalities_affected:
                        blocked.add(mod.lower())
                    warnings.append(
                        f"[DRUG CONTRAINDICATION] {med.get('name', drug_class)}: "
                        f"{interaction.recommendation}"
                    )
                elif interaction.severity == "major":
                    for mod in interaction.modalities_affected:
                        restricted.add(mod.lower())
                    warnings.append(
                        f"[DRUG MAJOR INTERACTION] {med.get('name', drug_class)}: "
                        f"{interaction.recommendation}"
                    )
                elif interaction.severity == "moderate":
                    warnings.append(
                        f"[DRUG MODERATE INTERACTION] {med.get('name', drug_class)}: "
                        f"{interaction.recommendation}"
                    )

            # Check interaction_flags from the medication record
            for flag in med.get("interaction_flags", []):
                flag_lower = flag.lower()
                if "seizure" in flag_lower:
                    restricted.add("tdcs")
                    restricted.add("tps")
                    warnings.append(
                        f"[MEDICATION FLAG] {med.get('name', 'unknown')}: "
                        f"'{flag}' -- caution with excitatory stimulation."
                    )

        # ── 1e. Age-based restrictions ──────────────────────────────────
        age = request.patient_demographics.get("age")
        if age is not None:
            if age < PEDIATRIC_AGE_THRESHOLD:
                warnings.append(
                    f"[AGE CAUTION] Patient is {age} years old (pediatric). "
                    f"Reduced stimulation parameters recommended. "
                    f"Parental/guardian consent required."
                )
                restricted.update(["tdcs", "tps"])
            if age >= GERIATRIC_AGE_THRESHOLD:
                warnings.append(
                    f"[AGE CAUTION] Patient is {age} years old (geriatric). "
                    f"Monitor for orthostatic hypotension and cardiac effects. "
                    f"Consider reduced session duration."
                )
                restricted.add("tavns")
                restricted.add("ces")

        safety_cleared = len(blocked) == 0 and not any(
            "[CONTRAINDICATION]" in w or "[DRUG CONTRAINDICATION]" in w
            for w in warnings
        )

        return {
            "safety_cleared": safety_cleared,
            "blocked_modalities": sorted(blocked),
            "restricted_modalities": sorted(restricted),
            "safety_warnings": warnings,
            "medication_interactions": interactions,
        }

    # ================================================================== #
    # Layer 2: Evidence-Weighted Protocol Selection                       #
    # ================================================================== #

    def _layer2_selection(
        self, request: PersonalizationRequest, safety: dict,
    ) -> dict:
        """Match phenotype, then rank protocols by composite score.

        Returns
        -------
        dict with keys: matched_phenotype, phenotype_confidence,
        ranked_protocols.
        """
        # Phenotype matching
        phenotypes = self.condition.get("phenotypes", [])
        # Convert Pydantic models to dicts if needed
        pheno_dicts = []
        for p in phenotypes:
            if hasattr(p, "model_dump"):
                pheno_dicts.append(p.model_dump())
            elif isinstance(p, dict):
                pheno_dicts.append(p)
            else:
                pheno_dicts.append(dict(p))

        match_result = self.matcher.match(
            phenotypes=pheno_dicts,
            patient_symptoms=request.symptoms,
            treatment_history=request.treatment_history,
        )

        # Protocol ranking
        protocols = self.condition.get("protocols", [])
        proto_dicts = []
        for p in protocols:
            if hasattr(p, "model_dump"):
                proto_dicts.append(p.model_dump())
            elif isinstance(p, dict):
                proto_dicts.append(p)
            else:
                proto_dicts.append(dict(p))

        ranked = self.ranker.rank(
            protocols=proto_dicts,
            matched_phenotype_slug=match_result.phenotype_slug,
            phenotype_confidence=match_result.confidence,
            treatment_history=request.treatment_history,
            blocked_modalities=safety["blocked_modalities"],
            restricted_modalities=safety["restricted_modalities"],
            target_modalities=request.target_modalities,
        )

        return {
            "matched_phenotype": match_result.phenotype_slug,
            "phenotype_confidence": match_result.confidence,
            "phenotype_match_details": match_result,
            "ranked_protocols": ranked,
        }

    # ================================================================== #
    # Layer 3: EEG-Driven Refinement                                     #
    # ================================================================== #

    def _layer3_eeg(
        self,
        request: PersonalizationRequest,
        selection: dict,
    ) -> dict:
        """Analyse EEG features and produce parameter/target adjustments.

        Returns
        -------
        dict with keys: eeg_adjustments, target_refinement, eeg_explanation.
        """
        if not request.eeg_features:
            logger.info("No EEG features provided -- skipping Layer 3.")
            return {
                "eeg_adjustments": [],
                "target_refinement": None,
                "eeg_explanation": "No EEG data available for refinement.",
            }

        # Determine the current primary target from top-ranked protocol
        ranked = selection.get("ranked_protocols", [])
        current_target = ranked[0].target if ranked else None

        analysis: EEGAnalysisResult = self.eeg_analyzer.analyze(
            eeg_features=request.eeg_features,
            condition_slug=request.condition_slug,
            current_target=current_target,
        )

        # Serialize adjustments to dicts for the result
        adj_dicts = [
            {
                "parameter": a.parameter,
                "original_value": a.original_value,
                "adjusted_value": a.adjusted_value,
                "reason": a.reason,
                "confidence": a.confidence,
            }
            for a in analysis.adjustments
        ]

        # Serialize target refinement
        tr_dict = None
        if analysis.target_refinement:
            tr = analysis.target_refinement
            tr_dict = {
                "suggested_target": tr.suggested_target,
                "laterality": tr.laterality,
                "rationale": tr.rationale,
                "network_basis": tr.network_basis,
                "confidence": tr.confidence,
            }

        return {
            "eeg_adjustments": adj_dicts,
            "target_refinement": tr_dict,
            "eeg_explanation": analysis.explanation,
            "network_findings": analysis.network_findings,
        }

    # ================================================================== #
    # Layer 4: Explanation & Confidence                                   #
    # ================================================================== #

    def _layer4_explanation(
        self,
        request: PersonalizationRequest,
        safety: dict,
        selection: dict,
        eeg_result: dict,
    ) -> dict:
        """Generate human-readable explanation and compute confidence.

        Returns
        -------
        dict with keys: explanation, confidence_score, confidence_band.
        """
        # ── Confidence scoring ──────────────────────────────────────────
        evidence_level = self.condition.get("overall_evidence_quality", "medium")
        if hasattr(evidence_level, "value"):
            evidence_level = evidence_level.value

        references = self.condition.get("references", [])
        num_rcts = sum(
            1 for r in references
            if r.get("type", "").lower() in ("rct", "large_rct", "controlled_trial")
        )
        num_meta = sum(
            1 for r in references
            if r.get("type", "").lower() in ("meta_analysis", "systematic_review")
        )

        evidence_input = EvidenceStrengthInput(
            overall_evidence_level=evidence_level,
            num_supporting_articles=len(references),
            num_rcts=num_rcts,
            num_meta_analyses=num_meta,
            has_clinical_guideline=any(
                r.get("type", "").lower() == "clinical_practice_guideline"
                for r in references
            ),
            contradicting_evidence_count=0,
            evidence_recency_years=2.0,  # Default assumption
        )

        has_prior_response = any(
            tx.get("outcome", "").lower() in ("responder", "partial_responder")
            for tx in request.treatment_history
        )

        data_input = DataCompletenessInput(
            has_demographics=bool(request.patient_demographics),
            has_symptom_scores=len(request.symptoms) > 0,
            num_symptom_scales=len(request.symptoms),
            has_treatment_history=len(request.treatment_history) > 0,
            has_medications=len(request.medications) > 0,
            has_eeg=request.eeg_features is not None,
            has_brain_map=False,
            has_prior_response=has_prior_response,
            total_assessments=len(request.symptoms),
        )

        pheno_match = selection.get("phenotype_match_details")
        phenotype_input = PhenotypeMatchInput(
            condition_slug=request.condition_slug,
            matched_phenotype=selection.get("matched_phenotype"),
            symptom_overlap_ratio=pheno_match.symptom_overlap if pheno_match else 0.0,
            network_concordance=0.5 if request.eeg_features else 0.0,
            treatment_history_consistent=has_prior_response,
        )

        confidence_breakdown = self.confidence_scorer.score(
            evidence=evidence_input,
            data=data_input,
            phenotype=phenotype_input,
        )

        # ── Explanation text ────────────────────────────────────────────
        explanation = self._build_full_explanation(
            request, safety, selection, eeg_result, confidence_breakdown,
        )

        return {
            "explanation": explanation,
            "confidence_score": confidence_breakdown.composite_score,
            "confidence_band": confidence_breakdown.band.value,
        }

    def _build_full_explanation(
        self,
        request: PersonalizationRequest,
        safety: dict,
        selection: dict,
        eeg_result: dict,
        confidence_breakdown,
    ) -> str:
        """Build a complete clinical explanation of the personalisation."""
        sections: list[str] = []

        # Header
        cond_name = self.condition.get("display_name", request.condition_slug)
        sections.append(
            f"Personalized protocol recommendation for {cond_name}."
        )

        # Demographics summary
        demo = request.patient_demographics
        age = demo.get("age", "unknown")
        sex = demo.get("sex", "unknown")
        sections.append(f"Patient: {age}-year-old {sex}.")

        # Safety summary
        if safety["safety_warnings"]:
            warning_count = len(safety["safety_warnings"])
            sections.append(
                f"Safety review identified {warning_count} warning(s). "
                + (
                    f"Blocked modalities: {', '.join(safety['blocked_modalities'])}. "
                    if safety["blocked_modalities"]
                    else "No modalities fully blocked. "
                )
                + (
                    f"Restricted modalities: {', '.join(safety['restricted_modalities'])}."
                    if safety["restricted_modalities"]
                    else "No additional restrictions."
                )
            )
        else:
            sections.append("Safety review: no contraindications identified.")

        # Medication interactions
        if safety["medication_interactions"]:
            n_interactions = len(safety["medication_interactions"])
            major = sum(
                1 for i in safety["medication_interactions"]
                if i.get("severity") in ("contraindicated", "major")
            )
            sections.append(
                f"Medication interactions: {n_interactions} identified "
                f"({major} major/contraindicated)."
            )

        # Phenotype
        pheno = selection.get("matched_phenotype")
        pheno_conf = selection.get("phenotype_confidence", 0.0)
        if pheno:
            sections.append(
                f"Phenotype match: '{pheno}' (confidence {pheno_conf:.0%}). "
                f"Protocol selection targeted to this phenotype."
            )
        else:
            sections.append(
                "No specific phenotype matched. Using condition-level "
                "protocol defaults."
            )

        # Protocol recommendation
        ranked = selection.get("ranked_protocols", [])
        if ranked:
            top = ranked[0]
            sections.append(
                f"Recommended protocol: {top.modality.upper()} targeting "
                f"{top.target} (score {top.score:.3f}, evidence: {top.evidence_level})."
            )
            if len(ranked) > 1:
                alt = ranked[1]
                sections.append(
                    f"Alternative: {alt.modality.upper()} targeting "
                    f"{alt.target} (score {alt.score:.3f})."
                )
        else:
            sections.append(
                "No suitable protocols identified after safety filtering. "
                "Manual protocol design recommended."
            )

        # EEG refinement
        eeg_explanation = eeg_result.get("eeg_explanation", "")
        if eeg_explanation and eeg_explanation != "No EEG data available for refinement.":
            sections.append(f"EEG refinement: {eeg_explanation}")

        # Confidence
        sections.append(
            f"Confidence: {confidence_breakdown.band.value} "
            f"({confidence_breakdown.composite_score:.0%}). "
            f"{confidence_breakdown.review_recommendation}"
        )

        return " ".join(sections)
