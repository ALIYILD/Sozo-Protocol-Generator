"""
Partners-tier All-In-One Protocol Compendium — data package.

Each condition lives in its own module (depression.py, adhd.py, …).
This __init__ merges them all into a single PARTNERS_CONDITIONS dict
that is API-identical to the original monolithic file.

Usage (unchanged from before):
    from scripts.partners_data import PARTNERS_CONDITIONS
    # or, via the compatibility shim:
    from scripts.partners_all_in_one_data import PARTNERS_CONDITIONS
"""

from ._shared import _plato_programs_default  # noqa: F401  — re-exported for condition modules

PARTNERS_CONDITIONS: dict = {}

# ── Import each condition module and merge its data ─────────────────────────
from .depression import PARTNERS_CONDITIONS as _pc_depression
from .adhd import PARTNERS_CONDITIONS as _pc_adhd
from .alzheimers import PARTNERS_CONDITIONS as _pc_alzheimers
from .anxiety import PARTNERS_CONDITIONS as _pc_anxiety
from .stroke_rehab import PARTNERS_CONDITIONS as _pc_stroke_rehab
from .tbi import PARTNERS_CONDITIONS as _pc_tbi
from .chronic_pain import PARTNERS_CONDITIONS as _pc_chronic_pain
from .ptsd import PARTNERS_CONDITIONS as _pc_ptsd
from .ocd import PARTNERS_CONDITIONS as _pc_ocd
from .ms import PARTNERS_CONDITIONS as _pc_ms
from .asd import PARTNERS_CONDITIONS as _pc_asd
from .long_covid import PARTNERS_CONDITIONS as _pc_long_covid
from .tinnitus import PARTNERS_CONDITIONS as _pc_tinnitus
from .insomnia import PARTNERS_CONDITIONS as _pc_insomnia
from .parkinsons import PARTNERS_CONDITIONS as _pc_parkinsons

PARTNERS_CONDITIONS.update(_pc_depression)
PARTNERS_CONDITIONS.update(_pc_adhd)
PARTNERS_CONDITIONS.update(_pc_alzheimers)
PARTNERS_CONDITIONS.update(_pc_anxiety)
PARTNERS_CONDITIONS.update(_pc_stroke_rehab)
PARTNERS_CONDITIONS.update(_pc_tbi)
PARTNERS_CONDITIONS.update(_pc_chronic_pain)
PARTNERS_CONDITIONS.update(_pc_ptsd)
PARTNERS_CONDITIONS.update(_pc_ocd)
PARTNERS_CONDITIONS.update(_pc_ms)
PARTNERS_CONDITIONS.update(_pc_asd)
PARTNERS_CONDITIONS.update(_pc_long_covid)
PARTNERS_CONDITIONS.update(_pc_tinnitus)
PARTNERS_CONDITIONS.update(_pc_insomnia)
PARTNERS_CONDITIONS.update(_pc_parkinsons)

# ── Run normalizers (mutate PARTNERS_CONDITIONS in-place) ───────────────────
from . import _normalizers as _norm  # noqa: F401

# The normalizer functions reference the module-level PARTNERS_CONDITIONS name;
# we re-bind it in the normalizers module so they see our merged dict.
import sys as _sys
_norm_mod = _sys.modules[__name__ + "._normalizers"] if (__name__ + "._normalizers") in _sys.modules else _norm
if hasattr(_norm, "_normalize_list_protocols"):
    import importlib as _il
    _norm_globals = vars(_norm)
    _norm_globals["PARTNERS_CONDITIONS"] = PARTNERS_CONDITIONS
    _norm._normalize_list_protocols()
    if hasattr(_norm, "_normalize_phenotypes"):
        _norm._normalize_phenotypes()
    if hasattr(_norm, "_normalize_phenotype_tables"):
        _norm._normalize_phenotype_tables()
