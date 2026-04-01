"""Figure manifest generation -- tracks all visuals produced for a build.

Builds a :class:`FigureManifest` from the files output by the visual generators,
computing content hashes and generating standard captions for each figure type.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..schemas.contracts import FigureEntry, FigureManifest

logger = logging.getLogger(__name__)

# Standard caption templates keyed by figure type.
_CAPTION_TEMPLATES: dict[str, str] = {
    "brain_map": "Brain target map for {condition}",
    "network_diagram": "FNON network dysfunction diagram for {condition}",
    "symptom_flow": "Symptom-to-protocol flow diagram for {condition}",
    "patient_journey": "Patient journey timeline for {condition}",
}


class FigureManifestBuilder:
    """Builds :class:`FigureManifest` from generated visual files.

    Parameters
    ----------
    output_base_dir:
        Root directory where visual output files are stored.
    """

    def __init__(self, output_base_dir: Path) -> None:
        self.output_base_dir = Path(output_base_dir)
        logger.info("FigureManifestBuilder initialised with base=%s", self.output_base_dir)

    def build_manifest(
        self,
        condition_slug: str,
        visual_results: dict[str, Path | None],
        legend_results: dict[str, Path | None] | None = None,
    ) -> FigureManifest:
        """Build a complete figure manifest from generation results.

        Parameters
        ----------
        condition_slug:
            Condition identifier (e.g. ``"depression"``).
        visual_results:
            Mapping of figure type to file path (or ``None`` if generation failed).
        legend_results:
            Optional mapping of legend type to file path.

        Returns
        -------
        FigureManifest
            Manifest containing entries for all successfully generated figures.
        """
        figures: list[FigureEntry] = []
        shared_legends: list[FigureEntry] = []

        for figure_type, file_path in visual_results.items():
            if file_path is None:
                logger.warning(
                    "Skipping %s for %s: no file produced", figure_type, condition_slug
                )
                continue
            file_path = Path(file_path)
            if not file_path.exists():
                logger.warning(
                    "Skipping %s for %s: file does not exist at %s",
                    figure_type,
                    condition_slug,
                    file_path,
                )
                continue
            entry = self._create_entry(figure_type, file_path, condition_slug)
            figures.append(entry)
            logger.debug("Added figure entry: %s -> %s", figure_type, file_path)

        if legend_results:
            for legend_type, file_path in legend_results.items():
                if file_path is None:
                    continue
                file_path = Path(file_path)
                if not file_path.exists():
                    logger.warning(
                        "Skipping legend %s: file does not exist at %s",
                        legend_type,
                        file_path,
                    )
                    continue
                entry = self._create_entry(legend_type, file_path, condition_slug)
                shared_legends.append(entry)
                logger.debug("Added legend entry: %s -> %s", legend_type, file_path)

        manifest = FigureManifest(
            condition_slug=condition_slug,
            figures=figures,
            shared_legends=shared_legends,
        )
        logger.info(
            "Built manifest for %s: %d figures, %d legends",
            condition_slug,
            len(figures),
            len(shared_legends),
        )
        return manifest

    def _create_entry(
        self, figure_type: str, file_path: Path, condition_slug: str
    ) -> FigureEntry:
        """Create a single :class:`FigureEntry` with hash and caption.

        Parameters
        ----------
        figure_type:
            Type identifier (e.g. ``"brain_map"``).
        file_path:
            Absolute or relative path to the generated image file.
        condition_slug:
            Condition identifier used for caption generation.
        """
        content_hash = self._compute_file_hash(file_path)
        caption = self._generate_caption(figure_type, condition_slug)

        return FigureEntry(
            figure_id=f"fig-{condition_slug}-{figure_type}-{content_hash[:8]}",
            figure_type=figure_type,
            file_path=str(file_path),
            condition_slug=condition_slug,
            content_hash=content_hash,
            caption=caption,
        )

    @staticmethod
    def _compute_file_hash(file_path: Path) -> str:
        """Compute SHA-256 hash of file contents, truncated to 16 hex characters.

        Parameters
        ----------
        file_path:
            Path to the file to hash.

        Returns
        -------
        str
            First 16 characters of the hex-encoded SHA-256 digest.
        """
        sha = hashlib.sha256()
        with open(file_path, "rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                sha.update(chunk)
        return sha.hexdigest()[:16]

    @staticmethod
    def _generate_caption(figure_type: str, condition_slug: str) -> str:
        """Generate a human-readable caption for a figure.

        Parameters
        ----------
        figure_type:
            The figure type key (e.g. ``"brain_map"``).
        condition_slug:
            Condition slug used to derive the display name.

        Returns
        -------
        str
            A formatted caption string.
        """
        condition_display = condition_slug.replace("_", " ").replace("-", " ").title()
        template = _CAPTION_TEMPLATES.get(figure_type)
        if template:
            return template.format(condition=condition_display)
        # Fallback for unknown figure types.
        figure_display = figure_type.replace("_", " ").title()
        return f"{figure_display} for {condition_display}"

    def save_manifest(self, manifest: FigureManifest, output_path: Path) -> Path:
        """Serialise a :class:`FigureManifest` to JSON.

        Parameters
        ----------
        manifest:
            The manifest to save.
        output_path:
            Destination file path.

        Returns
        -------
        Path
            The path the manifest was written to.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(manifest.model_dump(), indent=2, default=str),
            encoding="utf-8",
        )
        logger.info("Saved figure manifest to %s", output_path)
        return output_path

    @staticmethod
    def load_manifest(path: Path) -> FigureManifest:
        """Load a :class:`FigureManifest` from a JSON file.

        Parameters
        ----------
        path:
            Path to the JSON manifest file.

        Returns
        -------
        FigureManifest
            Deserialised manifest.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Manifest file not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        manifest = FigureManifest.model_validate(data)
        logger.info(
            "Loaded figure manifest from %s (%d figures)",
            path,
            len(manifest.figures),
        )
        return manifest
