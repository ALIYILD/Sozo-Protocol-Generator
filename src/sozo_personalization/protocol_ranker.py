"""Protocol ranker -- score and sort candidate protocols.

Weights:
  - Evidence quality   40%
  - Phenotype match    30%
  - Prior response     20%
  - Feasibility        10%

Each component is normalised to 0--1 before applying the weight.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from .models import ProtocolCandidate

logger = logging.getLogger(__name__)

# Evidence level string -> numeric score (aligned with EvidenceLevel enum).
EVIDENCE_SCORES: dict[str, float] = {
    "highest": 1.0,
    "high": 0.85,
    "medium": 0.65,
    "low": 0.40,
    "very_low": 0.20,
    "missing": 0.05,
}


@dataclass
class RankerWeights:
    """Configurable weights for the four ranking dimensions."""

    evidence: float = 0.40
    phenotype_match: float = 0.30
    prior_response: float = 0.20
    feasibility: float = 0.10

    def __post_init__(self) -> None:
        total = self.evidence + self.phenotype_match + self.prior_response + self.feasibility
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Ranker weights must sum to 1.0, got {total:.4f}")


class ProtocolRanker:
    """Rank protocol candidates using a weighted multi-criteria score.

    Parameters
    ----------
    weights : RankerWeights, optional
        Custom weights; defaults to 40/30/20/10 split.
    """

    def __init__(self, weights: Optional[RankerWeights] = None) -> None:
        self.weights = weights or RankerWeights()

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #

    def rank(
        self,
        protocols: list[dict],
        matched_phenotype_slug: Optional[str],
        phenotype_confidence: float,
        treatment_history: list[dict],
        blocked_modalities: list[str],
        restricted_modalities: list[str],
        target_modalities: Optional[list[str]] = None,
    ) -> list[ProtocolCandidate]:
        """Score and sort candidate protocols, filtering blocked modalities.

        Parameters
        ----------
        protocols : list[dict]
            Raw protocol entries from a ConditionSchema. Expected keys:
            ``protocol_id``, ``modality``, ``target_region``,
            ``target_abbreviation``, ``parameters``, ``evidence_level``,
            ``phenotype_slugs``, ``rationale``, ``session_count``, ``notes``.
        matched_phenotype_slug : str | None
            Phenotype matched by the PhenotypeMatcher, or None.
        phenotype_confidence : float
            Confidence of the phenotype match (0--1).
        treatment_history : list[dict]
            Patient treatment records.
        blocked_modalities : list[str]
            Modalities that must be excluded (safety layer).
        restricted_modalities : list[str]
            Modalities requiring extra caution (penalised but not excluded).
        target_modalities : list[str] | None
            If supplied, only protocols matching these modalities are
            considered.

        Returns
        -------
        list[ProtocolCandidate]
            Scored and sorted (highest first) list of candidates.
        """
        blocked_lower = {m.lower() for m in blocked_modalities}
        restricted_lower = {m.lower() for m in restricted_modalities}
        target_lower = {m.lower() for m in target_modalities} if target_modalities else None

        candidates: list[ProtocolCandidate] = []

        for proto in protocols:
            modality = proto.get("modality", "").lower()

            # Hard filter: blocked modalities
            if modality in blocked_lower:
                logger.debug(
                    "Protocol %s excluded -- modality %s is blocked.",
                    proto.get("protocol_id", "?"), modality,
                )
                continue

            # Filter by requested modalities if specified
            if target_lower and modality not in target_lower:
                continue

            # --- Evidence score ---
            ev_level = proto.get("evidence_level", "missing")
            if isinstance(ev_level, str):
                ev_score = EVIDENCE_SCORES.get(ev_level.lower(), 0.05)
            else:
                # Enum value
                ev_score = EVIDENCE_SCORES.get(str(ev_level).lower(), 0.05)

            # --- Phenotype match score ---
            pheno_score = self._compute_phenotype_score(
                proto, matched_phenotype_slug, phenotype_confidence,
            )

            # --- Prior response score ---
            prior_score = self._compute_prior_response_score(proto, treatment_history)

            # --- Feasibility score ---
            feasibility = self._compute_feasibility_score(proto, restricted_lower)

            # Weighted composite
            composite = (
                self.weights.evidence * ev_score
                + self.weights.phenotype_match * pheno_score
                + self.weights.prior_response * prior_score
                + self.weights.feasibility * feasibility
            )
            composite = round(composite, 4)

            # Build rationale string
            rationale = self._build_rationale(
                proto, ev_score, pheno_score, prior_score, feasibility,
                matched_phenotype_slug,
            )

            # Build montage dict
            montage = {
                "target_region": proto.get("target_region", ""),
                "target_abbreviation": proto.get("target_abbreviation", ""),
            }

            # Build schedule dict
            session_count = proto.get("session_count")
            schedule = {"session_count": session_count} if session_count else {}

            candidate = ProtocolCandidate(
                modality=proto.get("modality", "unknown"),
                target=proto.get("target_abbreviation", proto.get("target_region", "")),
                montage=montage,
                parameters=proto.get("parameters", {}),
                schedule=schedule,
                phenotype_slug=matched_phenotype_slug,
                evidence_level=ev_level if isinstance(ev_level, str) else ev_level.value,
                score=composite,
                rationale=rationale,
            )
            candidates.append(candidate)

        # Sort descending by score
        candidates.sort(key=lambda c: c.score, reverse=True)

        logger.info(
            "Ranked %d protocol candidates (from %d raw, %d blocked).",
            len(candidates), len(protocols), len(protocols) - len(candidates),
        )
        return candidates

    # ------------------------------------------------------------------ #
    # Scoring helpers                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _compute_phenotype_score(
        proto: dict,
        matched_phenotype_slug: Optional[str],
        phenotype_confidence: float,
    ) -> float:
        """Score how well a protocol aligns with the matched phenotype.

        Returns 1.0 * confidence if the protocol explicitly lists the matched
        phenotype.  Returns 0.5 * confidence for protocols with no phenotype
        restriction (general protocols).  Returns 0.1 for mismatched protocols.
        """
        phenotype_slugs: list[str] = proto.get("phenotype_slugs", [])

        if not matched_phenotype_slug:
            # No phenotype matched -- all protocols scored equally at baseline
            return 0.3

        if not phenotype_slugs:
            # General protocol, applies to all phenotypes
            return 0.5 * phenotype_confidence

        if matched_phenotype_slug in phenotype_slugs:
            return 1.0 * phenotype_confidence

        # Phenotype mismatch
        return 0.1

    @staticmethod
    def _compute_prior_response_score(proto: dict, treatment_history: list[dict]) -> float:
        """Score based on prior patient response to similar protocols.

        - 1.0: patient responded to same modality + target
        - 0.7: patient responded to same modality, different target
        - 0.5: no prior history (neutral)
        - 0.2: patient was a non-responder to same modality + target
        - 0.0: patient had adverse events with this modality
        """
        if not treatment_history:
            return 0.5  # No history, neutral

        proto_modality = proto.get("modality", "").lower()
        proto_target = proto.get("target_abbreviation", "").lower()

        best_score = 0.5  # default neutral

        for tx in treatment_history:
            tx_modality = tx.get("modality", "").lower()
            tx_target = tx.get("target", "").lower()
            outcome = tx.get("outcome", "not_assessed").lower()
            adverse = tx.get("adverse_events", [])

            if tx_modality != proto_modality:
                continue

            # Same modality -- check outcome
            same_target = tx_target == proto_target

            if adverse and any(
                sev in str(ae).lower()
                for ae in adverse
                for sev in ("seizure", "severe", "hospitali")
            ):
                # Serious adverse event with this modality
                return 0.0

            if outcome == "responder":
                best_score = max(best_score, 1.0 if same_target else 0.7)
            elif outcome == "partial_responder":
                best_score = max(best_score, 0.8 if same_target else 0.6)
            elif outcome == "non_responder":
                best_score = min(best_score, 0.2 if same_target else 0.35)

        return best_score

    @staticmethod
    def _compute_feasibility_score(proto: dict, restricted_lower: set[str]) -> float:
        """Score protocol feasibility.

        Considers whether the modality is restricted (penalised) and the
        session count (fewer sessions = higher feasibility for the patient).
        """
        modality = proto.get("modality", "").lower()
        base = 1.0

        # Penalty for restricted modalities
        if modality in restricted_lower:
            base -= 0.3

        # Session burden penalty (diminishing)
        session_count = proto.get("session_count")
        if session_count and session_count > 20:
            base -= min(0.2, (session_count - 20) * 0.01)

        return max(0.0, base)

    @staticmethod
    def _build_rationale(
        proto: dict,
        ev_score: float,
        pheno_score: float,
        prior_score: float,
        feasibility: float,
        matched_phenotype: Optional[str],
    ) -> str:
        """Construct a human-readable rationale string for a protocol candidate."""
        parts: list[str] = []

        # Protocol identity
        proto_id = proto.get("protocol_id", proto.get("label", "Protocol"))
        parts.append(f"{proto_id}: {proto.get('rationale', 'No rationale provided.')}")

        # Evidence
        ev_label = proto.get("evidence_level", "unknown")
        parts.append(f"Evidence: {ev_label} (score {ev_score:.2f}).")

        # Phenotype
        if matched_phenotype:
            phenotype_slugs = proto.get("phenotype_slugs", [])
            if matched_phenotype in phenotype_slugs:
                parts.append(f"Phenotype-specific for '{matched_phenotype}' (score {pheno_score:.2f}).")
            else:
                parts.append(f"General protocol; phenotype '{matched_phenotype}' (score {pheno_score:.2f}).")
        else:
            parts.append("No phenotype matched; scored as general protocol.")

        # Prior response
        if prior_score >= 0.7:
            parts.append("Prior treatment response supports this choice.")
        elif prior_score <= 0.2:
            parts.append("Caution: prior non-response or adverse event with similar protocol.")

        # Feasibility
        if feasibility < 0.7:
            parts.append("Feasibility reduced due to restrictions or high session burden.")

        return " ".join(parts)
