"""CanonicalFigure builders for the SOZO long-document pipeline.

FigureBuilder creates CanonicalFigure objects and delegates rendering to the
existing visual generators in sozo_generator.visuals.  Every delegation is
wrapped in a try/except so failures are recorded in alt_text rather than
crashing the pipeline.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from sozo_generator.schemas.canonical import CanonicalFigure
from sozo_generator.schemas.condition import ConditionSchema

logger = logging.getLogger(__name__)

# Target abbreviation → common electrode mapping used for QEEG
_ABBR_TO_ELECTRODE: dict[str, str] = {
    "L-DLPFC": "F3",
    "R-DLPFC": "F4",
    "DLPFC": "F3",
    "L-M1": "C3",
    "R-M1": "C4",
    "M1": "C3",
    "SMA": "FCz",
    "CEREBELLUM": "Cbz",
    "CB": "Cbz",
    "ACC": "Fz",
    "MPFC": "Fz",
    "OFC": "Fp1",
    "PPC": "P3",
    "L-PPC": "P3",
    "R-PPC": "P4",
    "L-STG": "T5",
    "R-STG": "T6",
    "TPJ": "P3",
    "INSULA": "FC5",
    "A-INSULA": "FC5",
}

# Target abbreviation → (anode_electrode, cathode_electrode) for tDCS montage
_TARGET_TO_ANODE_CATHODE: dict[str, tuple[str, str]] = {
    "L-DLPFC": ("F3", "Fp2"),
    "R-DLPFC": ("F4", "Fp1"),
    "DLPFC": ("F3", "Fp2"),
    "L-M1": ("C3", "C4"),
    "R-M1": ("C4", "C3"),
    "M1": ("C3", "Fp2"),
    "SMA": ("Fz", "Pz"),
    "ACC": ("Fz", "Cz"),
    "MPFC": ("Fz", "Pz"),
    "OFC": ("Fp1", "Fp2"),
    "INSULA": ("FC5", "FC6"),
}


class FigureBuilder:
    """Creates CanonicalFigure objects and delegates rendering to existing
    visual generators in sozo_generator.visuals.
    """

    def __init__(self, output_dir: str = "outputs/assets") -> None:
        self.output_dir = output_dir

    # ------------------------------------------------------------------
    # QEEG topomap
    # ------------------------------------------------------------------

    def build_qeeg_topomap(
        self,
        condition: ConditionSchema,
        variant: str = "fellow",
        output_path: Optional[str] = None,
    ) -> CanonicalFigure:
        """Delegate to sozo_generator.visuals.qeeg_topomap.

        Returns CanonicalFigure with output_path set, or with image_path=None
        and error noted in alt_text if the generator fails.
        """
        title = f"QEEG Topographic Map — {condition.display_name}"
        if output_path is None:
            output_path = self._build_output_path(condition.slug, "qeeg_topomap")

        try:
            from sozo_generator.visuals.qeeg_topomap import generate_qeeg_for_condition

            result_path = generate_qeeg_for_condition(condition, Path(output_path).parent)
            if result_path is not None:
                return CanonicalFigure(
                    title=title,
                    image_path=str(result_path),
                    alt_text=(
                        f"QEEG topographic brain map showing stimulation targets "
                        f"for {condition.display_name}."
                    ),
                    renderer_type="qeeg_topomap",
                )
            else:
                return CanonicalFigure(
                    title=title,
                    image_path=None,
                    alt_text=(
                        f"QEEG topomap could not be generated for {condition.display_name}: "
                        "renderer returned None."
                    ),
                    renderer_type="qeeg_topomap",
                )
        except Exception as exc:
            logger.warning("build_qeeg_topomap failed for %s: %s", condition.slug, exc)
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=(
                    f"QEEG topomap unavailable for {condition.display_name}: {exc}"
                ),
                renderer_type="qeeg_topomap",
            )

    # ------------------------------------------------------------------
    # Montage diagram
    # ------------------------------------------------------------------

    def build_montage_diagram(
        self,
        condition: ConditionSchema,
        modality: str = "tDCS",
        output_path: Optional[str] = None,
    ) -> CanonicalFigure:
        """Delegate to sozo_generator.visuals.montage_diagrams.

        Selects the first stimulation target matching the requested modality
        to determine anode/cathode placement.
        """
        title = f"Stimulation Montage ({modality.upper()}) — {condition.display_name}"
        if output_path is None:
            output_path = self._build_output_path(
                condition.slug, f"montage_{modality.lower()}"
            )

        try:
            from sozo_generator.visuals.montage_diagrams import MontageDiagramGenerator

            # Find the best matching target for the requested modality
            anode = "F3"
            cathode = "Fp2"
            protocol_label = ""

            for target in condition.stimulation_targets:
                mod_val = (
                    target.modality.value
                    if hasattr(target.modality, "value")
                    else str(target.modality)
                )
                if mod_val.lower() == modality.lower():
                    abbr = target.target_abbreviation.upper()
                    pair = _TARGET_TO_ANODE_CATHODE.get(abbr)
                    if pair:
                        anode, cathode = pair
                    protocol_label = target.protocol_label or abbr
                    break

            output_dir = Path(output_path).parent
            filename = Path(output_path).name
            generator = MontageDiagramGenerator()
            result_path = generator.generate_montage_diagram(
                anode=anode,
                cathode=cathode,
                condition_name=condition.display_name,
                protocol_label=protocol_label,
                modality=modality.upper(),
                output_dir=output_dir,
                filename=filename,
            )

            if result_path is not None:
                return CanonicalFigure(
                    title=title,
                    image_path=str(result_path),
                    alt_text=(
                        f"{modality.upper()} montage diagram for {condition.display_name}. "
                        f"Anode: {anode}, Cathode: {cathode}."
                    ),
                    renderer_type="montage_diagram",
                )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=(
                    f"Montage diagram renderer returned None for {condition.display_name}."
                ),
                renderer_type="montage_diagram",
            )
        except Exception as exc:
            logger.warning("build_montage_diagram failed for %s: %s", condition.slug, exc)
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=(
                    f"Montage diagram unavailable for {condition.display_name}: {exc}"
                ),
                renderer_type="montage_diagram",
            )

    # ------------------------------------------------------------------
    # Network diagram
    # ------------------------------------------------------------------

    def build_network_diagram(
        self,
        condition: ConditionSchema,
        output_path: Optional[str] = None,
    ) -> CanonicalFigure:
        """Delegate to sozo_generator.visuals.network_diagrams."""
        title = f"FNON Network Diagram — {condition.display_name}"
        if output_path is None:
            output_path = self._build_output_path(condition.slug, "network_diagram")

        try:
            from sozo_generator.visuals.network_diagrams import NetworkDiagramGenerator

            output_dir = Path(output_path).parent
            generator = NetworkDiagramGenerator()
            result_path = generator.generate_network_diagram(condition, output_dir)

            if result_path is not None:
                return CanonicalFigure(
                    title=title,
                    image_path=str(result_path),
                    alt_text=(
                        f"Hexagon diagram showing the six FNON network involvement "
                        f"profile for {condition.display_name}."
                    ),
                    renderer_type="network_diagram",
                )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=(
                    f"Network diagram renderer returned None for {condition.display_name}."
                ),
                renderer_type="network_diagram",
            )
        except Exception as exc:
            logger.warning("build_network_diagram failed for %s: %s", condition.slug, exc)
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=(
                    f"Network diagram unavailable for {condition.display_name}: {exc}"
                ),
                renderer_type="network_diagram",
            )

    # ------------------------------------------------------------------
    # Patient journey
    # ------------------------------------------------------------------

    def build_patient_journey(
        self,
        condition: ConditionSchema,
        output_path: Optional[str] = None,
    ) -> CanonicalFigure:
        """Delegate to sozo_generator.visuals.patient_journey."""
        title = f"Patient Journey — {condition.display_name}"
        if output_path is None:
            output_path = self._build_output_path(condition.slug, "patient_journey")

        try:
            from sozo_generator.visuals.patient_journey import PatientJourneyGenerator

            output_dir = Path(output_path).parent
            generator = PatientJourneyGenerator()
            result_path = generator.generate_journey_diagram(condition.slug, output_dir)

            if result_path is not None:
                return CanonicalFigure(
                    title=title,
                    image_path=str(result_path),
                    alt_text=(
                        "Eight-stage SOZO patient care pathway diagram: "
                        "Scheduling → Intake → Consent → Clinical Exam → "
                        "Protocol Selection → Treatment → Response Tracking → "
                        "Maintenance & Discharge."
                    ),
                    renderer_type="patient_journey",
                )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=(
                    f"Patient journey diagram renderer returned None for {condition.display_name}."
                ),
                renderer_type="patient_journey",
            )
        except Exception as exc:
            logger.warning("build_patient_journey failed for %s: %s", condition.slug, exc)
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=(
                    f"Patient journey diagram unavailable for {condition.display_name}: {exc}"
                ),
                renderer_type="patient_journey",
            )

    # ------------------------------------------------------------------
    # Wrap an existing image
    # ------------------------------------------------------------------

    def build_from_existing_path(
        self,
        image_path: str,
        title: str,
        alt_text: str = "",
    ) -> CanonicalFigure:
        """Wrap an existing PNG (or any image) as a CanonicalFigure."""
        return CanonicalFigure(
            title=title,
            image_path=image_path,
            alt_text=alt_text or f"Image: {title}",
            renderer_type=None,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_output_path(self, condition_slug: str, figure_type: str) -> str:
        """Build a deterministic output path for a figure asset."""
        directory = Path(self.output_dir)
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{condition_slug}_{figure_type}.png"
        return str(directory / filename)
