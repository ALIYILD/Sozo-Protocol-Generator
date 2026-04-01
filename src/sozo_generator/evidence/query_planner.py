"""
Evidence query planner — builds structured PubMed query plans per condition.

Given a condition's metadata (name, ICD-10, networks, modalities, symptoms),
generates a QueryPlan covering all 13 ClaimCategory values with appropriate
PubMed-style query strings.
"""
from __future__ import annotations

import logging
from typing import Optional

from pydantic import BaseModel, Field

from ..core.enums import ClaimCategory, Modality, NetworkKey

logger = logging.getLogger(__name__)

# ── Modality display names for query strings ─────────────────────────

_MODALITY_NAMES: dict[Modality, str] = {
    Modality.TDCS: "transcranial direct current stimulation",
    Modality.TPS: "transcranial pulse stimulation",
    Modality.TAVNS: "transcutaneous auricular vagus nerve stimulation",
    Modality.CES: "cranial electrotherapy stimulation",
    Modality.MULTIMODAL: "multimodal neuromodulation",
}

_MODALITY_ABBREVS: dict[Modality, str] = {
    Modality.TDCS: "tDCS",
    Modality.TPS: "TPS",
    Modality.TAVNS: "taVNS",
    Modality.CES: "CES",
    Modality.MULTIMODAL: "neuromodulation",
}

_NETWORK_NAMES: dict[NetworkKey, str] = {
    NetworkKey.DMN: "default mode network",
    NetworkKey.CEN: "central executive network",
    NetworkKey.SN: "salience network",
    NetworkKey.SMN: "sensorimotor network",
    NetworkKey.LIMBIC: "limbic system",
    NetworkKey.ATTENTION: "attention network",
}

# ── Publication type filters ─────────────────────────────────────────

PUB_TYPE_REVIEWS = ["Review", "Systematic Review", "Meta-Analysis"]
PUB_TYPE_TRIALS = ["Randomized Controlled Trial", "Clinical Trial"]
PUB_TYPE_GUIDELINES = ["Practice Guideline", "Guideline"]
PUB_TYPE_ALL = []  # empty means no filter


# ── Models ───────────────────────────────────────────────────────────


class QuerySpec(BaseModel):
    """A single PubMed query with search parameters."""

    query_string: str
    category: ClaimCategory
    max_results: int = 30
    years_back: int = 10
    publication_types: list[str] = Field(default_factory=list)


class QueryPlan(BaseModel):
    """Complete query plan for one condition."""

    condition_slug: str
    queries: list[QuerySpec] = Field(default_factory=list)

    @property
    def total_max_results(self) -> int:
        return sum(q.max_results for q in self.queries)

    @property
    def category_coverage(self) -> set[ClaimCategory]:
        return {q.category for q in self.queries}


# ── Planner ──────────────────────────────────────────────────────────


