"""Sozo Personalization Engine -- 4-layer patient protocol adaptation.

Exports the main engine class and result dataclass for downstream consumers.
"""

from .engine import PersonalizationEngine, PersonalizationResult

__all__ = ["PersonalizationEngine", "PersonalizationResult"]
