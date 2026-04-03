"""
Protocol Sequence Builder — creates composable SOZO session protocols
from canonical knowledge objects.

Translates knowledge YAML protocol entries into executable ProtocolSequences
with proper SOZO phase ordering (S-O-Z-O).
"""
from __future__ import annotations

import logging
from typing import Optional

from .models import (
    FilterCoefficients,
    Laterality,
    Modality,
    ProtocolPhase,
    ProtocolSequence,
    ProtocolStep,
    SOZOPhase,
    StepType,
)

logger = logging.getLogger(__name__)

# Modality → SOZO phase mapping
_MODALITY_PHASE = {
    "tavns": SOZOPhase.STABILIZE,
    "ces": SOZOPhase.STABILIZE,
    "tdcs": SOZOPhase.OPTIMIZE,
    "tps": SOZOPhase.ZONE,
}

# Target region → electrode mapping (common patterns)
_TARGET_ELECTRODES = {
    "L-DLPFC": (["F3"], ["Fp2"]),
    "R-DLPFC": (["F4"], ["Fp1"]),
    "DLPFC": (["F3", "F4"], ["Fp1", "Fp2"]),
    "M1": (["C3", "C4"], ["Fp1", "Fp2"]),
    "L-M1": (["C3"], ["Fp2"]),
    "R-M1": (["C4"], ["Fp1"]),
    "SMA": (["FCz"], ["Fp1"]),
    "Cerebellum": (["Cb1", "Cbz", "Cb2"], ["Fpz"]),
    "ACC": (["Fz"], ["Pz"]),
    "OFC": (["Fp1", "Fp2"], ["Pz"]),
    "PPC": (["P3", "P4"], ["Fp1"]),
}


def build_sozo_sequence(
    condition_slug: str,
    tier: str = "fellow",
    knowledge_protocols: list[dict] | None = None,
) -> ProtocolSequence:
    """Build a complete SOZO session sequence from knowledge protocol data.

    If knowledge_protocols is None, loads from the knowledge base.
    Returns a ProtocolSequence with proper S-O-Z-O phase ordering.
    """
    if knowledge_protocols is None:
        knowledge_protocols = _load_protocols_from_knowledge(condition_slug)

    # Sort protocols into SOZO phases
    phase_steps: dict[SOZOPhase, list[ProtocolStep]] = {
        SOZOPhase.PRE: [],
        SOZOPhase.STABILIZE: [],
        SOZOPhase.OPTIMIZE: [],
        SOZOPhase.ZONE: [],
        SOZOPhase.OUTCOME: [],
        SOZOPhase.POST: [],
    }

    for proto in knowledge_protocols:
        modality = proto.get("modality", "")
        step = _protocol_to_step(proto)
        if step:
            phase = _MODALITY_PHASE.get(modality, SOZOPhase.OPTIMIZE)
            phase_steps[phase].append(step)

    # Add standard pre/post monitoring steps
    phase_steps[SOZOPhase.PRE].insert(0, ProtocolStep(
        step_type=StepType.MONITORING,
        modality=Modality.EEG,
        label="Pre-session impedance check",
        duration_min=2.0,
        max_impedance_kohm=5.0,
    ))
    phase_steps[SOZOPhase.POST].append(ProtocolStep(
        step_type=StepType.MONITORING,
        modality=Modality.EEG,
        label="Post-session outcome assessment",
        duration_min=5.0,
    ))

    # Add outcome phase (stabilize modality + rehab tasks)
    if phase_steps[SOZOPhase.STABILIZE]:
        # Copy first stabilize step to outcome phase
        stab_step = phase_steps[SOZOPhase.STABILIZE][0].model_copy()
        stab_step.step_id = f"step-outcome-{stab_step.modality.value}"
        stab_step.label = f"Post-stimulation {stab_step.modality.value} (neuroplasticity window)"
        stab_step.duration_min = 15.0
        phase_steps[SOZOPhase.OUTCOME].append(stab_step)

    # Build phases
    phases = []
    phase_order = [SOZOPhase.PRE, SOZOPhase.STABILIZE, SOZOPhase.OPTIMIZE,
                   SOZOPhase.ZONE, SOZOPhase.OUTCOME, SOZOPhase.POST]

    for sp in phase_order:
        steps = phase_steps[sp]
        if steps:
            phases.append(ProtocolPhase(
                sozo_phase=sp,
                label=_phase_label(sp),
                steps=steps,
            ))

    # Collect evidence PMIDs
    pmids = []
    for proto in knowledge_protocols:
        # Check for evidence references
        if "evidence_pmids" in proto:
            pmids.extend(proto["evidence_pmids"])

    return ProtocolSequence(
        name=f"SOZO Session — {condition_slug}",
        condition_slug=condition_slug,
        tier=tier,
        phases=phases,
        evidence_level="medium",
        evidence_pmids=list(set(pmids)),
    )


