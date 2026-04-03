"""EEG-driven analysis for protocol target refinement (Layer 3 / V2).

Interprets EEG features to produce:
  - Parameter adjustments (e.g. frequency tuning to individual alpha)
  - Target refinements (lateralisation, region prioritisation)
  - Network dysfunction inferences

This module works with the dict representation of EEGFeatures to stay
loosely coupled from the Pydantic schema layer.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# Standard alpha range for IAF-based adjustments
STANDARD_ALPHA_LOW = 8.0
STANDARD_ALPHA_HIGH = 13.0
STANDARD_IAF = 10.0

# Frontal alpha asymmetry thresholds
FAA_SIGNIFICANT_THRESHOLD = 0.1  # absolute value

# Theta/beta ratio clinical thresholds
TBR_ELEVATED_THRESHOLD = 4.5   # common ADHD cut-off
TBR_HIGH_THRESHOLD = 6.0

# Network keys (mirrors NetworkKey enum values)
NETWORK_LABELS = {
    "dmn": "Default Mode Network",
    "cen": "Central Executive Network",
    "sn": "Salience Network",
    "smn": "Sensorimotor Network",
    "limbic": "Limbic Network",
    "attention": "Attention Network",
}

# Network-to-region mapping for target suggestions
NETWORK_TARGET_MAP: dict[str, list[str]] = {
    "dmn": ["medial PFC", "PCC", "angular gyrus"],
    "cen": ["L-DLPFC", "R-DLPFC", "posterior parietal cortex"],
    "sn": ["anterior insula", "dACC"],
    "smn": ["M1", "SMA", "premotor cortex"],
    "limbic": ["OFC", "amygdala (indirect)", "vmPFC"],
    "attention": ["R-DLPFC", "intraparietal sulcus", "FEF"],
}


@dataclass
class EEGAdjustment:
    """A single parameter adjustment derived from EEG analysis."""

    parameter: str
    original_value: Optional[str]
    adjusted_value: str
    reason: str
    confidence: float


@dataclass
class TargetRefinement:
    """Refined stimulation target based on EEG findings."""

    suggested_target: str
    laterality: str  # left | right | bilateral
    rationale: str
    network_basis: list[str]
    confidence: float


@dataclass
class EEGAnalysisResult:
    """Complete output of the EEG analysis layer."""

    adjustments: list[EEGAdjustment] = field(default_factory=list)
    target_refinement: Optional[TargetRefinement] = None
    network_findings: list[dict] = field(default_factory=list)
    quality_adequate: bool = True
    explanation: str = ""


class EEGAnalyzer:
    """Analyze EEG features to refine stimulation targets and parameters.

    Parameters
    ----------
    min_quality : float
        Minimum EEG quality score (0--1) required to proceed with analysis.
        Below this threshold, EEG adjustments are skipped.
    """

    def __init__(self, min_quality: float = 0.5) -> None:
        self.min_quality = min_quality

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #

    def analyze(
        self,
        eeg_features: dict,
        condition_slug: str,
        current_target: Optional[str] = None,
    ) -> EEGAnalysisResult:
        """Run the full EEG analysis pipeline.

        Parameters
        ----------
        eeg_features : dict
            Dict representation of EEGFeatures (or a raw dict with the
            same keys: ``dominant_frequency``, ``peak_alpha_frequency``,
            ``frontal_alpha_asymmetry``, ``theta_beta_ratio``,
            ``network_dysfunction_map``, ``abnormal_regions``,
            ``suggested_targets``, ``confidence``).
        condition_slug : str
            Target condition for context-aware interpretation.
        current_target : str | None
            Currently selected stimulation target (from earlier layers)
            that may be refined.

        Returns
        -------
        EEGAnalysisResult
        """
        confidence = eeg_features.get("confidence", 0.0)
        if confidence < self.min_quality:
            logger.warning(
                "EEG confidence %.2f below threshold %.2f -- skipping adjustments.",
                confidence, self.min_quality,
            )
            return EEGAnalysisResult(
                quality_adequate=False,
                explanation=(
                    f"EEG data quality ({confidence:.0%}) is below the minimum "
                    f"threshold ({self.min_quality:.0%}). EEG-based adjustments "
                    f"were not applied. Proceed with standard protocol parameters."
                ),
            )

        adjustments: list[EEGAdjustment] = []
        network_findings: list[dict] = []

        # 1. Individual alpha frequency adjustment
        iaf_adj = self._analyze_iaf(eeg_features)
        if iaf_adj:
            adjustments.append(iaf_adj)

        # 2. Frontal alpha asymmetry -> lateralisation
        faa_adj = self._analyze_frontal_asymmetry(eeg_features, condition_slug)
        if faa_adj:
            adjustments.append(faa_adj)

        # 3. Theta/beta ratio
        tbr_adj = self._analyze_theta_beta_ratio(eeg_features, condition_slug)
        if tbr_adj:
            adjustments.append(tbr_adj)

        # 4. Network dysfunction interpretation
        network_findings = self._analyze_network_dysfunction(eeg_features)

        # 5. Target refinement based on integrated findings
        target_refinement = self._compute_target_refinement(
            eeg_features, network_findings, condition_slug, current_target,
        )

        # 6. Build explanation
        explanation = self._build_explanation(
            eeg_features, adjustments, network_findings, target_refinement,
        )

        logger.info(
            "EEG analysis complete: %d adjustments, %d network findings, target=%s",
            len(adjustments),
            len(network_findings),
            target_refinement.suggested_target if target_refinement else "unchanged",
        )

        return EEGAnalysisResult(
            adjustments=adjustments,
            target_refinement=target_refinement,
            network_findings=network_findings,
            quality_adequate=True,
            explanation=explanation,
        )

    # ------------------------------------------------------------------ #
    # IAF analysis                                                        #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _analyze_iaf(eeg: dict) -> Optional[EEGAdjustment]:
        """Adjust stimulation frequency based on individual alpha frequency.

        Standard protocols assume IAF ~ 10 Hz.  Patients with shifted IAF
        benefit from frequency-adjusted parameters (e.g. tACS at individual
        alpha, or tDCS session timing relative to alpha power windows).
        """
        iaf = eeg.get("peak_alpha_frequency")
        if iaf is None:
            return None

        deviation = iaf - STANDARD_IAF

        if abs(deviation) < 0.5:
            # Within normal range, no adjustment needed
            return None

        direction = "slower" if deviation < 0 else "faster"
        return EEGAdjustment(
            parameter="stimulation_frequency_hz",
            original_value=f"{STANDARD_IAF:.1f}",
            adjusted_value=f"{iaf:.1f}",
            reason=(
                f"Individual alpha frequency ({iaf:.1f} Hz) is {abs(deviation):.1f} Hz "
                f"{direction} than standard ({STANDARD_IAF:.1f} Hz). "
                f"Frequency-dependent parameters adjusted to patient IAF."
            ),
            confidence=min(1.0, eeg.get("confidence", 0.5) * 1.2),
        )

    # ------------------------------------------------------------------ #
    # Frontal alpha asymmetry                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _analyze_frontal_asymmetry(
        eeg: dict, condition_slug: str,
    ) -> Optional[EEGAdjustment]:
        """Interpret frontal alpha asymmetry for lateralisation guidance.

        Convention: F4 - F3 alpha power.
        - Negative = left frontal hypoactivation (common in depression)
        - Positive = right frontal hypoactivation
        """
        faa = eeg.get("frontal_alpha_asymmetry")
        if faa is None:
            return None

        if abs(faa) < FAA_SIGNIFICANT_THRESHOLD:
            return None  # Not clinically significant

        if faa < 0:
            # Left frontal hypoactivation
            laterality = "left"
            target_suggestion = "L-DLPFC excitatory / R-DLPFC inhibitory"
            clinical_note = (
                "Left frontal alpha hypoactivation detected (FAA = "
                f"{faa:.3f}). This pattern is commonly associated with "
                "reduced left prefrontal engagement."
            )
            if condition_slug in ("depression", "mdd"):
                clinical_note += (
                    " In depression, this supports excitatory stimulation "
                    "of left DLPFC (standard target for tDCS/rTMS)."
                )
        else:
            laterality = "right"
            target_suggestion = "R-DLPFC modulation"
            clinical_note = (
                f"Right frontal alpha hypoactivation detected (FAA = {faa:.3f}). "
                "Consider right-lateralised targeting strategy."
            )
            if condition_slug in ("anxiety", "gad", "ptsd"):
                clinical_note += (
                    " In anxiety-spectrum conditions, right prefrontal "
                    "dysfunction may warrant inhibitory right DLPFC stimulation."
                )

        return EEGAdjustment(
            parameter="lateralisation",
            original_value="bilateral",
            adjusted_value=f"{laterality} ({target_suggestion})",
            reason=clinical_note,
            confidence=min(1.0, abs(faa) * 5),  # Scale FAA magnitude to confidence
        )

    # ------------------------------------------------------------------ #
    # Theta/beta ratio                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _analyze_theta_beta_ratio(
        eeg: dict, condition_slug: str,
    ) -> Optional[EEGAdjustment]:
        """Interpret theta/beta ratio for attention and arousal assessment.

        Elevated TBR (>4.5) is a biomarker for cortical hypoarousal,
        commonly seen in ADHD but also in other conditions with attentional
        deficits.
        """
        tbr = eeg.get("theta_beta_ratio")
        if tbr is None:
            return None

        if tbr < TBR_ELEVATED_THRESHOLD:
            return None  # Normal range

        severity = "markedly elevated" if tbr >= TBR_HIGH_THRESHOLD else "elevated"
        reason = (
            f"Theta/beta ratio is {severity} ({tbr:.2f}; threshold {TBR_ELEVATED_THRESHOLD}), "
            f"indicating cortical hypoarousal."
        )

        if condition_slug in ("adhd", "attention_deficit"):
            reason += (
                " This supports a hypoarousal phenotype. Consider excitatory "
                "DLPFC stimulation to increase prefrontal beta activity."
            )
            adjusted_value = "increase_beta_target"
        else:
            reason += (
                " Even outside ADHD, elevated TBR may indicate attentional "
                "difficulties. Consider incorporating attentional monitoring."
            )
            adjusted_value = "monitor_attention"

        return EEGAdjustment(
            parameter="arousal_adjustment",
            original_value="standard",
            adjusted_value=adjusted_value,
            reason=reason,
            confidence=min(1.0, (tbr - TBR_ELEVATED_THRESHOLD) / 3.0 + 0.5),
        )

    # ------------------------------------------------------------------ #
    # Network dysfunction                                                 #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _analyze_network_dysfunction(eeg: dict) -> list[dict]:
        """Interpret the network dysfunction map from EEG features.

        Returns a list of findings, each with network key, severity,
        clinical implication, and suggested targets.
        """
        ndm: dict[str, str] = eeg.get("network_dysfunction_map", {})
        findings: list[dict] = []

        for network_key, severity in ndm.items():
            nk = network_key.lower()
            if severity.lower() in ("normal", "none"):
                continue

            network_label = NETWORK_LABELS.get(nk, network_key)
            targets = NETWORK_TARGET_MAP.get(nk, [])

            implication = f"{network_label} shows {severity} dysfunction."
            if nk == "dmn" and severity.lower() in ("moderate", "severe"):
                implication += (
                    " DMN hyperactivation is associated with rumination "
                    "and self-referential processing deficits."
                )
            elif nk == "cen" and severity.lower() in ("moderate", "severe"):
                implication += (
                    " CEN hypoactivation is associated with executive "
                    "function and working memory deficits."
                )
            elif nk == "sn" and severity.lower() in ("moderate", "severe"):
                implication += (
                    " Salience network dysfunction affects appropriate "
                    "switching between DMN and CEN."
                )

            findings.append({
                "network": nk,
                "network_label": network_label,
                "severity": severity,
                "implication": implication,
                "suggested_targets": targets,
            })

        return findings

    # ------------------------------------------------------------------ #
    # Target refinement                                                   #
    # ------------------------------------------------------------------ #

    def _compute_target_refinement(
        self,
        eeg: dict,
        network_findings: list[dict],
        condition_slug: str,
        current_target: Optional[str],
    ) -> Optional[TargetRefinement]:
        """Integrate EEG findings to suggest a refined stimulation target.

        Priority order:
        1. EEG-suggested targets (from the features themselves)
        2. Network dysfunction-based targets (most severe network first)
        3. Asymmetry-guided lateralisation of current target

        Returns None if no refinement is warranted.
        """
        # Use suggested targets from the EEG features if available
        suggested = eeg.get("suggested_targets", [])
        abnormal_regions = eeg.get("abnormal_regions", [])

        # Sort network findings by severity
        severity_order = {"severe": 3, "moderate": 2, "mild": 1}
        sorted_findings = sorted(
            network_findings,
            key=lambda f: severity_order.get(f.get("severity", "mild").lower(), 0),
            reverse=True,
        )

        # Determine laterality from frontal asymmetry
        faa = eeg.get("frontal_alpha_asymmetry", 0.0)
        if faa is not None and abs(faa) >= FAA_SIGNIFICANT_THRESHOLD:
            laterality = "left" if faa < 0 else "right"
        else:
            laterality = "bilateral"

        # Case 1: EEG features already suggest specific targets
        if suggested:
            primary_target = suggested[0]
            network_basis = [f["network"] for f in sorted_findings[:2]] if sorted_findings else []
            return TargetRefinement(
                suggested_target=primary_target,
                laterality=laterality,
                rationale=(
                    f"EEG analysis suggests '{primary_target}' as primary target "
                    f"based on spectral features and network analysis. "
                    f"Abnormal regions: {', '.join(abnormal_regions) if abnormal_regions else 'none identified'}."
                ),
                network_basis=network_basis,
                confidence=eeg.get("confidence", 0.5),
            )

        # Case 2: Derive from most dysfunctional network
        if sorted_findings:
            top_finding = sorted_findings[0]
            top_targets = top_finding.get("suggested_targets", [])
            if top_targets:
                primary_target = top_targets[0]
                # Apply laterality if target is lateralisable
                if laterality != "bilateral" and any(
                    kw in primary_target.lower()
                    for kw in ("dlpfc", "pfc", "m1", "cortex")
                ):
                    primary_target = f"{laterality[0].upper()}-{primary_target}"

                return TargetRefinement(
                    suggested_target=primary_target,
                    laterality=laterality,
                    rationale=(
                        f"Primary target derived from {top_finding['network_label']} "
                        f"dysfunction ({top_finding['severity']}). "
                        f"{top_finding['implication']}"
                    ),
                    network_basis=[top_finding["network"]],
                    confidence=min(
                        0.8,
                        severity_order.get(top_finding["severity"].lower(), 1) * 0.25,
                    ),
                )

        # No refinement warranted
        return None

    # ------------------------------------------------------------------ #
    # Explanation                                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _build_explanation(
        eeg: dict,
        adjustments: list[EEGAdjustment],
        network_findings: list[dict],
        target_refinement: Optional[TargetRefinement],
    ) -> str:
        """Construct a clinical narrative from EEG analysis findings."""
        parts: list[str] = []

        iaf = eeg.get("peak_alpha_frequency")
        if iaf is not None:
            parts.append(f"Individual alpha frequency: {iaf:.1f} Hz.")

        faa = eeg.get("frontal_alpha_asymmetry")
        if faa is not None:
            direction = "left hypoactivation" if faa < 0 else "right hypoactivation"
            parts.append(
                f"Frontal alpha asymmetry: {faa:.3f} ({direction})."
            )

        tbr = eeg.get("theta_beta_ratio")
        if tbr is not None:
            label = "elevated" if tbr >= TBR_ELEVATED_THRESHOLD else "normal"
            parts.append(f"Theta/beta ratio: {tbr:.2f} ({label}).")

        if network_findings:
            nf_summary = "; ".join(
                f"{f['network_label']}: {f['severity']}"
                for f in network_findings
            )
            parts.append(f"Network findings: {nf_summary}.")

        if adjustments:
            adj_summary = "; ".join(a.parameter for a in adjustments)
            parts.append(f"Parameters adjusted: {adj_summary}.")

        if target_refinement:
            parts.append(
                f"Refined target: {target_refinement.suggested_target} "
                f"({target_refinement.laterality})."
            )

        return " ".join(parts) if parts else "No EEG-based adjustments applied."
