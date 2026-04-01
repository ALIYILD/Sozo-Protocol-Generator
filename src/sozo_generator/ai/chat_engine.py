"""
Chat engine — processes user messages, executes actions, and returns responses.

This is the brain of the chat interface. It:
1. Parses user intent (via LLM or rules)
2. Validates the request against the registry
3. Executes the appropriate generation/merge/query action
4. Returns a structured response with results and download paths

SAFETY: Clinical content comes ONLY from ConditionSchema.
The chat engine orchestrates — it never fabricates medical data.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Callable

from .intent_parser import parse_intent_rules, parse_intent_llm, UserIntent
from .doc_composer import DocComposer

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """A single message in the chat history."""
    role: str  # "user" or "assistant"
    content: str
    files: list[Path] = field(default_factory=list)
    intent: Optional[UserIntent] = None
    error: bool = False


@dataclass
class ChatResponse:
    """Response from the chat engine."""
    message: str
    files: dict[str, Path] = field(default_factory=dict)  # label -> path
    intent: Optional[UserIntent] = None
    success: bool = True
    action_taken: str = ""
    details: list[str] = field(default_factory=list)


# ── Condition display names for nice output ──────────────────────────────
_CONDITION_NAMES = {
    "parkinsons": "Parkinson's Disease",
    "depression": "Major Depressive Disorder",
    "anxiety": "Generalized Anxiety Disorder",
    "adhd": "ADHD",
    "alzheimers": "Alzheimer's Disease / MCI",
    "stroke_rehab": "Post-Stroke Rehabilitation",
    "tbi": "Traumatic Brain Injury",
    "chronic_pain": "Chronic Pain / Fibromyalgia",
    "ptsd": "PTSD",
    "ocd": "OCD",
    "ms": "Multiple Sclerosis",
    "asd": "Autism Spectrum Disorder",
    "long_covid": "Long COVID",
    "tinnitus": "Tinnitus",
    "insomnia": "Insomnia",
}

_DOC_TYPE_NAMES = {
    "evidence_based_protocol": "Evidence-Based Protocol",
    "all_in_one_protocol": "All-in-One Protocol",
    "handbook": "Clinical Handbook",
    "clinical_exam": "Clinical Examination Checklist",
    "phenotype_classification": "Phenotype Classification",
    "responder_tracking": "Responder Tracking",
    "psych_intake": "Psychological Intake & PRS",
    "network_assessment": "6-Network Bedside Assessment",
}


class ChatEngine:
    """Main chat processing engine."""

    def __init__(
        self,
        output_dir: str = "outputs/documents/",
        anthropic_api_key: str = "",
        openai_api_key: str = "",
        use_llm: bool = False,
        progress_callback: Optional[Callable[[str], None]] = None,
    ):
        self.output_dir = Path(output_dir)
        self.anthropic_api_key = anthropic_api_key
        self.openai_api_key = openai_api_key
        self.use_llm = use_llm and (anthropic_api_key or openai_api_key)
        self.composer = DocComposer(output_dir=output_dir)
        self._progress = progress_callback or (lambda msg: None)
        self._registry = None

    @property
    def registry(self):
        if self._registry is None:
            from ..conditions.registry import get_registry
            self._registry = get_registry()
        return self._registry

    def process_message(
        self,
        text: str,
        uploaded_file_path: Optional[Path] = None,
    ) -> ChatResponse:
        """
        Process a user message and return a response.

        This is the main entry point for the chat interface.
        """
        start = time.time()

        # Parse intent
        if self.use_llm and self.anthropic_api_key:
            intent = parse_intent_llm(text, self.anthropic_api_key, provider="anthropic")
        elif self.use_llm and self.openai_api_key:
            intent = parse_intent_llm(text, self.openai_api_key, provider="openai")
        else:
            intent = parse_intent_rules(text)

        if uploaded_file_path:
            intent.action = "upload"
            intent.template_path = str(uploaded_file_path)

        logger.info("Parsed intent: %s", intent.summary)

        # Route to handler
        handlers = {
            "generate": self._handle_generate,
            "merge": self._handle_merge,
            "upload": self._handle_upload,
            "list": self._handle_list,
            "explain": self._handle_explain,
            "qa": self._handle_qa,
            "help": self._handle_help,
            "unknown": self._handle_unknown,
        }
        handler = handlers.get(intent.action, self._handle_unknown)

        try:
            response = handler(intent)
        except Exception as e:
            logger.error("Chat engine error: %s", e, exc_info=True)
            response = ChatResponse(
                message=f"Something went wrong: {e}",
                intent=intent,
                success=False,
                action_taken="error",
            )

        elapsed = time.time() - start
        response.details.append(f"Completed in {elapsed:.1f}s")
        return response

    # ── Action handlers ──────────────────────────────────────────────────

    def _handle_generate(self, intent: UserIntent) -> ChatResponse:
        """Generate documents for conditions."""
        conditions = self._resolve_conditions(intent)
        if not conditions:
            return ChatResponse(
                message=(
                    "I couldn't determine which condition(s) you want. "
                    "Try something like:\n"
                    "- *Generate all documents for Parkinson's*\n"
                    "- *Create evidence-based protocol for depression and anxiety*\n"
                    "- *Build all 15 conditions*"
                ),
                intent=intent,
                success=False,
            )

        doc_types = intent.doc_types if intent.doc_types else []
        tier = intent.tier

        all_outputs: dict[str, Path] = {}
        generated_details: list[str] = []

        for slug in conditions:
            self._progress(f"Generating {_CONDITION_NAMES.get(slug, slug)}...")
            try:
                condition = self.registry.get(slug)
                outputs = self.composer.generate_standard(condition, doc_types=doc_types, tier=tier)
                for key, path in outputs.items():
                    all_outputs[f"{slug}/{key}"] = path
                doc_count = len(outputs)
                ref_count = len(condition.references) if condition.references else 0
                generated_details.append(
                    f"**{_CONDITION_NAMES.get(slug, slug)}**: {doc_count} documents, {ref_count} references"
                )
            except Exception as e:
                generated_details.append(f"**{slug}**: Failed — {e}")

        # Build response message
        doc_type_desc = ", ".join(_DOC_TYPE_NAMES.get(dt, dt) for dt in doc_types) if doc_types else "all document types"
        condition_desc = (
            "all 15 conditions" if intent.all_conditions
            else ", ".join(_CONDITION_NAMES.get(c, c) for c in conditions)
        )

        msg = (
            f"Generated **{len(all_outputs)}** documents for {condition_desc} "
            f"({doc_type_desc}, {tier} tier).\n\n"
            + "\n".join(f"- {d}" for d in generated_details)
        )

        return ChatResponse(
            message=msg,
            files=all_outputs,
            intent=intent,
            success=True,
            action_taken="generate",
            details=generated_details,
        )

    def _handle_merge(self, intent: UserIntent) -> ChatResponse:
        """Merge multiple document types into one."""
        conditions = self._resolve_conditions(intent)
        if not conditions:
            return ChatResponse(
                message="Which condition should I merge documents for? E.g., *Merge handbook and protocol for Parkinson's*",
                intent=intent,
                success=False,
            )

        merge_types = intent.merge_doc_types or intent.doc_types
        if len(merge_types) < 2:
            return ChatResponse(
                message=(
                    "I need at least 2 document types to merge. Try:\n"
                    "- *Merge handbook and evidence-based protocol for depression*\n"
                    "- *Combine clinical exam and phenotype classification for ADHD*"
                ),
                intent=intent,
                success=False,
            )

        all_outputs: dict[str, Path] = {}
        details: list[str] = []
        tier = intent.tier if intent.tier != "both" else "fellow"

        for slug in conditions:
            self._progress(f"Merging documents for {_CONDITION_NAMES.get(slug, slug)}...")
            try:
                condition = self.registry.get(slug)
                merged_path = self.composer.merge_documents(
                    condition=condition,
                    doc_types_to_merge=merge_types,
                    tier=tier,
                    custom_title=intent.custom_title,
                )
                all_outputs[f"{slug}/merged"] = merged_path
                type_names = [_DOC_TYPE_NAMES.get(dt, dt) for dt in merge_types]
                details.append(f"**{_CONDITION_NAMES.get(slug, slug)}**: Merged {' + '.join(type_names)}")
            except Exception as e:
                details.append(f"**{slug}**: Merge failed — {e}")

        msg = (
            f"Merged **{len(all_outputs)}** documents.\n\n"
            + "\n".join(f"- {d}" for d in details)
        )

        return ChatResponse(
            message=msg,
            files=all_outputs,
            intent=intent,
            success=True,
            action_taken="merge",
            details=details,
        )

    def _handle_upload(self, intent: UserIntent) -> ChatResponse:
        """Generate from an uploaded template."""
        if not intent.template_path:
            return ChatResponse(
                message="Please upload a DOCX template file along with your message.",
                intent=intent,
                success=False,
            )

        template_path = Path(intent.template_path)
        conditions = self._resolve_conditions(intent)
        if not conditions:
            # Default to all conditions for template generation
            conditions = self.registry.list_slugs()
            intent.all_conditions = True

        all_outputs: dict[str, Path] = {}
        details: list[str] = []

        for slug in conditions:
            self._progress(f"Generating from template for {_CONDITION_NAMES.get(slug, slug)}...")
            try:
                condition = self.registry.get(slug)
                outputs = self.composer.generate_from_template(
                    condition=condition,
                    template_path=template_path,
                    tier=intent.tier,
                )
                for key, path in outputs.items():
                    all_outputs[f"{slug}/{key}"] = path
                details.append(f"**{_CONDITION_NAMES.get(slug, slug)}**: {len(outputs)} documents")
            except Exception as e:
                details.append(f"**{slug}**: Failed — {e}")

        msg = (
            f"Generated **{len(all_outputs)}** documents from template "
            f"`{template_path.name}` for {len(conditions)} conditions.\n\n"
            + "\n".join(f"- {d}" for d in details)
        )

        return ChatResponse(
            message=msg,
            files=all_outputs,
            intent=intent,
            success=True,
            action_taken="upload_generate",
            details=details,
        )

    def _handle_list(self, intent: UserIntent) -> ChatResponse:
        """List available conditions or document types."""
        if any(w in intent.raw_text.lower() for w in ["document", "doc type", "types"]):
            lines = ["**Available document types (8):**\n"]
            for slug, name in _DOC_TYPE_NAMES.items():
                lines.append(f"- `{slug}` — {name}")
            return ChatResponse(message="\n".join(lines), intent=intent, action_taken="list_docs")

        lines = ["**Available conditions (15):**\n"]
        for slug in sorted(self.registry.list_slugs()):
            name = _CONDITION_NAMES.get(slug, slug)
            try:
                condition = self.registry.get(slug)
                refs = len(condition.references) if condition.references else 0
                protos = len(condition.protocols) if condition.protocols else 0
                lines.append(f"- **{name}** (`{slug}`) — {refs} refs, {protos} protocols")
            except Exception:
                lines.append(f"- **{name}** (`{slug}`)")
        return ChatResponse(message="\n".join(lines), intent=intent, action_taken="list_conditions")

    def _handle_explain(self, intent: UserIntent) -> ChatResponse:
        """Explain a condition's data (from registry, not AI-generated)."""
        conditions = self._resolve_conditions(intent)
        if not conditions:
            return ChatResponse(
                message="Which condition would you like to know about?",
                intent=intent,
                success=False,
            )

        slug = conditions[0]
        try:
            c = self.registry.get(slug)
        except Exception as e:
            return ChatResponse(message=f"Could not load {slug}: {e}", intent=intent, success=False)

        lines = [
            f"## {c.display_name} ({c.icd10})\n",
            f"**Overview:** {c.overview[:300]}...\n" if len(c.overview) > 300 else f"**Overview:** {c.overview}\n",
            f"**Evidence quality:** {c.overall_evidence_quality.value}",
            f"**References:** {len(c.references)}",
            f"**Protocols:** {len(c.protocols)}",
            f"**Phenotypes:** {len(c.phenotypes)}",
            f"**Network profiles:** {len(c.network_profiles)}",
            f"**Assessment tools:** {len(c.assessment_tools)}",
            f"**Safety notes:** {len(c.safety_notes)}",
        ]
        if c.evidence_gaps:
            lines.append(f"\n**Evidence gaps:** {', '.join(c.evidence_gaps[:3])}")

        return ChatResponse(
            message="\n".join(lines),
            intent=intent,
            action_taken="explain",
        )

    def _handle_qa(self, intent: UserIntent) -> ChatResponse:
        """Run QA checks on conditions."""
        conditions = self._resolve_conditions(intent)
        if not conditions:
            conditions = self.registry.list_slugs()

        try:
            from ..qa.engine import QAEngine
            engine = QAEngine()
        except Exception as e:
            return ChatResponse(message=f"QA engine failed to load: {e}", intent=intent, success=False)

        details: list[str] = []
        total_blocks = 0
        total_warnings = 0

        for slug in conditions:
            try:
                condition = self.registry.get(slug)
                report = engine.run_condition_qa(condition)
                report.compute_counts()
                status = "PASS" if report.passed else f"FAIL ({report.block_count} blocks)"
                details.append(f"**{_CONDITION_NAMES.get(slug, slug)}**: {status}, {report.warning_count} warnings")
                total_blocks += report.block_count
                total_warnings += report.warning_count
            except Exception as e:
                details.append(f"**{slug}**: Error — {e}")

        msg = (
            f"QA results for {len(conditions)} conditions: "
            f"**{total_blocks} blocks, {total_warnings} warnings**\n\n"
            + "\n".join(f"- {d}" for d in details)
        )
        return ChatResponse(message=msg, intent=intent, action_taken="qa", details=details)

    def _handle_help(self, intent: UserIntent) -> ChatResponse:
        return ChatResponse(
            message=(
                "## SOZO Document Generator — Chat Commands\n\n"
                "**Generate documents:**\n"
                "- *Generate all documents for Parkinson's*\n"
                "- *Create evidence-based protocol for depression, fellow tier*\n"
                "- *Build handbook for all conditions*\n"
                "- *Generate all 15 conditions*\n\n"
                "**Merge documents:**\n"
                "- *Merge handbook and protocol for ADHD*\n"
                "- *Combine clinical exam and phenotype classification for anxiety*\n\n"
                "**Upload template:**\n"
                "- Upload a DOCX file and say *Generate from this template for all conditions*\n\n"
                "**Information:**\n"
                "- *List all conditions*\n"
                "- *List document types*\n"
                "- *Explain Parkinson's*\n"
                "- *Run QA on depression*\n"
            ),
            intent=intent,
            action_taken="help",
        )

    def _handle_unknown(self, intent: UserIntent) -> ChatResponse:
        return ChatResponse(
            message=(
                "I'm not sure what you'd like me to do. Try:\n"
                "- *Generate documents for [condition]*\n"
                "- *Merge handbook and protocol for [condition]*\n"
                "- *List conditions*\n"
                "- Type **help** for full command list"
            ),
            intent=intent,
            success=False,
            action_taken="unknown",
        )

    # ── Helpers ──────────────────────────────────────────────────────────

    def _resolve_conditions(self, intent: UserIntent) -> list[str]:
        """Resolve condition slugs from intent, validating against registry."""
        if intent.all_conditions:
            return self.registry.list_slugs()

        valid_slugs = set(self.registry.list_slugs())
        resolved = [c for c in intent.conditions if c in valid_slugs]

        if not resolved and intent.conditions:
            # Try fuzzy matching
            for c in intent.conditions:
                for slug in valid_slugs:
                    if c in slug or slug in c:
                        resolved.append(slug)
                        break

        return resolved