class QueryPlanner:
    """Builds evidence query plans for conditions."""

    def plan_condition(
        self,
        condition_slug: str,
        display_name: str,
        icd10: str = "",
        networks: list[NetworkKey] | None = None,
        modalities: list[Modality] | None = None,
        symptoms: list[str] | None = None,
    ) -> QueryPlan:
        """Generate a comprehensive QueryPlan covering all ClaimCategory values."""
        networks = networks or []
        modalities = modalities or [Modality.TDCS]
        symptoms = symptoms or []

        queries: list[QuerySpec] = []

        queries.extend(self._build_pathophysiology_queries(display_name, icd10, symptoms))
        queries.extend(self._build_brain_region_queries(display_name, networks))
        queries.extend(self._build_network_queries(display_name, networks))
        queries.extend(self._build_phenotype_queries(display_name, symptoms))
        queries.extend(self._build_assessment_queries(display_name))
        queries.extend(self._build_stimulation_queries(display_name, modalities, networks))
        queries.extend(self._build_safety_queries(display_name, modalities))
        queries.extend(self._build_responder_queries(display_name, modalities))
        queries.extend(self._build_criteria_queries(display_name, modalities))

        plan = QueryPlan(condition_slug=condition_slug, queries=queries)
        logger.info(
            "QueryPlan for %s: %d queries across %d categories, max %d results",
            condition_slug,
            len(plan.queries),
            len(plan.category_coverage),
            plan.total_max_results,
        )
        return plan

    # ── Private builders ─────────────────────────────────────────────

    def _build_pathophysiology_queries(
        self,
        display_name: str,
        icd10: str,
        symptoms: list[str],
    ) -> list[QuerySpec]:
        """Pathophysiology and clinical presentation queries."""
        queries: list[QuerySpec] = []
        base = f'("{display_name}"[Title/Abstract])'
        icd_part = f' OR ("{icd10}"[Title/Abstract])' if icd10 else ""

        queries.append(QuerySpec(
            query_string=f'{base}{icd_part} AND (pathophysiology OR neurobiology OR etiology)',
            category=ClaimCategory.PATHOPHYSIOLOGY,
            max_results=30,
            years_back=10,
            publication_types=PUB_TYPE_REVIEWS,
        ))

        if symptoms:
            symptom_or = " OR ".join(f'"{s}"' for s in symptoms[:5])
            queries.append(QuerySpec(
                query_string=f'{base} AND ({symptom_or}) AND (mechanism OR pathophysiology)',
                category=ClaimCategory.PATHOPHYSIOLOGY,
                max_results=20,
                years_back=10,
                publication_types=PUB_TYPE_ALL,
            ))

        return queries

    def _build_brain_region_queries(
        self,
        display_name: str,
        networks: list[NetworkKey],
    ) -> list[QuerySpec]:
        """Brain region involvement queries."""
        queries: list[QuerySpec] = []
        base = f'("{display_name}"[Title/Abstract])'

        queries.append(QuerySpec(
            query_string=(
                f'{base} AND (brain region OR cortical OR subcortical OR neuroimaging '
                f'OR fMRI OR structural MRI)'
            ),
            category=ClaimCategory.BRAIN_REGIONS,
            max_results=25,
            years_back=10,
            publication_types=PUB_TYPE_REVIEWS,
        ))

        for nk in networks[:3]:
            net_name = _NETWORK_NAMES.get(nk, nk.value)
            queries.append(QuerySpec(
                query_string=f'{base} AND ("{net_name}" OR "{nk.value}") AND (brain region OR cortex)',
                category=ClaimCategory.BRAIN_REGIONS,
                max_results=15,
                years_back=8,
                publication_types=PUB_TYPE_ALL,
            ))

        return queries

    def _build_network_queries(
        self,
        display_name: str,
        networks: list[NetworkKey],
    ) -> list[QuerySpec]:
        """Network connectivity and dysfunction queries."""
        queries: list[QuerySpec] = []
        base = f'("{display_name}"[Title/Abstract])'

        queries.append(QuerySpec(
            query_string=(
                f'{base} AND (functional connectivity OR resting state OR network dysfunction '
                f'OR connectome)'
            ),
            category=ClaimCategory.NETWORK_INVOLVEMENT,
            max_results=25,
            years_back=8,
            publication_types=PUB_TYPE_ALL,
        ))

        for nk in networks[:4]:
            net_name = _NETWORK_NAMES.get(nk, nk.value)
            queries.append(QuerySpec(
                query_string=f'{base} AND ("{net_name}") AND (connectivity OR dysfunction)',
                category=ClaimCategory.NETWORK_INVOLVEMENT,
                max_results=15,
                years_back=8,
                publication_types=PUB_TYPE_ALL,
            ))

        return queries

    def _build_phenotype_queries(
        self,
        display_name: str,
        symptoms: list[str],
    ) -> list[QuerySpec]:
        """Clinical phenotype and subtype queries."""
        queries: list[QuerySpec] = []
        base = f'("{display_name}"[Title/Abstract])'

        queries.append(QuerySpec(
            query_string=f'{base} AND (phenotype OR subtype OR clinical presentation OR classification)',
            category=ClaimCategory.CLINICAL_PHENOTYPES,
            max_results=20,
            years_back=10,
            publication_types=PUB_TYPE_REVIEWS,
        ))

        if symptoms:
            symptom_or = " OR ".join(f'"{s}"' for s in symptoms[:5])
            queries.append(QuerySpec(
                query_string=f'{base} AND ({symptom_or}) AND (phenotype OR subgroup)',
                category=ClaimCategory.CLINICAL_PHENOTYPES,
                max_results=15,
                years_back=10,
                publication_types=PUB_TYPE_ALL,
            ))

        return queries

    def _build_assessment_queries(
        self,
        display_name: str,
    ) -> list[QuerySpec]:
        """Assessment tools and outcome measures queries."""
        base = f'("{display_name}"[Title/Abstract])'
        return [
            QuerySpec(
                query_string=(
                    f'{base} AND (outcome measure OR assessment tool OR validated scale '
                    f'OR questionnaire OR psychometric)'
                ),
                category=ClaimCategory.ASSESSMENT_TOOLS,
                max_results=20,
                years_back=10,
                publication_types=PUB_TYPE_REVIEWS,
            ),
        ]

    def _build_stimulation_queries(
        self,
        display_name: str,
        modalities: list[Modality],
        networks: list[NetworkKey],
    ) -> list[QuerySpec]:
        """Stimulation targets, parameters, and modality rationale queries."""
        queries: list[QuerySpec] = []
        base = f'("{display_name}"[Title/Abstract])'

        for mod in modalities:
            mod_name = _MODALITY_NAMES.get(mod, mod.value)
            mod_abbrev = _MODALITY_ABBREVS.get(mod, mod.value)

            # Stimulation targets
            queries.append(QuerySpec(
                query_string=(
                    f'{base} AND ("{mod_name}" OR "{mod_abbrev}") AND '
                    f'(target OR montage OR electrode placement OR stimulation site)'
                ),
                category=ClaimCategory.STIMULATION_TARGETS,
                max_results=25,
                years_back=10,
                publication_types=PUB_TYPE_ALL,
            ))

            # Stimulation parameters
            queries.append(QuerySpec(
                query_string=(
                    f'{base} AND ("{mod_name}" OR "{mod_abbrev}") AND '
                    f'(dosage OR intensity OR duration OR frequency OR protocol OR parameters)'
                ),
                category=ClaimCategory.STIMULATION_PARAMETERS,
                max_results=25,
                years_back=10,
                publication_types=PUB_TYPE_TRIALS,
            ))

            # Modality rationale
            queries.append(QuerySpec(
                query_string=(
                    f'{base} AND ("{mod_name}" OR "{mod_abbrev}") AND '
                    f'(efficacy OR effectiveness OR rationale OR mechanism of action)'
                ),
                category=ClaimCategory.MODALITY_RATIONALE,
                max_results=25,
                years_back=10,
                publication_types=PUB_TYPE_REVIEWS,
            ))

        # Network-targeted stimulation
        for nk in networks[:3]:
            net_name = _NETWORK_NAMES.get(nk, nk.value)
            mod_terms = " OR ".join(
                f'"{_MODALITY_ABBREVS.get(m, m.value)}"' for m in modalities
            )
            queries.append(QuerySpec(
                query_string=(
                    f'{base} AND ({mod_terms}) AND ("{net_name}") AND '
                    f'(stimulation target OR neuromodulation)'
                ),
                category=ClaimCategory.STIMULATION_TARGETS,
                max_results=15,
                years_back=8,
                publication_types=PUB_TYPE_ALL,
            ))

        return queries

    def _build_safety_queries(
        self,
        display_name: str,
        modalities: list[Modality],
    ) -> list[QuerySpec]:
        """Safety and contraindication queries."""
        queries: list[QuerySpec] = []
        base = f'("{display_name}"[Title/Abstract])'

        for mod in modalities:
            mod_name = _MODALITY_NAMES.get(mod, mod.value)
            mod_abbrev = _MODALITY_ABBREVS.get(mod, mod.value)

            queries.append(QuerySpec(
                query_string=(
                    f'{base} AND ("{mod_name}" OR "{mod_abbrev}") AND '
                    f'(safety OR adverse effects OR side effects OR tolerability)'
                ),
                category=ClaimCategory.SAFETY,
                max_results=20,
                years_back=10,
                publication_types=PUB_TYPE_ALL,
            ))

            queries.append(QuerySpec(
                query_string=(
                    f'{base} AND ("{mod_name}" OR "{mod_abbrev}") AND '
                    f'(contraindication OR precaution OR exclusion criteria OR risk)'
                ),
                category=ClaimCategory.CONTRAINDICATIONS,
                max_results=15,
                years_back=10,
                publication_types=PUB_TYPE_GUIDELINES,
            ))

        # General neuromodulation safety
        queries.append(QuerySpec(
            query_string=(
                f'(neuromodulation OR brain stimulation) AND '
                f'(safety guidelines OR contraindications) AND (consensus OR guideline)'
            ),
            category=ClaimCategory.CONTRAINDICATIONS,
            max_results=15,
            years_back=10,
            publication_types=PUB_TYPE_GUIDELINES,
        ))

        return queries

    def _build_responder_queries(
        self,
        display_name: str,
        modalities: list[Modality],
    ) -> list[QuerySpec]:
        """Responder criteria queries."""
        queries: list[QuerySpec] = []
        base = f'("{display_name}"[Title/Abstract])'

        mod_terms = " OR ".join(
            f'"{_MODALITY_ABBREVS.get(m, m.value)}"' for m in modalities
        )

        queries.append(QuerySpec(
            query_string=(
                f'{base} AND ({mod_terms}) AND '
                f'(responder OR predictor OR biomarker OR treatment response)'
            ),
            category=ClaimCategory.RESPONDER_CRITERIA,
            max_results=20,
            years_back=10,
            publication_types=PUB_TYPE_ALL,
        ))

        return queries

    def _build_criteria_queries(
        self,
        display_name: str,
        modalities: list[Modality],
    ) -> list[QuerySpec]:
        """Inclusion and exclusion criteria queries."""
        queries: list[QuerySpec] = []
        base = f'("{display_name}"[Title/Abstract])'

        mod_terms = " OR ".join(
            f'"{_MODALITY_ABBREVS.get(m, m.value)}"' for m in modalities
        )

        queries.append(QuerySpec(
            query_string=(
                f'{base} AND ({mod_terms}) AND '
                f'(inclusion criteria OR eligibility OR patient selection)'
            ),
            category=ClaimCategory.INCLUSION_CRITERIA,
            max_results=15,
            years_back=10,
            publication_types=PUB_TYPE_TRIALS,
        ))

        queries.append(QuerySpec(
            query_string=(
                f'{base} AND ({mod_terms}) AND '
                f'(exclusion criteria OR contraindication OR ineligible)'
            ),
            category=ClaimCategory.EXCLUSION_CRITERIA,
            max_results=15,
            years_back=10,
            publication_types=PUB_TYPE_TRIALS,
        ))

        return queries
