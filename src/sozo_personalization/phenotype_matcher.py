"""Phenotype matcher -- maps patient symptoms to condition phenotypes.

Given a ConditionSchema (which carries a list of PhenotypeSubtype objects)
and a patient symptom list, this module computes overlap scores and returns
the best-matching phenotype along with confidence.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class PhenotypeMatch:
    """Result of matching a patient's symptoms against available phenotypes."""

    phenotype_slug: Optional[str]
    phenotype_label: Optional[str]
    confidence: float
    symptom_overlap: float
    matched_features: list[str]
    total_features: int
    all_scores: list[dict]


class PhenotypeMatcher:
    """Score symptom overlap between patient data and condition phenotypes.

    The matcher normalises symptom text to lowercase tokens and computes a
    Jaccard-like overlap against each phenotype's ``key_features``.  A
    minimum overlap threshold (default 0.2) must be met for a match to be
    considered valid.

    Parameters
    ----------
    min_confidence : float
        Minimum overlap ratio to accept a phenotype match (0--1).
    """

    def __init__(self, min_confidence: float = 0.2) -> None:
        self.min_confidence = min_confidence

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #

    def match(
        self,
        phenotypes: list[dict],
        patient_symptoms: list[dict],
        treatment_history: Optional[list[dict]] = None,
    ) -> PhenotypeMatch:
        """Find the best phenotype match for a patient.

        Parameters
        ----------
        phenotypes : list[dict]
            Phenotype definitions from a ConditionSchema, each expected to
            have at minimum ``slug``, ``label``, and ``key_features`` keys.
        patient_symptoms : list[dict]
            Patient symptom dicts.  The matcher looks for ``scale_name``,
            ``abbreviation``, ``severity_band``, and ``subscale_scores``
            fields, and also accepts a plain ``name`` key for simple
            symptom lists.
        treatment_history : list[dict], optional
            Prior treatments; used as a tie-breaker when two phenotypes
            score equally.

        Returns
        -------
        PhenotypeMatch
        """
        if not phenotypes:
            logger.info("No phenotypes defined for condition -- returning empty match.")
            return PhenotypeMatch(
                phenotype_slug=None,
                phenotype_label=None,
                confidence=0.0,
                symptom_overlap=0.0,
                matched_features=[],
                total_features=0,
                all_scores=[],
            )

        patient_tokens = self._extract_patient_tokens(patient_symptoms)
        logger.debug("Patient symptom tokens: %s", patient_tokens)

        all_scores: list[dict] = []
        for pheno in phenotypes:
            slug = pheno.get("slug", "unknown")
            label = pheno.get("label", slug)
            key_features: list[str] = pheno.get("key_features", [])

            if not key_features:
                all_scores.append({
                    "slug": slug,
                    "label": label,
                    "overlap": 0.0,
                    "matched": [],
                    "total_features": 0,
                })
                continue

            feature_tokens = {self._normalise(f) for f in key_features}
            matched = []
            for ft in feature_tokens:
                if self._token_matches(ft, patient_tokens):
                    matched.append(ft)

            overlap = len(matched) / len(feature_tokens) if feature_tokens else 0.0

            # Boost score if treatment history aligns with preferred modalities
            history_bonus = 0.0
            if treatment_history and pheno.get("preferred_modalities"):
                preferred = {m.lower() for m in pheno["preferred_modalities"]}
                for tx in treatment_history:
                    mod = tx.get("modality", "").lower()
                    outcome = tx.get("outcome", "").lower()
                    if mod in preferred and outcome in ("responder", "partial_responder"):
                        history_bonus = 0.1
                        break

            final_score = min(1.0, overlap + history_bonus)

            all_scores.append({
                "slug": slug,
                "label": label,
                "overlap": round(overlap, 3),
                "history_bonus": round(history_bonus, 3),
                "final_score": round(final_score, 3),
                "matched": matched,
                "total_features": len(feature_tokens),
            })

        # Sort by final_score descending
        all_scores.sort(key=lambda x: x.get("final_score", 0.0), reverse=True)

        best = all_scores[0] if all_scores else None
        if best and best.get("final_score", 0.0) >= self.min_confidence:
            logger.info(
                "Phenotype matched: %s (confidence=%.3f, overlap=%.3f)",
                best["slug"], best["final_score"], best["overlap"],
            )
            return PhenotypeMatch(
                phenotype_slug=best["slug"],
                phenotype_label=best["label"],
                confidence=best["final_score"],
                symptom_overlap=best["overlap"],
                matched_features=best.get("matched", []),
                total_features=best.get("total_features", 0),
                all_scores=all_scores,
            )

        logger.info(
            "No phenotype exceeded min_confidence=%.2f (best=%.3f).",
            self.min_confidence,
            best.get("final_score", 0.0) if best else 0.0,
        )
        return PhenotypeMatch(
            phenotype_slug=None,
            phenotype_label=None,
            confidence=best.get("final_score", 0.0) if best else 0.0,
            symptom_overlap=best.get("overlap", 0.0) if best else 0.0,
            matched_features=[],
            total_features=best.get("total_features", 0) if best else 0,
            all_scores=all_scores,
        )

    # ------------------------------------------------------------------ #
    # Token extraction                                                    #
    # ------------------------------------------------------------------ #

    def _extract_patient_tokens(self, symptoms: list[dict]) -> set[str]:
        """Build a set of normalised tokens from patient symptom data.

        Handles several common input shapes:
        - ``{"name": "anhedonia"}``
        - ``{"scale_name": "phq9", "severity_band": "moderate", ...}``
        - ``{"abbreviation": "PHQ-9", "subscale_scores": {"anhedonia": 3}}``
        """
        tokens: set[str] = set()
        for sym in symptoms:
            # Plain name
            if "name" in sym:
                tokens.add(self._normalise(sym["name"]))

            # Scale-based symptoms
            if "scale_name" in sym:
                tokens.add(self._normalise(sym["scale_name"]))
            if "abbreviation" in sym:
                tokens.add(self._normalise(sym["abbreviation"]))
            if "severity_band" in sym:
                tokens.add(self._normalise(sym["severity_band"]))

            # Subscale names are often clinically meaningful
            for subscale_key in sym.get("subscale_scores", {}):
                tokens.add(self._normalise(subscale_key))

            # Domains if provided
            for domain in sym.get("domains", []):
                tokens.add(self._normalise(domain))

            # Keywords list if provided
            for kw in sym.get("keywords", []):
                tokens.add(self._normalise(kw))

        return tokens

    @staticmethod
    def _normalise(text: str) -> str:
        """Lowercase, strip, collapse whitespace, replace hyphens with underscores."""
        return text.lower().strip().replace("-", "_").replace("  ", " ")

    @staticmethod
    def _token_matches(feature_token: str, patient_tokens: set[str]) -> bool:
        """Check if a feature token matches any patient token.

        Uses both exact match and substring containment so that e.g.
        feature "anhedonia" matches patient token "loss_of_pleasure" if
        it appears as a substring, and vice versa.
        """
        if feature_token in patient_tokens:
            return True
        # Substring matching in both directions
        for pt in patient_tokens:
            if feature_token in pt or pt in feature_token:
                return True
        return False
