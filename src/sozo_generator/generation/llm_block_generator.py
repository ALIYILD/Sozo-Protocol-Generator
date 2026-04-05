"""LLM-powered block generator for the SOZO long-document production pipeline.

Wraps BlockGenerator with optional Claude API generation per text block.
Falls back gracefully to structured-data generation when the LLM is unavailable
or when a call fails.

SAFETY: Medical/clinical content is always grounded in ConditionSchema data.
The LLM expands/enriches — it never fabricates conditions, protocols, or PMIDs.
All real data (protocols, contraindications, PMIDs, etc.) is injected from the
verified ConditionSchema before the LLM prompt is sent.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Optional

from ..schemas.canonical import CanonicalBlock, ContentBlockSpec
from ..schemas.condition import ConditionSchema
from .block_generator import BlockGenerator

logger = logging.getLogger(__name__)

# Block types that can benefit from LLM generation (all text-like types)
_LLM_ELIGIBLE_TYPES = {"text", "callout"}

# Block types that always use the structured fallback (asset types)
_ASSET_TYPES = {"table", "figure", "chart", "image"}


class LLMBlockGenerator:
    """
    BlockGenerator that uses Claude API for text blocks when an API key is available.
    Falls back to structured-data generation (BlockGenerator) when LLM is unavailable.

    SAFETY: Medical/clinical content always grounded in ConditionSchema data.
    The LLM expands/enriches — it never fabricates conditions, protocols, or PMIDs.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-haiku-4-5-20251001",  # fast + cheap for block generation
        fallback_generator: Optional[BlockGenerator] = None,
        max_tokens_per_block: int = 800,
        use_llm: bool = True,
    ) -> None:
        self.fallback = fallback_generator or BlockGenerator()
        self.model = model
        self.max_tokens = max_tokens_per_block
        self.use_llm = use_llm
        self._client = None

        # Get API key from param, env var, or settings
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not self._api_key:
            try:
                from sozo_generator.core.settings import get_settings
                self._api_key = getattr(get_settings(), "anthropic_api_key", "")
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def llm_available(self) -> bool:
        """True if API key is set and anthropic package is importable."""
        if not self._api_key or not self.use_llm:
            return False
        try:
            import anthropic  # noqa: F401
            return True
        except ImportError:
            return False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        spec: ContentBlockSpec,
        condition: ConditionSchema,
        variant: str,
        asset_registry: Optional[Any] = None,
    ) -> CanonicalBlock:
        """
        Generate a CanonicalBlock.

        For text/callout blocks, use LLM if available.
        For asset blocks (table/figure/chart/image) and structural blocks
        (heading/divider/list), always use the fallback BlockGenerator.
        """
        bt = spec.block_type

        # Asset and structural blocks always use the deterministic fallback
        if bt not in _LLM_ELIGIBLE_TYPES or not self.llm_available:
            return self.fallback.generate(
                spec=spec,
                condition=condition,
                variant=variant,
                asset_registry=asset_registry,
            )

        return self._generate_with_llm(spec, condition, variant)

    def batch_generate_sections(
        self,
        specs: list[ContentBlockSpec],
        condition: ConditionSchema,
        variant: str,
    ) -> list[CanonicalBlock]:
        """
        Generate multiple blocks. LLM blocks run sequentially to avoid rate limits.
        Non-text blocks use fallback immediately.
        """
        blocks: list[CanonicalBlock] = []
        for spec in specs:
            block = self.generate(spec=spec, condition=condition, variant=variant)
            blocks.append(block)
        return blocks

    # ------------------------------------------------------------------
    # LLM generation
    # ------------------------------------------------------------------

    def _generate_with_llm(
        self,
        spec: ContentBlockSpec,
        condition: ConditionSchema,
        variant: str,
    ) -> CanonicalBlock:
        """
        Call Claude API to generate block content.

        On any exception, falls back to self.fallback.generate().
        """
        try:
            client = self._get_client()
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(spec, condition, variant)

            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            # Extract text from the response
            content_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content_text += block.text

            content_text = content_text.strip()
            if not content_text:
                logger.warning(
                    "LLMBlockGenerator: empty response for block '%s', falling back.",
                    spec.block_id,
                )
                return self.fallback.generate(spec=spec, condition=condition, variant=variant)

            logger.debug(
                "LLMBlockGenerator: generated block '%s' via LLM (%d chars).",
                spec.block_id,
                len(content_text),
            )

            return CanonicalBlock(
                block_id=spec.block_id,
                block_type=spec.block_type,
                heading=spec.heading,
                heading_level=spec.heading_level,
                content=content_text,
                placeholder_resolved=True,
                metadata=dict(spec.metadata),
                generation_metadata={
                    "content_hint": spec.content_hint,
                    "variant": variant,
                    "target_word_count": spec.target_word_count,
                    "llm_generated": True,
                    "model": self.model,
                },
            )

        except Exception as exc:
            logger.warning(
                "LLMBlockGenerator: LLM call failed for block '%s' (%s), falling back.",
                spec.block_id,
                exc,
            )
            return self.fallback.generate(spec=spec, condition=condition, variant=variant)

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    def _build_system_prompt(self) -> str:
        """Clinical writing system prompt."""
        return (
            "You are a clinical content writer for SOZO Brain Center, a specialist "
            "neuromodulation clinic. Write precise, evidence-grounded content. "
            "Use only the clinical data provided — never fabricate PMIDs, protocol "
            "parameters, contraindications, or clinical claims. "
            "Be concise, professional, and accurate. "
            "Write in clear prose paragraphs. Do not add headings or bullet points "
            "unless explicitly instructed."
        )

    def _build_user_prompt(
        self,
        spec: ContentBlockSpec,
        condition: ConditionSchema,
        variant: str,
    ) -> str:
        """
        Build user prompt with condition context.

        Injects real condition data so the LLM enriches rather than fabricates.
        """
        hint = (spec.content_hint or "").strip().lower()
        lines: list[str] = []

        # --- Identity and purpose ---
        lines.append(f"Condition: {condition.display_name} ({condition.icd10})")
        lines.append(f"Document variant: {variant}")
        lines.append(f"Section purpose: {spec.content_hint}")
        lines.append(f"Target length: ~{spec.target_word_count} words" if spec.target_word_count else "Target length: ~100 words")

        # --- Variant tone guidance ---
        if variant == "partners":
            lines.append(
                "Tone: Advanced clinical language, FNON framework integration, "
                "quantitative parameters where available."
            )
        else:
            lines.append(
                "Tone: Clear clinical language, straightforward protocol descriptions "
                "suitable for a clinical fellow."
            )

        lines.append("")  # blank separator

        # --- Always include: overview (first 200 chars) ---
        if condition.overview:
            overview_snippet = condition.overview[:200].rstrip()
            if len(condition.overview) > 200:
                overview_snippet += "..."
            lines.append(f"Clinical overview: {overview_snippet}")

        # --- Contextual data based on content_hint ---
        if "evidence" in hint and condition.evidence_summary:
            lines.append(f"Evidence summary: {condition.evidence_summary}")

        if ("protocol" in hint or "session" in hint or "treatment" in hint) and condition.protocols:
            lines.append("Available protocols:")
            for proto in condition.protocols[:2]:
                params_str = ""
                if proto.parameters:
                    param_items = [f"{k}: {v}" for k, v in list(proto.parameters.items())[:4]]
                    params_str = " | ".join(param_items)
                session_str = f", {proto.session_count} sessions" if proto.session_count else ""
                lines.append(
                    f"  • {proto.label} — {proto.target_region} ({proto.target_abbreviation})"
                    f"{session_str}"
                    + (f" [{params_str}]" if params_str else "")
                )

        if ("safety" in hint or "contraindication" in hint) and condition.contraindications:
            lines.append("Contraindications (real, verified):")
            for c in condition.contraindications[:5]:
                lines.append(f"  • {c}")

        if ("fnon" in hint or "network" in hint) and condition.fnon_rationale:
            lines.append(f"FNON rationale: {condition.fnon_rationale}")

        if "phenotype" in hint and condition.phenotypes:
            lines.append("Clinical phenotypes:")
            for ph in condition.phenotypes[:2]:
                lines.append(f"  • {ph.label}: {ph.description}")

        if ("pathophysiology" in hint or "overview" in hint) and condition.pathophysiology:
            lines.append(f"Pathophysiology: {condition.pathophysiology[:300]}")

        lines.append("")
        lines.append(
            "Write the content now. Do not include headings. Output only the paragraph text."
        )

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Client initialisation
    # ------------------------------------------------------------------

    def _get_client(self) -> Any:
        """Lazy-init anthropic client."""
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic(api_key=self._api_key)
        return self._client
