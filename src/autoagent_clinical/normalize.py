"""Normalize SOZO outputs into text the benchmark validators understand."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def document_spec_to_benchmark_markdown(spec: Any) -> str:
    """Turn a :class:`sozo_generator.schemas.documents.DocumentSpec` into ATX markdown."""
    from sozo_generator.schemas.documents import DocumentSpec, SectionContent

    if isinstance(spec, dict):
        spec = DocumentSpec.model_validate(spec)
    elif not isinstance(spec, DocumentSpec):
        spec = DocumentSpec.model_validate(spec)

    lines: list[str] = []

    if spec.title:
        lines.append(f"# {spec.title}")
    if spec.subtitle:
        lines.append(f"*{spec.subtitle}*")
    meta_bits = [f"Audience: {spec.audience}" if spec.audience else ""]
    meta_bits = [b for b in meta_bits if b]
    if meta_bits:
        lines.append("\n".join(meta_bits))

    def walk_section(sec: SectionContent, level: int) -> None:
        lvl = max(2, min(level, 6))
        hashes = "#" * lvl
        if sec.title:
            lines.append(f"{hashes} {sec.title}")
        if sec.content and sec.content.strip():
            lines.append(sec.content.strip())
        for sub in sec.subsections:
            walk_section(sub, level + 1)

    for section in spec.sections:
        walk_section(section, 2)

    if spec.references:
        lines.append("## References")
        for ref in spec.references[:80]:
            if isinstance(ref, dict):
                title = ref.get("title") or ref.get("citation") or str(ref)[:120]
            else:
                title = str(ref)
            lines.append(f"- {title}")

    return "\n\n".join(lines) if lines else ""


def docx_to_benchmark_markdown(docx_path: str | Path) -> str:
    """Convert a generated DOCX into pseudo-markdown (headings use # prefixes).

    Validators such as protocol_structure_validator look for ATX-style headings.
    """
    from docx import Document

    path = Path(docx_path)
    if not path.is_file():
        return ""

    doc = Document(str(path))
    chunks: list[str] = []
    for para in doc.paragraphs:
        text = (para.text or "").strip()
        if not text:
            continue
        style_name = para.style.name if para.style is not None else ""
        if style_name.startswith("Heading"):
            suffix = style_name.replace("Heading", "", 1).strip()
            try:
                level = max(1, min(int(suffix), 6)) if suffix else 1
            except ValueError:
                level = 1
            prefix = "#" * level
            chunks.append(f"{prefix} {text}")
        else:
            chunks.append(text)
    return "\n\n".join(chunks)
