"""Document assembler for the SOZO long-document production pipeline.

Assembles a CanonicalDocument from sections, assets, references, and metadata.
Acts as the bridge between the generation phase and the DOCX rendering phase,
and provides a compatibility adapter to the legacy DocumentSpec / DocumentRenderer.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Optional

from sozo_generator.schemas.canonical import (
    AssetRecord,
    AssemblyProvenance,
    CanonicalBlock,
    CanonicalCitation,
    CanonicalDocument,
    CanonicalSection,
    DocumentBlueprint,
)
from sozo_generator.schemas.condition import ConditionSchema
from sozo_generator.schemas.documents import DocumentSpec, SectionContent
from sozo_generator.core.enums import DocumentType, Tier

logger = logging.getLogger(__name__)


def _new_id() -> str:
    return str(uuid.uuid4())


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


class DocumentAssembler:
    """
    Assembles a CanonicalDocument from sections, assets, and metadata.

    Responsibilities:
    1. Merge canonical sections in order
    2. Resolve asset references in blocks (embed AssetRecord into CanonicalBlock.asset_record)
    3. Assign table/figure numbering labels
    4. Assign caption strings to blocks
    5. Build references/citations section
    6. Build appendices section
    7. Build TOC entries
    8. Set document metadata
    9. Record assembly provenance
    10. Validate assembly completeness (basic check)
    """

    def __init__(self, asset_registry: Optional[Any] = None) -> None:
        """
        Args:
            asset_registry: AssetRegistry instance for resolving asset references.
        """
        self.asset_registry = asset_registry

    # ------------------------------------------------------------------
    # Main assembly pipeline
    # ------------------------------------------------------------------

    def assemble(
        self,
        blueprint: DocumentBlueprint,
        sections: list[CanonicalSection],
        condition: ConditionSchema,
        references: Optional[list[CanonicalCitation]] = None,
        appendix_sections: Optional[list[CanonicalSection]] = None,
    ) -> CanonicalDocument:
        """
        Full assembly pipeline:
        1. Sort sections by ordering
        2. Resolve asset references throughout
        3. Finalize asset numbering
        4. Assign captions to all asset blocks
        5. Build TOC entries
        6. Build references section
        7. Build appendices
        8. Record provenance
        9. Return CanonicalDocument
        """
        errors: list[str] = []

        # 1. Sort sections by ordering
        sorted_sections = sorted(sections or [], key=lambda s: s.ordering)

        # 2. Resolve asset references
        if self.asset_registry is not None:
            sorted_sections = self.resolve_asset_references(
                sorted_sections, self.asset_registry
            )

        # 3. Finalize asset numbering in registry
        if self.asset_registry is not None and hasattr(
            self.asset_registry, "finalize_numbering"
        ):
            try:
                self.asset_registry.finalize_numbering()
            except Exception as exc:  # noqa: BLE001
                msg = f"finalize_numbering failed: {exc}"
                logger.warning(msg)
                errors.append(msg)

        # 4. Assign captions
        sorted_sections = self.assign_captions(sorted_sections)

        # 5. Build TOC entries
        toc_entries = self.build_toc_entries(sorted_sections)

        # 6. Build references section — merge passed-in citations with condition.references
        all_citations = list(references or [])
        if condition is not None:
            all_citations = self._merge_condition_references(all_citations, condition)
        ref_section = self.build_references_section(all_citations, condition)

        # 7. Build appendices
        assembled_appendices: list[CanonicalSection] = list(appendix_sections or [])

        # 8. Collect assets from registry for the document
        all_assets: list[AssetRecord] = []
        if self.asset_registry is not None and hasattr(self.asset_registry, "get_all"):
            try:
                all_assets = self.asset_registry.get_all()
            except Exception as exc:  # noqa: BLE001
                logger.warning("get_all assets failed: %s", exc)

        # Validate completeness
        unresolved_count = self.count_unresolved_placeholders(sorted_sections)
        if unresolved_count > 0:
            msg = f"Assembly complete with {unresolved_count} unresolved placeholder(s)."
            logger.warning(msg)
            errors.append(msg)

        document_id = _new_id()

        # 9. Build provenance
        provenance = self.build_provenance(
            blueprint=blueprint,
            document_id=document_id,
            sections=sorted_sections,
            errors=errors if errors else None,
        )

        # Map blueprint variant to CanonicalDocument variant
        variant = blueprint.variant if blueprint is not None else "shared"

        # Finalise numbered citations
        for idx, citation in enumerate(all_citations, start=1):
            citation.reference_number = idx

        # Construct the document
        document = CanonicalDocument(
            document_id=document_id,
            condition_slug=condition.slug if condition is not None else blueprint.condition_slug,
            variant=variant,
            document_type=blueprint.document_type if blueprint is not None else "handbook",
            title=blueprint.title if blueprint is not None else "",
            subtitle=blueprint.subtitle if blueprint is not None else "",
            version=blueprint.version if blueprint is not None else "1.0",
            sections=sorted_sections,
            assets=all_assets,
            references=all_citations,
            appendices=assembled_appendices,
            toc_entries=toc_entries,
            qa_status="complete",
            assembly_provenance=provenance,
        )

        # Add the references section to appendices for completeness (optional storage)
        if ref_section.blocks:
            document.appendices.append(ref_section)

        logger.info(
            "DocumentAssembler.assemble: document_id=%s, sections=%d, "
            "assets=%d, citations=%d, unresolved=%d",
            document_id,
            len(sorted_sections),
            len(all_assets),
            len(all_citations),
            unresolved_count,
        )

        return document

    # ------------------------------------------------------------------
    # Asset resolution
    # ------------------------------------------------------------------

    def resolve_asset_references(
        self,
        sections: list[CanonicalSection],
        asset_registry: Any,
    ) -> list[CanonicalSection]:
        """
        Walk all blocks in all sections. For each block where:
        - block.asset_id is set
        - block.asset_record is None
        Look up asset_registry.get(block.asset_id) and embed the record.
        Mark block.placeholder_resolved = True if asset is found and generated.
        Mark block.placeholder_resolved = False if asset is missing.
        Returns sections with updated blocks.
        """
        for section in sections:
            self._resolve_blocks(section.blocks, asset_registry)
            if section.subsections:
                section.subsections = self.resolve_asset_references(
                    section.subsections, asset_registry
                )
        return sections

    def _resolve_blocks(
        self,
        blocks: list[CanonicalBlock],
        asset_registry: Any,
    ) -> None:
        """Mutate blocks in-place to embed AssetRecord lookups."""
        for block in blocks:
            if block.asset_id and block.asset_record is None:
                try:
                    record: Optional[AssetRecord] = asset_registry.get(block.asset_id)
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        "resolve_asset_references: registry.get(%r) raised %s",
                        block.asset_id,
                        exc,
                    )
                    record = None

                if record is not None:
                    block.asset_record = record
                    # Mark resolved only if the asset was actually generated
                    block.placeholder_resolved = record.status in (
                        "generated",
                        "validated",
                    )
                else:
                    block.placeholder_resolved = False
                    logger.debug(
                        "resolve_asset_references: asset not found in registry: %r",
                        block.asset_id,
                    )

    # ------------------------------------------------------------------
    # Caption assignment
    # ------------------------------------------------------------------

    def assign_captions(
        self,
        sections: list[CanonicalSection],
    ) -> list[CanonicalSection]:
        """
        For every block that has an asset_record with a numbering_label:
        - Set block.caption = asset_record.caption (if set) else build from title
        - Set block.numbering_label = asset_record.numbering_label
        Returns sections with captions assigned.
        """
        for section in sections:
            self._assign_block_captions(section.blocks)
            if section.subsections:
                section.subsections = self.assign_captions(section.subsections)
        return sections

    def _assign_block_captions(self, blocks: list[CanonicalBlock]) -> None:
        """Mutate blocks in-place to assign captions and numbering labels."""
        for block in blocks:
            record = block.asset_record
            if record is None:
                continue

            # Assign numbering label from the asset record
            if record.numbering_label:
                block.numbering_label = record.numbering_label

            # Assign caption: prefer explicit caption, fall back to title-based
            if record.caption:
                block.caption = record.caption
            elif record.numbering_label:
                # Build a minimal caption from the numbering label and content hint
                title_hint = (
                    record.source_data.get("title", "")
                    if isinstance(record.source_data, dict)
                    else ""
                )
                if title_hint:
                    block.caption = f"{record.numbering_label}. {title_hint}"
                else:
                    block.caption = record.numbering_label

    # ------------------------------------------------------------------
    # TOC
    # ------------------------------------------------------------------

    def build_toc_entries(
        self,
        sections: list[CanonicalSection],
    ) -> list[dict]:
        """
        Build TOC entries list:
        [{"title": ..., "level": ..., "section_id": ..., "page_hint": None}]

        Include:
        - All sections at level 1 (main sections)
        - Subsections at level 2 (if they have titles)
        - Appendices

        page_hint: None (set later by DOCX renderer if it supports it)
        """
        entries: list[dict] = []
        self._collect_toc_entries(sections, entries)
        return entries

    def _collect_toc_entries(
        self,
        sections: list[CanonicalSection],
        entries: list[dict],
    ) -> None:
        """Recursively collect TOC entries."""
        for section in sorted(sections, key=lambda s: s.ordering):
            entries.append(
                {
                    "title": section.title,
                    "level": section.level,
                    "section_id": section.section_id,
                    "page_hint": None,
                }
            )
            if section.subsections:
                self._collect_toc_entries(section.subsections, entries)

    # ------------------------------------------------------------------
    # References section
    # ------------------------------------------------------------------

    def build_references_section(
        self,
        citations: list[CanonicalCitation],
        condition: ConditionSchema,
    ) -> CanonicalSection:
        """
        Build a CanonicalSection for References.

        Steps:
        1. Collect all citations (passed in + from condition.references)
        2. Assign sequential reference_number (1, 2, 3...)
        3. Format each citation as a CanonicalBlock(block_type="text")
           with content: "[N] AuthorsShort (Year). Title. Journal."
        4. Return as CanonicalSection(section_type="references")
        """
        blocks: list[CanonicalBlock] = []

        for idx, citation in enumerate(citations, start=1):
            citation.reference_number = idx
            year_str = str(citation.year) if citation.year else "n.d."
            journal_str = f" {citation.journal}." if citation.journal else ""
            content = (
                f"[{idx}] {citation.authors_short} ({year_str}). "
                f"{citation.title}.{journal_str}"
            )
            blocks.append(
                CanonicalBlock(
                    block_type="text",
                    content=content,
                )
            )

        condition_slug = condition.slug if condition is not None else "unknown"

        return CanonicalSection(
            title="References",
            level=1,
            section_type="references",
            blocks=blocks,
            ordering=9999,
        )

    # ------------------------------------------------------------------
    # Appendix section
    # ------------------------------------------------------------------

    def build_appendix_section(
        self,
        content: list[dict],  # list of {"title": str, "body": str}
        condition: ConditionSchema,
    ) -> CanonicalSection:
        """
        Build an Appendix CanonicalSection from content dicts.
        Each entry becomes a subsection.
        """
        subsections: list[CanonicalSection] = []

        for idx, entry in enumerate(content or []):
            title = entry.get("title", f"Appendix {idx + 1}")
            body = entry.get("body", "")
            body_block = CanonicalBlock(
                block_type="text",
                content=body,
            )
            sub = CanonicalSection(
                title=title,
                level=2,
                section_type="appendix",
                blocks=[body_block] if body else [],
                ordering=idx,
            )
            subsections.append(sub)

        return CanonicalSection(
            title="Appendices",
            level=1,
            section_type="appendix",
            blocks=[],
            subsections=subsections,
            ordering=9998,
        )

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    def build_provenance(
        self,
        blueprint: DocumentBlueprint,
        document_id: str,
        sections: list[CanonicalSection],
        errors: Optional[list[str]] = None,
    ) -> AssemblyProvenance:
        """Build AssemblyProvenance record for this assembly run."""
        section_log: list[dict] = [
            {
                "section_id": s.section_id,
                "title": s.title,
                "section_type": s.section_type,
                "block_count": len(s.blocks),
                "subsection_count": len(s.subsections),
                "word_count": s.word_count,
            }
            for s in (sections or [])
        ]

        blueprint_id = blueprint.blueprint_id if blueprint is not None else None
        condition_slug = blueprint.condition_slug if blueprint is not None else "unknown"
        variant = blueprint.variant if blueprint is not None else "shared"

        return AssemblyProvenance(
            document_id=document_id,
            blueprint_id=blueprint_id,
            condition_slug=condition_slug,
            variant=variant,
            section_generation_log=section_log,
            assembly_log=[
                {
                    "stage": "assemble",
                    "timestamp": _now_iso(),
                    "section_count": len(sections or []),
                }
            ],
            errors=errors or [],
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def count_unresolved_placeholders(
        self, sections: list[CanonicalSection]
    ) -> int:
        """Count blocks where placeholder_resolved=False across all sections recursively."""
        count = 0
        for section in sections or []:
            for block in section.blocks:
                if not block.placeholder_resolved:
                    count += 1
            if section.subsections:
                count += self.count_unresolved_placeholders(section.subsections)
        return count

    def collect_all_evidence_pmids(
        self, sections: list[CanonicalSection]
    ) -> list[str]:
        """Collect all unique PMIDs mentioned in section.evidence_pmids."""
        seen: set[str] = set()
        result: list[str] = []
        for section in sections or []:
            for pmid in section.evidence_pmids:
                if pmid not in seen:
                    seen.add(pmid)
                    result.append(pmid)
            if section.subsections:
                for pmid in self.collect_all_evidence_pmids(section.subsections):
                    if pmid not in seen:
                        seen.add(pmid)
                        result.append(pmid)
        return result

    # ------------------------------------------------------------------
    # Legacy DocumentSpec bridge
    # ------------------------------------------------------------------

    def to_legacy_document_spec(
        self,
        document: CanonicalDocument,
        condition: ConditionSchema,
    ) -> DocumentSpec:
        """
        Convert a CanonicalDocument to the legacy DocumentSpec format
        for use with the existing DocumentRenderer.

        This is the compatibility bridge.

        Mapping:
        - document.title → spec.title
        - document.sections → spec.sections (as SectionContent objects)
        - document.references → spec.references
        - document.condition_slug → spec.condition_slug
        - document.variant → spec.tier

        For each CanonicalSection → SectionContent:
        - section.title → SectionContent.title
        - All text blocks in section.blocks → SectionContent.content (joined with newlines)
        - All asset blocks where asset_record.asset_type=="table" → SectionContent.tables
        - evidence_pmids → SectionContent.evidence_pmids
        """
        # Map variant to Tier
        variant = document.variant if document.variant else "shared"
        if variant == "fellow":
            tier = Tier.FELLOW
        elif variant == "partners":
            tier = Tier.PARTNERS
        else:
            # "shared" maps to BOTH, or default to FELLOW if BOTH unavailable
            tier = Tier.BOTH if hasattr(Tier, "BOTH") else Tier.FELLOW

        # Map document_type to DocumentType enum
        doc_type_str = document.document_type if document.document_type else "handbook"
        try:
            doc_type = DocumentType(doc_type_str)
        except ValueError:
            doc_type = DocumentType.HANDBOOK

        # Convert sections
        legacy_sections = [
            self._canonical_section_to_legacy(s)
            for s in (document.sections or [])
        ]

        # Convert references to list[dict]
        legacy_refs: list[dict] = []
        for citation in document.references or []:
            ref_dict: dict = {
                "reference_number": citation.reference_number,
                "title": citation.title,
                "authors_short": citation.authors_short,
                "year": citation.year,
                "journal": citation.journal,
            }
            if citation.pmid:
                ref_dict["pmid"] = citation.pmid
            if citation.doi:
                ref_dict["doi"] = citation.doi
            legacy_refs.append(ref_dict)

        # condition_name: prefer display_name, fall back to slug
        condition_name = (
            condition.display_name
            if condition is not None and condition.display_name
            else document.condition_slug
        )

        return DocumentSpec(
            document_type=doc_type,
            tier=tier,
            condition_slug=document.condition_slug,
            condition_name=condition_name,
            title=document.title,
            subtitle=document.subtitle or None,
            version=document.version,
            sections=legacy_sections,
            references=legacy_refs,
        )

    def _canonical_section_to_legacy(
        self, section: CanonicalSection
    ) -> SectionContent:
        """Convert a single CanonicalSection to a SectionContent."""
        # Gather text content from text/list/callout/heading blocks
        text_parts: list[str] = []
        tables: list[dict] = []
        figures: list[str] = []

        for block in section.blocks or []:
            if block.block_type in ("text", "list", "callout", "heading"):
                if block.content:
                    text_parts.append(block.content)
            elif block.block_type in ("table",):
                # Build a table dict for legacy renderer
                table_dict = self._asset_record_to_table_dict(block)
                if table_dict:
                    tables.append(table_dict)
            elif block.block_type in ("figure", "chart", "image"):
                # Extract output path for figures
                if block.asset_record and block.asset_record.output_path:
                    figures.append(block.asset_record.output_path)
                elif block.content:
                    figures.append(block.content)

        # Recurse into subsections
        legacy_subsections = [
            self._canonical_section_to_legacy(sub)
            for sub in (section.subsections or [])
        ]

        return SectionContent(
            section_id=section.section_id,
            title=section.title,
            content="\n\n".join(text_parts),
            subsections=legacy_subsections,
            tables=tables,
            figures=figures,
            evidence_pmids=list(section.evidence_pmids or []),
        )

    def _asset_record_to_table_dict(self, block: CanonicalBlock) -> Optional[dict]:
        """Convert a table asset block to the legacy table dict format."""
        record = block.asset_record
        if record is None:
            # Fall back to content as plain text representation
            if block.content:
                return {"title": block.caption or "", "raw_content": block.content}
            return None

        source = record.source_data if isinstance(record.source_data, dict) else {}
        table_dict: dict = {
            "title": record.caption or block.caption or source.get("title", ""),
            "numbering_label": block.numbering_label or record.numbering_label or "",
            "headers": source.get("headers", []),
            "rows": source.get("rows", []),
            "footer": source.get("footer", ""),
        }
        return table_dict

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _merge_condition_references(
        self,
        citations: list[CanonicalCitation],
        condition: ConditionSchema,
    ) -> list[CanonicalCitation]:
        """
        Merge condition.references (list[dict]) into citations list.
        Avoids duplicates by matching on pmid if available.
        """
        existing_pmids: set[str] = {
            c.pmid for c in citations if c.pmid
        }
        existing_dois: set[str] = {
            c.doi for c in citations if c.doi
        }

        merged = list(citations)
        for ref_dict in condition.references or []:
            pmid = ref_dict.get("pmid")
            doi = ref_dict.get("doi")

            # Skip duplicates
            if pmid and pmid in existing_pmids:
                continue
            if doi and doi in existing_dois:
                continue

            try:
                citation = CanonicalCitation(
                    pmid=pmid,
                    doi=doi,
                    title=ref_dict.get("title", ""),
                    authors_short=ref_dict.get("authors_short", ref_dict.get("authors", "")),
                    year=ref_dict.get("year"),
                    journal=ref_dict.get("journal"),
                )
                merged.append(citation)
                if pmid:
                    existing_pmids.add(pmid)
                if doi:
                    existing_dois.add(doi)
            except Exception as exc:  # noqa: BLE001
                logger.debug("Skipping malformed condition reference: %s — %s", ref_dict, exc)

        return merged