def _protocol_to_step(proto: dict) -> Optional[ProtocolStep]:
    """Convert a knowledge protocol entry to a ProtocolStep."""
    modality_str = proto.get("modality", "")
    try:
        modality = Modality(modality_str)
    except ValueError:
        return None

    target = proto.get("target_abbreviation", proto.get("target_region", ""))
    source, sink = _TARGET_ELECTRODES.get(target, ([], []))

    # Extract parameters — safely handle mixed types from YAML
    params = proto.get("parameters", {})
    step = ProtocolStep(
        step_type=StepType.PULSE,
        modality=modality,
        label=proto.get("label", proto.get("protocol_id", "")),
        electrodes_source=proto.get("target_electrodes", source),
        electrodes_sink=sink,
        evidence_level=proto.get("evidence_level", "medium"),
        off_label=proto.get("off_label", True),
        rationale=proto.get("rationale", ""),
    )

    # Modality-specific defaults (safe numeric values)
    if modality == Modality.TDCS:
        step.intensity_ma = _safe_float(params.get("intensity_ma", params.get("intensity")), 2.0)
        step.duration_min = _safe_float(params.get("duration_min", params.get("duration")), 20.0)
        step.ramp_up_ms = _safe_int(params.get("ramp_up_ms"), 30000)
        step.ramp_down_ms = _safe_int(params.get("ramp_down_ms"), 30000)
    elif modality == Modality.TPS:
        step.intensity_mj = _safe_float(params.get("energy_mj", params.get("intensity_mj")), 0.25)
        step.frequency_hz = _safe_float(params.get("frequency_hz"), 5.0)
        step.pulse_count = _safe_int(params.get("pulse_count", params.get("pulses")), 3000)
        step.duration_min = _safe_float(params.get("duration_min"), 20.0)
    elif modality == Modality.TAVNS:
        step.frequency_hz = _safe_float(params.get("frequency_hz"), 25.0)
        step.pulse_width_us = _safe_int(params.get("pulse_width_us"), 250)
        step.intensity_ma = _safe_float(params.get("intensity_ma"), 1.0)
        step.duration_min = 15.0
    elif modality == Modality.CES:
        step.frequency_hz = _safe_float(params.get("frequency_hz"), 0.5)
        step.intensity_ma = _safe_float(params.get("intensity_ua"), 100) / 1000.0
        step.duration_min = 20.0

    return step


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Safely convert a value to float, handling strings like '20-30'."""
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        # Take first number from range strings like "20-30"
        import re
        match = re.match(r"[\d.]+", val)
        if match:
            try:
                return float(match.group())
            except ValueError:
                pass
    return default


def _safe_int(val: Any, default: int = 0) -> int:
    """Safely convert a value to int."""
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, str):
        import re
        match = re.match(r"\d+", val)
        if match:
            try:
                return int(match.group())
            except ValueError:
                pass
    return default


def _phase_label(phase: SOZOPhase) -> str:
    labels = {
        SOZOPhase.PRE: "Pre-Session Preparation",
        SOZOPhase.STABILIZE: "S — Stabilize (downshift sympathetic tone)",
        SOZOPhase.OPTIMIZE: "O — Optimize (prime target networks)",
        SOZOPhase.ZONE: "Z — Zone Target (deep network modulation)",
        SOZOPhase.OUTCOME: "O — Outcome (neuroplasticity window)",
        SOZOPhase.POST: "Post-Session Assessment",
    }
    return labels.get(phase, phase.value)


def _load_protocols_from_knowledge(condition_slug: str) -> list[dict]:
    """Load protocol data from the knowledge base."""
    try:
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        cond = kb.get_condition(condition_slug)
        if cond:
            return [p.model_dump() for p in cond.protocols]
    except Exception as e:
        logger.debug(f"Could not load protocols from KB: {e}")
    return []
