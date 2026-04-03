"""
PDF Export Module.

Converts generated DOCX documents to PDF format. Supports multiple backends:
1. docx2pdf (requires LibreOffice or Microsoft Word) — best quality
2. subprocess call to LibreOffice (headless) — works on Linux/CI
3. Fallback: skip PDF and log warning

Usage:
    from sozo_generator.docx.pdf_export import convert_to_pdf, batch_convert_to_pdf

    pdf_path = convert_to_pdf("output/doc.docx")
    results = batch_convert_to_pdf(["doc1.docx", "doc2.docx"])
"""
from __future__ import annotations

import logging
import subprocess
import shutil
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _find_libreoffice() -> Optional[str]:
    """Find LibreOffice binary path."""
    candidates = [
        "libreoffice",
        "soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/bin/libreoffice",
        "/usr/bin/soffice",
        "/snap/bin/libreoffice",
    ]
    for cmd in candidates:
        if shutil.which(cmd):
            return cmd
    return None


def convert_to_pdf(
    docx_path: str | Path,
    output_dir: str | Path | None = None,
) -> Optional[Path]:
    """Convert a DOCX file to PDF.

    Tries docx2pdf first, falls back to LibreOffice headless.

    Args:
        docx_path: Path to the .docx file
        output_dir: Output directory for PDF (default: same as docx)

    Returns:
        Path to the generated PDF, or None if conversion failed
    """
    docx_path = Path(docx_path)
    if not docx_path.exists():
        logger.error(f"DOCX file not found: {docx_path}")
        return None

    if output_dir:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        out_dir = docx_path.parent

    pdf_path = out_dir / docx_path.with_suffix(".pdf").name

    # Method 1: docx2pdf library
    try:
        from docx2pdf import convert
        convert(str(docx_path), str(pdf_path))
        if pdf_path.exists() and pdf_path.stat().st_size > 0:
            logger.info(f"PDF created (docx2pdf): {pdf_path}")
            return pdf_path
    except ImportError:
        logger.debug("docx2pdf not installed, trying LibreOffice")
    except Exception as e:
        logger.debug(f"docx2pdf failed: {e}, trying LibreOffice")

    # Method 2: LibreOffice headless
    lo_bin = _find_libreoffice()
    if lo_bin:
        try:
            result = subprocess.run(
                [
                    lo_bin,
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", str(out_dir),
                    str(docx_path),
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0 and pdf_path.exists():
                logger.info(f"PDF created (LibreOffice): {pdf_path}")
                return pdf_path
            else:
                logger.warning(f"LibreOffice conversion failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.warning("LibreOffice conversion timed out")
        except Exception as e:
            logger.warning(f"LibreOffice conversion error: {e}")

    logger.warning(
        f"PDF conversion unavailable for {docx_path.name}. "
        f"Install docx2pdf or LibreOffice for PDF export."
    )
    return None


def batch_convert_to_pdf(
    docx_paths: list[str | Path],
    output_dir: str | Path | None = None,
) -> dict[str, Optional[Path]]:
    """Convert multiple DOCX files to PDF.

    Args:
        docx_paths: List of DOCX file paths
        output_dir: Shared output directory (None = same as each docx)

    Returns:
        Dict mapping docx filename -> PDF path (or None if failed)
    """
    results = {}
    for docx_path in docx_paths:
        docx_path = Path(docx_path)
        pdf = convert_to_pdf(docx_path, output_dir)
        results[docx_path.name] = pdf

    success = sum(1 for v in results.values() if v is not None)
    logger.info(f"PDF batch: {success}/{len(results)} converted")
    return results
