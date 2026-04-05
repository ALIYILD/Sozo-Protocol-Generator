"""Generation layer — applies structured revisions to DocumentSpec objects.

New exports (long-document pipeline):
    BlockGenerator          — generates individual CanonicalBlock objects
    SectionGenerator        — generates CanonicalSection from SectionSpec
    SubsectionGenerator     — generates subsections independently
    SectionRevisionEngine   — repairs sections based on QA feedback
"""

from .block_generator import BlockGenerator
from .section_generator import SectionGenerator
from .subsection_generator import SubsectionGenerator
from .section_revision_engine import SectionRevisionEngine

__all__ = [
    "BlockGenerator",
    "SectionGenerator",
    "SubsectionGenerator",
    "SectionRevisionEngine",
]
