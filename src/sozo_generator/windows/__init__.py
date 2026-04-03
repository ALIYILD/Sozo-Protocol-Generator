"""
Sozo Windows — Specialist evidence-to-blueprint subagent modules.

Each Window maps to a clinical protocol space and contains 10 specialist
subagents. Subagents output structured JSON blocks conforming to the
DocumentSpec / SectionContent schema, with every claim tagged by DOI/PMID.
"""

from .window_6_atbs_trd import Window6ATBSTRDOrchestrator

__all__ = ["Window6ATBSTRDOrchestrator"]
