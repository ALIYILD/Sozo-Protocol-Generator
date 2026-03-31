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
}
