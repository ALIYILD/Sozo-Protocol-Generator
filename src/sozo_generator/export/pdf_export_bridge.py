"""
PDF export bridge for the SOZO long-document production pipeline.

Converts a CanonicalDocument to PDF by:
  Strategy 1 (default): Export to DOCX via CanonicalDocxExporter, then convert
                         via LibreOffice or pandoc.
  Strategy 2 (future):  Direct PDF via ReportLab.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
from typing import Optional

from sozo_generator.schemas.canonical import CanonicalDocument

logger = logging.getLogger(__name__)


class PDFExportBridge:
    """
    Bridge for PDF export from CanonicalDocument.

    Strategy 1 (implemented): Export to DOCX first, then convert via
    LibreOffice or pandoc subprocess call.
    Strategy 2 (future): Direct PDF via ReportLab.
    """

    def __init__(self, docx_exporter=None):
        # Late import to avoid circular dependency at module level
        if docx_exporter is None:
            from sozo_generator.export.docx_exporter import CanonicalDocxExporter
            docx_exporter = CanonicalDocxExporter()
        self.docx_exporter = docx_exporter

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def export(
        self,
        document: CanonicalDocument,
        output_path: Optional[str] = None,
    ) -> Optional[str]:
        """
        Export CanonicalDocument to PDF.

        Steps:
        1. Export to DOCX via CanonicalDocxExporter.
        2. Try LibreOffice headless conversion.
        3. If LibreOffice unavailable, try pandoc.
        4. If neither is available, log a warning and return None.

        Args:
            document: The CanonicalDocument to export.
            output_path: Desired PDF output path. If None, derived from DOCX path.

        Returns:
            Path to the generated PDF, or None if conversion failed.
        """
        # Step 1: produce DOCX
        docx_output: Optional[str] = None
        try:
            docx_output = self.docx_exporter.export(document)
            logger.info("PDF bridge: DOCX produced at %s", docx_output)
        except Exception as exc:
            logger.error("PDF bridge: DOCX generation failed: %s", exc, exc_info=True)
            return None

        # Determine PDF output path
        if output_path is None:
            output_path = os.path.splitext(docx_output)[0] + ".pdf"

        output_dir = os.path.dirname(os.path.abspath(output_path))
        os.makedirs(output_dir, exist_ok=True)

        # Step 2: Try LibreOffice
        pdf_path = self._try_libreoffice(docx_output, output_dir)
        if pdf_path:
            # LibreOffice places the PDF next to the DOCX; move if needed
            expected_lo_path = os.path.splitext(docx_output)[0] + ".pdf"
            if os.path.isfile(expected_lo_path) and os.path.abspath(expected_lo_path) != os.path.abspath(output_path):
                try:
                    shutil.move(expected_lo_path, output_path)
                    pdf_path = output_path
                except OSError as mv_err:
                    logger.warning("PDF bridge: could not move %s to %s: %s", expected_lo_path, output_path, mv_err)
                    pdf_path = expected_lo_path
            return pdf_path

        # Step 3: Try pandoc
        pdf_path = self._try_pandoc(docx_output, output_path)
        if pdf_path:
            return pdf_path

        # Step 4: Neither available
        logger.warning(
            "PDF bridge: no PDF converter available (LibreOffice or pandoc). "
            "DOCX is at %s. Install LibreOffice or pandoc to enable PDF export.",
            docx_output,
        )
        return None

    # ------------------------------------------------------------------
    # LibreOffice conversion
    # ------------------------------------------------------------------

    def _try_libreoffice(self, docx_path: str, output_dir: str) -> Optional[str]:
        """
        Attempt LibreOffice headless conversion.

        Returns the expected PDF path if successful, None otherwise.
        """
        lo_cmd = self._find_libreoffice()
        if lo_cmd is None:
            logger.debug("PDF bridge: LibreOffice not found on PATH.")
            return None

        cmd = [
            lo_cmd,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            docx_path,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                expected = os.path.join(
                    output_dir,
                    os.path.splitext(os.path.basename(docx_path))[0] + ".pdf",
                )
                if os.path.isfile(expected):
                    logger.info("PDF bridge: LibreOffice conversion succeeded: %s", expected)
                    return expected
                else:
                    logger.warning(
                        "PDF bridge: LibreOffice returned 0 but PDF not found at %s. stdout: %s",
                        expected,
                        result.stdout.strip(),
                    )
                    return None
            else:
                logger.warning(
                    "PDF bridge: LibreOffice returned non-zero (%d). stderr: %s",
                    result.returncode,
                    result.stderr.strip(),
                )
                return None
        except subprocess.TimeoutExpired:
            logger.warning("PDF bridge: LibreOffice conversion timed out.")
            return None
        except OSError as exc:
            logger.warning("PDF bridge: LibreOffice execution error: %s", exc)
            return None

    def _find_libreoffice(self) -> Optional[str]:
        """Return the LibreOffice executable name/path, or None if not found."""
        candidates = [
            "libreoffice",
            "soffice",
            # Windows common paths
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            # macOS
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        ]
        for candidate in candidates:
            if shutil.which(candidate):
                return candidate
            if os.path.isfile(candidate):
                return candidate
        return None

    # ------------------------------------------------------------------
    # pandoc conversion
    # ------------------------------------------------------------------

    def _try_pandoc(self, docx_path: str, output_path: str) -> Optional[str]:
        """
        Attempt pandoc conversion (docx -> pdf).

        pandoc requires a PDF engine (e.g. xelatex, wkhtmltopdf, weasyprint).
        Returns the PDF path if successful, None otherwise.
        """
        if shutil.which("pandoc") is None:
            logger.debug("PDF bridge: pandoc not found on PATH.")
            return None

        cmd = ["pandoc", docx_path, "-o", output_path]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0 and os.path.isfile(output_path):
                logger.info("PDF bridge: pandoc conversion succeeded: %s", output_path)
                return output_path
            else:
                logger.warning(
                    "PDF bridge: pandoc returned %d. stderr: %s",
                    result.returncode,
                    result.stderr.strip(),
                )
                return None
        except subprocess.TimeoutExpired:
            logger.warning("PDF bridge: pandoc conversion timed out.")
            return None
        except OSError as exc:
            logger.warning("PDF bridge: pandoc execution error: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Availability check
    # ------------------------------------------------------------------

    def is_pdf_available(self) -> bool:
        """Return True if at least one PDF converter (LibreOffice or pandoc) is available."""
        return self._find_libreoffice() is not None or shutil.which("pandoc") is not None
