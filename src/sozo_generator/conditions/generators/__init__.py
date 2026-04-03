"""Condition-specific schema generators."""
from .parkinsons import build_parkinsons_condition
from .depression import build_depression_condition
from .anxiety import build_anxiety_condition
from .adhd import build_adhd_condition
from .alzheimers import build_alzheimers_condition
from .stroke_rehab import build_stroke_rehab_condition
from .tbi import build_tbi_condition
from .chronic_pain import build_chronic_pain_condition
from .ptsd import build_ptsd_condition
from .ocd import build_ocd_condition
from .ms import build_ms_condition
from .asd import build_asd_condition
from .long_covid import build_long_covid_condition
from .tinnitus import build_tinnitus_condition
from .insomnia import build_insomnia_condition
from .home_tdcs_mdd_anxiety import build_home_tdcs_mdd_anxiety_condition
from .neuroonica_combo import build_neuroonica_combo_condition
from .tvns import build_tvns_condition
from .ces_alphastem import build_ces_alphastem_condition
from .trd_vns import build_trd_vns_condition

__all__ = [
    "build_parkinsons_condition",
    "build_depression_condition",
    "build_anxiety_condition",
    "build_adhd_condition",
    "build_alzheimers_condition",
    "build_stroke_rehab_condition",
    "build_tbi_condition",
    "build_chronic_pain_condition",
    "build_ptsd_condition",
    "build_ocd_condition",
    "build_ms_condition",
    "build_asd_condition",
    "build_long_covid_condition",
    "build_tinnitus_condition",
    "build_insomnia_condition",
    "build_home_tdcs_mdd_anxiety_condition",
    "build_neuroonica_combo_condition",
    "build_tvns_condition",
    "build_ces_alphastem_condition",
    "build_trd_vns_condition",
]

CONDITION_BUILDERS = {
    "parkinsons": build_parkinsons_condition,
    "depression": build_depression_condition,
    "anxiety": build_anxiety_condition,
    "adhd": build_adhd_condition,
    "alzheimers": build_alzheimers_condition,
    "stroke_rehab": build_stroke_rehab_condition,
    "tbi": build_tbi_condition,
    "chronic_pain": build_chronic_pain_condition,
    "ptsd": build_ptsd_condition,
    "ocd": build_ocd_condition,
    "ms": build_ms_condition,
    "asd": build_asd_condition,
    "long_covid": build_long_covid_condition,
    "tinnitus": build_tinnitus_condition,
    "insomnia": build_insomnia_condition,
    "home_tdcs_mdd_anxiety": build_home_tdcs_mdd_anxiety_condition,
    "neuroonica_combo": build_neuroonica_combo_condition,
    "tvns": build_tvns_condition,
    "ces_alphastem": build_ces_alphastem_condition,
    "trd_vns": build_trd_vns_condition,
}
