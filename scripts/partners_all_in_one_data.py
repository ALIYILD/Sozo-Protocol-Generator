"""
Partners-tier All-In-One Protocol Compendium data for all 15 conditions.

This file is now a compatibility shim. All condition data lives in the
per-condition modules under scripts/partners_data/:

    partners_data/depression.py
    partners_data/adhd.py
    partners_data/alzheimers.py
    partners_data/anxiety.py
    partners_data/stroke_rehab.py
    partners_data/tbi.py
    partners_data/chronic_pain.py
    partners_data/ptsd.py
    partners_data/ocd.py
    partners_data/ms.py
    partners_data/asd.py
    partners_data/long_covid.py
    partners_data/tinnitus.py
    partners_data/insomnia.py
    partners_data/parkinsons.py

Importing PARTNERS_CONDITIONS from this file works exactly as before —
the dict is built and normalised by partners_data/__init__.py.
"""

from partners_data import PARTNERS_CONDITIONS  # noqa: F401
from partners_data._shared import _plato_programs_default  # noqa: F401

__all__ = ["PARTNERS_CONDITIONS", "_plato_programs_default"]
