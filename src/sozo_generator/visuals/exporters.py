"""
SOZO Brain Center — visuals export coordinator.
Generates all visuals for a condition and returns paths.
"""

import logging
from pathlib import Path

from .brain_maps import BrainMapGenerator
from .network_diagrams import NetworkDiagramGenerator
from .symptom_flow import SymptomFlowGenerator
from .patient_journey import PatientJourneyGenerator
from .legends import LegendGenerator

logger = logging.getLogger(__name__)


class VisualsExporter:
    """
    Coordinates generation of all condition-specific and shared legend visuals.

    Output layout
    -------------
    <output_base_dir>/
        <condition.slug>/
            visuals/
                <slug>_brain_map.png
                <slug>_network_diagram.png
                <slug>_symptom_flow.png
                <slug>_patient_journey.png
        shared/
            evidence_legend.png
            network_legend.png
            confidence_legend.png
    """

    def __init__(self, output_base_dir: Path) -> None:
        self.output_base_dir = Path(output_base_dir)
        self._brain_map_gen   = BrainMapGenerator()
        self._network_gen     = NetworkDiagramGenerator()
        self._flow_gen        = SymptomFlowGenerator()
        self._journey_gen     = PatientJourneyGenerator()
        self._legend_gen      = LegendGenerator()

    # ------------------------------------------------------------------
    # Condition-specific visuals
    # ------------------------------------------------------------------

    def generate_all(self, condition, force: bool = False) -> dict[str, Path | None]:
        """
        Generate all 4 condition-specific visuals.

        Parameters
        ----------
        condition:
            A ConditionSchema instance (or any object with .slug).
        force:
            If False, skip generation when the output file already exists.

        Returns
        -------
        dict with keys: brain_map, network_diagram, symptom_flow, patient_journey.
        Values are Path objects or None on failure / skip.
        """
        slug = condition.slug
        visuals_dir = self.output_base_dir / slug / "visuals"
        visuals_dir.mkdir(parents=True, exist_ok=True)

        results: dict[str, Path | None] = {
            "brain_map":        None,
            "network_diagram":  None,
            "symptom_flow":     None,
            "patient_journey":  None,
        }

        # -- Brain map --
        brain_map_path = visuals_dir / f"{slug}_brain_map.png"
        if force or not brain_map_path.exists():
            try:
                results["brain_map"] = self._brain_map_gen.generate_target_map(condition, visuals_dir)
            except Exception as exc:
                logger.warning("Brain map generation failed for %s: %s", slug, exc)
        else:
            logger.debug("Brain map already exists for %s, skipping.", slug)
            results["brain_map"] = brain_map_path

        # -- Network diagram --
        network_path = visuals_dir / f"{slug}_network_diagram.png"
        if force or not network_path.exists():
            try:
                results["network_diagram"] = self._network_gen.generate_network_diagram(condition, visuals_dir)
            except Exception as exc:
                logger.warning("Network diagram generation failed for %s: %s", slug, exc)
        else:
            logger.debug("Network diagram already exists for %s, skipping.", slug)
            results["network_diagram"] = network_path

        # -- Symptom flow --
        flow_path = visuals_dir / f"{slug}_symptom_flow.png"
        if force or not flow_path.exists():
            try:
                results["symptom_flow"] = self._flow_gen.generate_symptom_flow(condition, visuals_dir)
            except Exception as exc:
                logger.warning("Symptom flow generation failed for %s: %s", slug, exc)
        else:
            logger.debug("Symptom flow already exists for %s, skipping.", slug)
            results["symptom_flow"] = flow_path

        # -- Patient journey --
        journey_path = visuals_dir / f"{slug}_patient_journey.png"
        if force or not journey_path.exists():
            try:
                results["patient_journey"] = self._journey_gen.generate_journey_diagram(slug, visuals_dir)
            except Exception as exc:
                logger.warning("Patient journey generation failed for %s: %s", slug, exc)
        else:
            logger.debug("Patient journey already exists for %s, skipping.", slug)
            results["patient_journey"] = journey_path

        logger.info(
            "generate_all complete for '%s': %s",
            slug,
            {k: str(v) if v else None for k, v in results.items()},
        )
        return results

    # ------------------------------------------------------------------
    # Shared legends
    # ------------------------------------------------------------------

    def generate_shared_legends(self, force: bool = False) -> dict[str, Path | None]:
        """
        Generate the 3 shared legend PNGs into ``output_base_dir / "shared"``.

        Returns
        -------
        dict with keys: evidence_legend, network_legend, confidence_legend.
        """
        shared_dir = self.output_base_dir / "shared"
        shared_dir.mkdir(parents=True, exist_ok=True)

        results: dict[str, Path | None] = {
            "evidence_legend":   None,
            "network_legend":    None,
            "confidence_legend": None,
        }

        targets = [
            ("evidence_legend",   shared_dir / "evidence_legend.png",   self._legend_gen.generate_evidence_legend),
            ("network_legend",    shared_dir / "network_legend.png",     self._legend_gen.generate_network_legend),
            ("confidence_legend", shared_dir / "confidence_legend.png",  self._legend_gen.generate_confidence_legend),
        ]

        for key, expected_path, generator_fn in targets:
            if force or not expected_path.exists():
                try:
                    results[key] = generator_fn(shared_dir)
                except Exception as exc:
                    logger.warning("Legend generation failed for '%s': %s", key, exc)
            else:
                logger.debug("Legend '%s' already exists, skipping.", key)
                results[key] = expected_path

        logger.info(
            "generate_shared_legends complete: %s",
            {k: str(v) if v else None for k, v in results.items()},
        )
        return results
