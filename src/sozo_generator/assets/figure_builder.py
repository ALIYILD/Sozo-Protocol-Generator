"""CanonicalFigure builders for the SOZO long-document pipeline.

FigureBuilder creates CanonicalFigure objects and delegates rendering to the
existing visual generators in sozo_generator.visuals.  Every delegation is
wrapped in a try/except so failures are recorded in alt_text rather than
crashing the pipeline.

All 17 visual generators are wired:
  qeeg_topomap         -> generate_qeeg_for_condition
  montage_diagrams     -> MontageDiagramGenerator.generate_montage_diagram
  network_diagrams     -> NetworkDiagramGenerator.generate_network_diagram
  patient_journey      -> PatientJourneyGenerator.generate_journey_diagram
  treatment_timeline   -> generate_timeline_for_condition
  symptom_flow         -> SymptomFlowGenerator.generate_symptom_flow
  connectivity_map     -> generate_connectivity_for_condition
  protocol_panel       -> generate_protocol_panel_for_condition
  brain_maps           -> BrainMapGenerator.generate_target_map
  axial_brain_view     -> generate_axial_for_condition
  spectral_topomap     -> generate_spectral_for_condition
  dose_response        -> generate_dose_response_for_condition
  impedance_map        -> generate_impedance_for_condition
  exporters            -> VisualsExporter.generate_all (batch)
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from sozo_generator.schemas.canonical import CanonicalFigure
from sozo_generator.schemas.condition import ConditionSchema

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Electrode lookup tables
# ---------------------------------------------------------------------------

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
    """Creates CanonicalFigure objects by delegating to existing visual generators.

    All 17 generators in src/sozo_generator/visuals/ are supported.
    All calls are wrapped in try/except -- failures return a CanonicalFigure
    with image_path=None and the error captured in alt_text.
    """

    def __init__(self, output_dir: str = "outputs/assets") -> None:
        self.output_dir = output_dir

    # ------------------------------------------------------------------
    # Core builders
    # ------------------------------------------------------------------

    def build_qeeg_topomap(
        self,
        condition: ConditionSchema,
        variant: str = "fellow",
        output_path: Optional[str] = None,
    ) -> CanonicalFigure:
        """Delegate to generate_qeeg_for_condition."""
        figure_type = "qeeg_topomap"
        title = f"QEEG Topographic Map -- {condition.display_name}"
        if output_path is None:
            output_path = self._build_output_path(
                self._condition_slug(condition), figure_type
            )
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
                    renderer_type=figure_type,
                )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: renderer returned None]",
                renderer_type=figure_type,
            )
        except Exception as exc:
            logger.warning(
                "build_qeeg_topomap failed for %s: %s",
                self._condition_slug(condition),
                exc,
            )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: {exc}]",
                renderer_type=figure_type,
            )

    def build_montage_diagram(
        self,
        condition: ConditionSchema,
        modality: str = "tDCS",
        output_path: Optional[str] = None,
    ) -> CanonicalFigure:
        """Delegate to MontageDiagramGenerator.generate_montage_diagram.

        Selects the first stimulation target matching the requested modality
        to determine anode/cathode placement.
        """
        figure_type = "montage_diagram"
        title = f"Stimulation Montage ({modality.upper()}) -- {condition.display_name}"
        if output_path is None:
            output_path = self._build_output_path(
                self._condition_slug(condition), f"montage_{modality.lower()}"
            )
        try:
            from sozo_generator.visuals.montage_diagrams import MontageDiagramGenerator

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
                    protocol_label = getattr(target, "protocol_label", None) or abbr
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
                    renderer_type=figure_type,
                )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: renderer returned None]",
                renderer_type=figure_type,
            )
        except Exception as exc:
            logger.warning(
                "build_montage_diagram failed for %s: %s",
                self._condition_slug(condition),
                exc,
            )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: {exc}]",
                renderer_type=figure_type,
            )

    def build_network_diagram(
        self,
        condition: ConditionSchema,
        output_path: Optional[str] = None,
    ) -> CanonicalFigure:
        """Delegate to NetworkDiagramGenerator.generate_network_diagram."""
        figure_type = "network_diagram"
        title = f"FNON Network Diagram -- {condition.display_name}"
        if output_path is None:
            output_path = self._build_output_path(
                self._condition_slug(condition), figure_type
            )
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
                    renderer_type=figure_type,
                )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: renderer returned None]",
                renderer_type=figure_type,
            )
        except Exception as exc:
            logger.warning(
                "build_network_diagram failed for %s: %s",
                self._condition_slug(condition),
                exc,
            )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: {exc}]",
                renderer_type=figure_type,
            )

    def build_patient_journey(
        self,
        condition: ConditionSchema,
        output_path: Optional[str] = None,
    ) -> CanonicalFigure:
        """Delegate to PatientJourneyGenerator.generate_journey_diagram."""
        figure_type = "patient_journey"
        title = f"Patient Journey -- {condition.display_name}"
        if output_path is None:
            output_path = self._build_output_path(
                self._condition_slug(condition), figure_type
            )
        try:
            from sozo_generator.visuals.patient_journey import PatientJourneyGenerator

            slug = self._condition_slug(condition)
            output_dir = Path(output_path).parent
            generator = PatientJourneyGenerator()
            result_path = generator.generate_journey_diagram(slug, output_dir)
            if result_path is not None:
                return CanonicalFigure(
                    title=title,
                    image_path=str(result_path),
                    alt_text=(
                        "Eight-stage SOZO patient care pathway diagram: "
                        "Scheduling, Consent, Psych Intake, Clinical Exam, "
                        "Protocol Selection, Treatment Delivery, Response Tracking, "
                        "Maintenance & Discharge."
                    ),
                    renderer_type=figure_type,
                )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: renderer returned None]",
                renderer_type=figure_type,
            )
        except Exception as exc:
            logger.warning(
                "build_patient_journey failed for %s: %s",
                self._condition_slug(condition),
                exc,
            )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: {exc}]",
                renderer_type=figure_type,
            )

    # ------------------------------------------------------------------
    # Extended builders
    # ------------------------------------------------------------------

    def build_treatment_timeline(
        self,
        condition: ConditionSchema,
        protocol_id: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> CanonicalFigure:
        """Delegate to generate_timeline_for_condition."""
        figure_type = "treatment_timeline"
        title = f"SOZO Multimodal Session Timeline -- {condition.display_name}"
        if output_path is None:
            output_path = self._build_output_path(
                self._condition_slug(condition), figure_type
            )
        try:
            from sozo_generator.visuals.treatment_timeline import (
                generate_timeline_for_condition,
            )

            output_dir = Path(output_path).parent
            result_path = generate_timeline_for_condition(condition, output_dir)
            if result_path is not None:
                return CanonicalFigure(
                    title=title,
                    image_path=str(result_path),
                    alt_text=(
                        f"Gantt-style S-O-Z-O multimodal session timeline for "
                        f"{condition.display_name}."
                    ),
                    renderer_type=figure_type,
                )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: renderer returned None]",
                renderer_type=figure_type,
            )
        except Exception as exc:
            logger.warning(
                "build_treatment_timeline failed for %s: %s",
                self._condition_slug(condition),
                exc,
            )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: {exc}]",
                renderer_type=figure_type,
            )

    def build_symptom_flow(
        self,
        condition: ConditionSchema,
        output_path: Optional[str] = None,
    ) -> CanonicalFigure:
        """Delegate to SymptomFlowGenerator.generate_symptom_flow."""
        figure_type = "symptom_flow"
        title = f"Symptom Network Modality Flow -- {condition.display_name}"
        if output_path is None:
            output_path = self._build_output_path(
                self._condition_slug(condition), figure_type
            )
        try:
            from sozo_generator.visuals.symptom_flow import SymptomFlowGenerator

            output_dir = Path(output_path).parent
            generator = SymptomFlowGenerator()
            result_path = generator.generate_symptom_flow(condition, output_dir)
            if result_path is not None:
                return CanonicalFigure(
                    title=title,
                    image_path=str(result_path),
                    alt_text=(
                        f"Three-column flow diagram mapping symptoms to affected "
                        f"networks and treatment modalities for {condition.display_name}."
                    ),
                    renderer_type=figure_type,
                )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: renderer returned None]",
                renderer_type=figure_type,
            )
        except Exception as exc:
            logger.warning(
                "build_symptom_flow failed for %s: %s",
                self._condition_slug(condition),
                exc,
            )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: {exc}]",
                renderer_type=figure_type,
            )

    def build_connectivity_map(
        self,
        condition: ConditionSchema,
        output_path: Optional[str] = None,
    ) -> CanonicalFigure:
        """Delegate to generate_connectivity_for_condition."""
        figure_type = "connectivity_map"
        title = f"FNON Network Connectivity Map -- {condition.display_name}"
        if output_path is None:
            output_path = self._build_output_path(
                self._condition_slug(condition), figure_type
            )
        try:
            from sozo_generator.visuals.connectivity_map import (
                generate_connectivity_for_condition,
            )

            output_dir = Path(output_path).parent
            result_path = generate_connectivity_for_condition(condition, output_dir)
            if result_path is not None:
                return CanonicalFigure(
                    title=title,
                    image_path=str(result_path),
                    alt_text=(
                        f"6x6 inter-network connectivity heatmap showing dysfunction "
                        f"profile for {condition.display_name}."
                    ),
                    renderer_type=figure_type,
                )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: renderer returned None]",
                renderer_type=figure_type,
            )
        except Exception as exc:
            logger.warning(
                "build_connectivity_map failed for %s: %s",
                self._condition_slug(condition),
                exc,
            )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: {exc}]",
                renderer_type=figure_type,
            )

    def build_protocol_panel(
        self,
        condition: ConditionSchema,
        output_path: Optional[str] = None,
    ) -> CanonicalFigure:
        """Delegate to generate_protocol_panel_for_condition.

        Returns a list of Paths (TPS + tDCS panels); the first path is used
        as the primary image_path.
        """
        figure_type = "protocol_panel"
        title = f"Protocol Montage Panel -- {condition.display_name}"
        if output_path is None:
            output_path = self._build_output_path(
                self._condition_slug(condition), figure_type
            )
        try:
            from sozo_generator.visuals.protocol_panel import (
                generate_protocol_panel_for_condition,
            )

            output_dir = Path(output_path).parent
            generated_paths = generate_protocol_panel_for_condition(condition, output_dir)
            if generated_paths:
                primary = generated_paths[0]
                paths_str = ", ".join(str(p) for p in generated_paths)
                return CanonicalFigure(
                    title=title,
                    image_path=str(primary),
                    alt_text=(
                        f"Multi-panel protocol montage grid for {condition.display_name}. "
                        f"Panels: {paths_str}."
                    ),
                    renderer_type=figure_type,
                )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: no protocol data available]",
                renderer_type=figure_type,
            )
        except Exception as exc:
            logger.warning(
                "build_protocol_panel failed for %s: %s",
                self._condition_slug(condition),
                exc,
            )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: {exc}]",
                renderer_type=figure_type,
            )

    def build_brain_map(
        self,
        condition: ConditionSchema,
        view: str = "axial",
        output_path: Optional[str] = None,
    ) -> CanonicalFigure:
        """Delegate to generate_axial_for_condition (view='axial') or
        BrainMapGenerator.generate_target_map (view='topdown'/'coronal').
        """
        figure_type = "brain_map"
        title = f"Brain Target Map ({view}) -- {condition.display_name}"
        if output_path is None:
            output_path = self._build_output_path(
                self._condition_slug(condition), f"brain_map_{view}"
            )
        try:
            output_dir = Path(output_path).parent

            if view == "axial":
                from sozo_generator.visuals.axial_brain_view import (
                    generate_axial_for_condition,
                )

                result_path = generate_axial_for_condition(condition, output_dir)
                alt = (
                    f"Axial (top-down) brain cross-section with color-coded "
                    f"stimulation targets for {condition.display_name}."
                )
            else:
                # topdown / coronal / fallback -> BrainMapGenerator
                from sozo_generator.visuals.brain_maps import BrainMapGenerator

                generator = BrainMapGenerator()
                result_path = generator.generate_target_map(condition, output_dir)
                alt = (
                    f"Top-down brain schematic with stimulation target regions "
                    f"highlighted for {condition.display_name}."
                )

            if result_path is not None:
                return CanonicalFigure(
                    title=title,
                    image_path=str(result_path),
                    alt_text=alt,
                    renderer_type=figure_type,
                )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: renderer returned None]",
                renderer_type=figure_type,
            )
        except Exception as exc:
            logger.warning(
                "build_brain_map failed for %s view=%s: %s",
                self._condition_slug(condition),
                view,
                exc,
            )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: {exc}]",
                renderer_type=figure_type,
            )

    def build_spectral_topomap(
        self,
        condition: ConditionSchema,
        output_path: Optional[str] = None,
    ) -> CanonicalFigure:
        """Delegate to generate_spectral_for_condition."""
        figure_type = "spectral_topomap"
        title = f"EEG Power Spectral Distribution -- {condition.display_name}"
        if output_path is None:
            output_path = self._build_output_path(
                self._condition_slug(condition), figure_type
            )
        try:
            from sozo_generator.visuals.spectral_topomap import (
                generate_spectral_for_condition,
            )

            output_dir = Path(output_path).parent
            result_path = generate_spectral_for_condition(condition, output_dir)
            if result_path is not None:
                return CanonicalFigure(
                    title=title,
                    image_path=str(result_path),
                    alt_text=(
                        f"Five-panel EEG band topographic map (Delta, Theta, Alpha, "
                        f"Beta, Gamma) showing typical spectral profile for "
                        f"{condition.display_name}. Template -- not patient-specific."
                    ),
                    renderer_type=figure_type,
                )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: renderer returned None]",
                renderer_type=figure_type,
            )
        except Exception as exc:
            logger.warning(
                "build_spectral_topomap failed for %s: %s",
                self._condition_slug(condition),
                exc,
            )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: {exc}]",
                renderer_type=figure_type,
            )

    def build_dose_response(
        self,
        condition: ConditionSchema,
        output_path: Optional[str] = None,
    ) -> CanonicalFigure:
        """Delegate to generate_dose_response_for_condition."""
        figure_type = "dose_response"
        title = f"Dose-Response Tracking Template -- {condition.display_name}"
        if output_path is None:
            output_path = self._build_output_path(
                self._condition_slug(condition), figure_type
            )
        try:
            from sozo_generator.visuals.dose_response import (
                generate_dose_response_for_condition,
            )

            output_dir = Path(output_path).parent
            result_path = generate_dose_response_for_condition(condition, output_dir)
            if result_path is not None:
                return CanonicalFigure(
                    title=title,
                    image_path=str(result_path),
                    alt_text=(
                        f"Dose-response tracking chart template for {condition.display_name}. "
                        "Shows responder/partial/non-responder zones across 12 sessions."
                    ),
                    renderer_type=figure_type,
                )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: renderer returned None]",
                renderer_type=figure_type,
            )
        except Exception as exc:
            logger.warning(
                "build_dose_response failed for %s: %s",
                self._condition_slug(condition),
                exc,
            )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: {exc}]",
                renderer_type=figure_type,
            )

    def build_impedance_map(
        self,
        condition: ConditionSchema,
        output_path: Optional[str] = None,
    ) -> CanonicalFigure:
        """Delegate to generate_impedance_for_condition."""
        figure_type = "impedance_map"
        title = f"Electrode Impedance Map -- {condition.display_name}"
        if output_path is None:
            output_path = self._build_output_path(
                self._condition_slug(condition), figure_type
            )
        try:
            from sozo_generator.visuals.impedance_map import (
                generate_impedance_for_condition,
            )

            output_dir = Path(output_path).parent
            result_path = generate_impedance_for_condition(condition, output_dir)
            if result_path is not None:
                return CanonicalFigure(
                    title=title,
                    image_path=str(result_path),
                    alt_text=(
                        f"Head map showing electrode impedance quality check for "
                        f"{condition.display_name} session. Green = good (<5 kOhm), "
                        "yellow = marginal, red = poor."
                    ),
                    renderer_type=figure_type,
                )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: renderer returned None]",
                renderer_type=figure_type,
            )
        except Exception as exc:
            logger.warning(
                "build_impedance_map failed for %s: %s",
                self._condition_slug(condition),
                exc,
            )
            return CanonicalFigure(
                title=title,
                image_path=None,
                alt_text=f"[{figure_type} not rendered: {exc}]",
                renderer_type=figure_type,
            )

    # ------------------------------------------------------------------
    # Batch builder
    # ------------------------------------------------------------------

    def build_all_for_condition(
        self,
        condition: ConditionSchema,
        variant: str = "partners",
        output_dir: Optional[str] = None,
    ) -> list[CanonicalFigure]:
        """Build all available figures for a condition.

        First attempts to use VisualsExporter.generate_all() for the four
        core visuals (brain_map, network_diagram, symptom_flow,
        patient_journey).  Then calls each individual builder for the
        remaining generators.  Failures are silently captured as
        CanonicalFigure objects with image_path=None.

        Returns a list of CanonicalFigure objects (some may have
        image_path=None if the renderer failed).
        """
        slug = self._condition_slug(condition)
        effective_dir = output_dir or str(Path(self.output_dir) / slug)
        self._ensure_output_dir(effective_dir)

        figures: list[CanonicalFigure] = []
        exporter_paths: dict[str, object] = {}

        # -- Try VisualsExporter batch first for the 4 core visuals --
        try:
            from sozo_generator.visuals.exporters import VisualsExporter

            exporter = VisualsExporter(output_base_dir=effective_dir)
            exporter_paths = exporter.generate_all(condition, force=False)
            logger.info("VisualsExporter.generate_all succeeded for %s", slug)
        except Exception as exc:
            logger.warning(
                "VisualsExporter.generate_all failed for %s (%s); "
                "falling back to individual builders.",
                slug,
                exc,
            )

        # -- Brain map --
        bp = exporter_paths.get("brain_map")
        if bp is not None:
            figures.append(
                CanonicalFigure(
                    title=f"Brain Target Map -- {condition.display_name}",
                    image_path=str(bp),
                    alt_text=f"Brain target map for {condition.display_name}.",
                    renderer_type="brain_map",
                )
            )
        else:
            figures.append(
                self.build_brain_map(
                    condition,
                    view="axial",
                    output_path=str(Path(effective_dir) / f"{slug}_brain_map.png"),
                )
            )

        # -- Network diagram --
        np_ = exporter_paths.get("network_diagram")
        if np_ is not None:
            figures.append(
                CanonicalFigure(
                    title=f"FNON Network Diagram -- {condition.display_name}",
                    image_path=str(np_),
                    alt_text=f"FNON network diagram for {condition.display_name}.",
                    renderer_type="network_diagram",
                )
            )
        else:
            figures.append(
                self.build_network_diagram(
                    condition,
                    output_path=str(
                        Path(effective_dir) / f"{slug}_network_diagram.png"
                    ),
                )
            )

        # -- Symptom flow --
        sf = exporter_paths.get("symptom_flow")
        if sf is not None:
            figures.append(
                CanonicalFigure(
                    title=f"Symptom Flow -- {condition.display_name}",
                    image_path=str(sf),
                    alt_text=f"Symptom flow diagram for {condition.display_name}.",
                    renderer_type="symptom_flow",
                )
            )
        else:
            figures.append(
                self.build_symptom_flow(
                    condition,
                    output_path=str(
                        Path(effective_dir) / f"{slug}_symptom_flow.png"
                    ),
                )
            )

        # -- Patient journey --
        pj = exporter_paths.get("patient_journey")
        if pj is not None:
            figures.append(
                CanonicalFigure(
                    title=f"Patient Journey -- {condition.display_name}",
                    image_path=str(pj),
                    alt_text="Eight-stage SOZO patient care pathway.",
                    renderer_type="patient_journey",
                )
            )
        else:
            figures.append(
                self.build_patient_journey(
                    condition,
                    output_path=str(
                        Path(effective_dir) / f"{slug}_patient_journey.png"
                    ),
                )
            )

        # -- Remaining individual builders --
        figures.append(
            self.build_qeeg_topomap(
                condition,
                variant=variant,
                output_path=str(Path(effective_dir) / f"{slug}_qeeg_topomap.png"),
            )
        )
        figures.append(
            self.build_montage_diagram(
                condition,
                output_path=str(Path(effective_dir) / f"{slug}_montage_tdcs.png"),
            )
        )
        figures.append(
            self.build_treatment_timeline(
                condition,
                output_path=str(
                    Path(effective_dir) / f"{slug}_treatment_timeline.png"
                ),
            )
        )
        figures.append(
            self.build_connectivity_map(
                condition,
                output_path=str(
                    Path(effective_dir) / f"{slug}_connectivity_map.png"
                ),
            )
        )
        figures.append(
            self.build_protocol_panel(
                condition,
                output_path=str(
                    Path(effective_dir) / f"{slug}_protocol_panel.png"
                ),
            )
        )
        figures.append(
            self.build_spectral_topomap(
                condition,
                output_path=str(
                    Path(effective_dir) / f"{slug}_spectral_topomap.png"
                ),
            )
        )
        figures.append(
            self.build_dose_response(
                condition,
                output_path=str(Path(effective_dir) / f"{slug}_dose_response.png"),
            )
        )
        figures.append(
            self.build_impedance_map(
                condition,
                output_path=str(
                    Path(effective_dir) / f"{slug}_impedance_map.png"
                ),
            )
        )

        generated = sum(1 for f in figures if f.image_path is not None)
        logger.info(
            "build_all_for_condition '%s': %d/%d figures generated",
            slug,
            generated,
            len(figures),
        )
        return figures

    # ------------------------------------------------------------------
    # Registry integration
    # ------------------------------------------------------------------

    def build_and_register(
        self,
        figure_type: str,
        condition: ConditionSchema,
        asset_registry,
        section_target: str,
        variant: str = "partners",
        **kwargs,
    ) -> tuple[CanonicalFigure, str]:
        """Build a figure AND register/update it in the asset registry.

        Steps:
          1. build_by_type() to render the figure.
          2. asset_registry.register() to create a pending record.
          3. asset_registry.update_status() to 'generated' or 'failed'.

        Returns:
            (CanonicalFigure, asset_id)
        """
        figure = self.build_by_type(
            figure_type=figure_type,
            condition=condition,
            variant=variant,
            **kwargs,
        )

        slug = self._condition_slug(condition)
        record = asset_registry.register(
            asset_type="figure",
            condition_slug=slug,
            section_target=section_target,
            renderer_type=figure_type,
            source_data={"figure_type": figure_type},
            caption=figure.title,
            variant_tags=[variant],
        )
        asset_id = record.asset_id

        if figure.image_path is not None:
            asset_registry.update_status(
                asset_id, "generated", output_path=figure.image_path
            )
        else:
            asset_registry.update_status(asset_id, "failed")

        return figure, asset_id

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    def build_by_type(
        self,
        figure_type: str,
        condition: ConditionSchema,
        variant: str = "partners",
        output_path: Optional[str] = None,
        **kwargs,
    ) -> CanonicalFigure:
        """Dispatch to the right build method by figure_type string.

        Supported types:
            "qeeg_topomap", "montage_diagram", "network_diagram",
            "patient_journey", "treatment_timeline", "symptom_flow",
            "connectivity_map", "protocol_panel",
            "brain_map", "brain_map_axial", "brain_map_coronal",
            "brain_map_topdown", "spectral_topomap", "dose_response",
            "impedance_map", "static_image"
        """
        ft = figure_type.lower().replace("-", "_")

        if ft == "qeeg_topomap":
            return self.build_qeeg_topomap(
                condition, variant=variant, output_path=output_path
            )
        if ft == "montage_diagram":
            modality = kwargs.get("modality", "tDCS")
            return self.build_montage_diagram(
                condition, modality=modality, output_path=output_path
            )
        if ft == "network_diagram":
            return self.build_network_diagram(condition, output_path=output_path)

        if ft == "patient_journey":
            return self.build_patient_journey(condition, output_path=output_path)

        if ft == "treatment_timeline":
            protocol_id = kwargs.get("protocol_id")
            return self.build_treatment_timeline(
                condition, protocol_id=protocol_id, output_path=output_path
            )
        if ft == "symptom_flow":
            return self.build_symptom_flow(condition, output_path=output_path)

        if ft == "connectivity_map":
            return self.build_connectivity_map(condition, output_path=output_path)

        if ft == "protocol_panel":
            return self.build_protocol_panel(condition, output_path=output_path)

        if ft in ("brain_map", "brain_map_axial"):
            return self.build_brain_map(
                condition, view="axial", output_path=output_path
            )
        if ft == "brain_map_coronal":
            return self.build_brain_map(
                condition, view="coronal", output_path=output_path
            )
        if ft == "brain_map_topdown":
            return self.build_brain_map(
                condition, view="topdown", output_path=output_path
            )
        if ft == "spectral_topomap":
            return self.build_spectral_topomap(condition, output_path=output_path)

        if ft == "dose_response":
            return self.build_dose_response(condition, output_path=output_path)

        if ft == "impedance_map":
            return self.build_impedance_map(condition, output_path=output_path)

        if ft == "static_image":
            img = kwargs.get("image_path") or output_path or ""
            title_kw = kwargs.get("title", "Static Image")
            alt = kwargs.get("alt_text", "")
            return self.build_from_existing_path(img, title_kw, alt)

        # Unknown type
        logger.warning("build_by_type: unknown figure_type %r", figure_type)
        return CanonicalFigure(
            title=f"[Unknown figure type: {figure_type}]",
            image_path=None,
            alt_text=f"[{figure_type} not rendered: unknown figure type]",
            renderer_type=figure_type,
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
            image_path=image_path if image_path else None,
            alt_text=alt_text or f"Image: {title}",
            renderer_type=None,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_output_path(self, condition_slug: str, figure_type: str) -> str:
        """Build a deterministic output path for a figure asset."""
        directory = Path(self.output_dir) / condition_slug
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{condition_slug}_{figure_type}.png"
        return str(directory / filename)

    def _ensure_output_dir(self, path: str) -> str:
        """Create directory at path if it does not exist. Returns path."""
        Path(path).mkdir(parents=True, exist_ok=True)
        return path

    def _condition_slug(self, condition) -> str:
        """Return condition slug whether condition is a str or ConditionSchema."""
        if isinstance(condition, str):
            return condition
        return getattr(condition, "slug", str(condition))
