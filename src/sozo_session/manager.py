"""
SOZO Session Manager — orchestrates treatment delivery through the device layer.

This is the core runtime orchestrator that:
1. Validates the protocol against device capabilities
2. Runs pre-session safety checks (impedance)
3. Executes each phase and step through device adapters
4. Monitors for adverse events
5. Records audit trail and outcomes
6. Handles emergency stop

Usage:
    from sozo_session.manager import SessionManager
    from sozo_protocol.models import ProtocolSequence
    from sozo_device.registry import DeviceAdapterRegistry

    mgr = SessionManager()
    result = await mgr.run_session("patient-001", protocol_sequence)
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from sozo_protocol.models import ProtocolSequence, ProtocolStep, Modality
from sozo_device.registry import DeviceAdapterRegistry
from sozo_device.adapters.base import DeviceAdapter, DeviceState, StepResult
from sozo_device.streaming.event_bus import SessionEventBus, SessionEvent, EventChannel

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Session State ────────────────────────────────────────────────────────


class SessionStatus:
    CREATED = "created"
    PRE_CHECK = "pre_check"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABORTED = "aborted"
    ERROR = "error"


@dataclass
class SessionState:
    """Per-session state container (like OMNI-BIC's BICDeviceInfoStruct)."""
    session_id: str = ""
    patient_id: str = ""
    clinician_id: str = ""
    status: str = SessionStatus.CREATED
    protocol_name: str = ""
    condition: str = ""
    tier: str = ""
    started_at: str = ""
    completed_at: str = ""
    current_phase: str = ""
    current_step: str = ""
    steps_completed: int = 0
    steps_total: int = 0
    adverse_events: list[str] = field(default_factory=list)
    audit_log: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if not self.session_id:
            self.session_id = f"sess-{uuid.uuid4().hex[:8]}"

    def log(self, event_type: str, detail: str = "", **kwargs):
        self.audit_log.append({
            "timestamp": _now(),
            "event": event_type,
            "detail": detail,
            "phase": self.current_phase,
            "step": self.current_step,
            **kwargs,
        })


@dataclass
class SessionResult:
    """Result of a completed session."""
    session_id: str = ""
    patient_id: str = ""
    status: str = ""
    started_at: str = ""
    completed_at: str = ""
    duration_min: float = 0.0
    steps_completed: int = 0
    steps_total: int = 0
    step_results: list[StepResult] = field(default_factory=list)
    adverse_events: list[str] = field(default_factory=list)
    impedance_pre: dict[str, float] = field(default_factory=dict)
    impedance_post: dict[str, float] = field(default_factory=dict)
    audit_log: list[dict] = field(default_factory=list)
    error: str = ""

    @property
    def success(self) -> bool:
        return self.status == SessionStatus.COMPLETED and not self.error


# ── Safety Monitor ───────────────────────────────────────────────────────


class SafetyMonitor:
    """Real-time safety monitor for stimulation sessions."""

    def __init__(self, max_impedance_kohm: float = 10.0):
        self.max_impedance = max_impedance_kohm
        self.adverse_events: list[str] = []

    def check_impedance(self, impedance: dict[str, float]) -> bool:
        """Check if all electrode impedances are within safe limits."""
        for electrode, value in impedance.items():
            if value > self.max_impedance:
                self.adverse_events.append(
                    f"High impedance on {electrode}: {value} kΩ (max: {self.max_impedance})"
                )
                return False
        return True

    def check_step_result(self, result: StepResult) -> bool:
        """Check if a step result indicates a safety issue."""
        if result.adverse_events:
            self.adverse_events.extend(result.adverse_events)
            return False
        return True

    def is_safe(self) -> bool:
        return len(self.adverse_events) == 0


# ── Session Manager ──────────────────────────────────────────────────────


class SessionManager:
    """Orchestrates SOZO treatment sessions through the device layer."""

    def __init__(self):
        self.device_registry = DeviceAdapterRegistry()
        self.event_bus = SessionEventBus()
        self.safety = SafetyMonitor()
        self._active_session: Optional[SessionState] = None

    async def run_session(
        self,
        patient_id: str,
        protocol: ProtocolSequence,
        clinician_id: str = "",
        use_simulator: bool = True,
    ) -> SessionResult:
        """Execute a complete treatment session.

        Args:
            patient_id: Patient identifier
            protocol: The protocol sequence to execute
            clinician_id: Supervising clinician
            use_simulator: If True, use simulator adapters (no real hardware)
        """
        state = SessionState(
            patient_id=patient_id,
            clinician_id=clinician_id,
            protocol_name=protocol.name,
            condition=protocol.condition_slug,
            tier=protocol.tier,
            steps_total=len(protocol.all_steps),
        )
        self._active_session = state
        result = SessionResult(
            session_id=state.session_id,
            patient_id=patient_id,
            steps_total=state.steps_total,
        )

        try:
            state.status = SessionStatus.PRE_CHECK
            state.started_at = _now()
            result.started_at = state.started_at
            state.log("session_start", f"Protocol: {protocol.name}")

            await self.event_bus.publish(SessionEvent(
                channel=EventChannel.AUDIT,
                event_type="session_start",
                session_id=state.session_id,
                data={"patient_id": patient_id, "protocol": protocol.name},
            ))

            # 1. Create device adapters for each modality
            adapters = {}
            for modality in protocol.all_modalities:
                if modality == "none":
                    continue
                device_type = "simulator" if use_simulator else None
                adapter = self.device_registry.create(
                    device_type or modality, device_id=f"{modality}-{state.session_id[:8]}"
                )
                await adapter.connect()
                adapters[modality] = adapter
                state.log("device_connected", f"Modality: {modality}, Device: {adapter.device_id}")

            # 2. Validate protocol against device capabilities
            for step in protocol.all_steps:
                if step.modality.value in adapters:
                    violations = adapters[step.modality.value].validate_step(step)
                    if violations:
                        state.log("validation_fail", f"Step {step.step_id}: {violations}")
                        result.error = f"Validation failed: {'; '.join(violations)}"
                        result.status = SessionStatus.ERROR
                        return result

            # 3. Pre-session impedance check
            for mod, adapter in adapters.items():
                caps = adapter.get_capabilities()
                if caps.supports_impedance:
                    impedance = await adapter.get_impedance()
                    result.impedance_pre.update(impedance)
                    if not self.safety.check_impedance(impedance):
                        state.log("impedance_fail", f"Modality: {mod}")
                        await self.event_bus.publish(SessionEvent(
                            channel=EventChannel.SAFETY,
                            event_type="impedance_fail",
                            session_id=state.session_id,
                            severity="critical",
                        ))
                        result.error = f"Impedance check failed: {self.safety.adverse_events}"
                        result.status = SessionStatus.ABORTED
                        return result

            # 4. Execute phases and steps
            state.status = SessionStatus.RUNNING
            for phase in protocol.phases:
                state.current_phase = phase.sozo_phase.value
                state.log("phase_start", f"Phase: {phase.label}")

                for step in phase.steps:
                    state.current_step = step.step_id

                    # Get adapter for this step's modality
                    adapter = adapters.get(step.modality.value)
                    if not adapter and step.modality != Modality.NONE:
                        state.log("skip_step", f"No adapter for {step.modality.value}")
                        continue

                    # Execute step
                    state.log("step_start", f"Step: {step.label} ({step.modality.value})")
                    await self.event_bus.publish(SessionEvent(
                        channel=EventChannel.STIMULATION,
                        event_type="step_start",
                        session_id=state.session_id,
                        data={"step_id": step.step_id, "modality": step.modality.value},
                    ))

                    if adapter:
                        step_result = await adapter.execute_step(step)
                    else:
                        # Pause/monitoring step without hardware
                        if step.duration_total_ms > 0:
                            await asyncio.sleep(min(step.duration_total_ms / 1000.0, 0.1))
                        step_result = StepResult(step_id=step.step_id, success=True)

                    result.step_results.append(step_result)

                    # Safety check after step
                    if not self.safety.check_step_result(step_result):
                        state.log("safety_alert", f"Step {step.step_id}: {step_result.adverse_events}")
                        await self._emergency_stop_all(adapters)
                        result.adverse_events = self.safety.adverse_events
                        result.status = SessionStatus.ABORTED
                        return result

                    state.steps_completed += 1
                    state.log("step_complete", f"Step: {step.label}")

                state.log("phase_complete", f"Phase: {phase.label}")

            # 5. Post-session impedance
            for mod, adapter in adapters.items():
                caps = adapter.get_capabilities()
                if caps.supports_impedance:
                    impedance = await adapter.get_impedance()
                    result.impedance_post.update(impedance)

            # 6. Disconnect
            for adapter in adapters.values():
                await adapter.disconnect()

            state.status = SessionStatus.COMPLETED
            state.completed_at = _now()
            state.log("session_complete")

            result.status = SessionStatus.COMPLETED
            result.completed_at = state.completed_at
            result.steps_completed = state.steps_completed
            result.audit_log = state.audit_log

            # Calculate duration
            if result.started_at and result.completed_at:
                from datetime import datetime as dt
                start = dt.fromisoformat(result.started_at.replace("Z", "+00:00"))
                end = dt.fromisoformat(result.completed_at.replace("Z", "+00:00"))
                result.duration_min = (end - start).total_seconds() / 60.0

        except Exception as e:
            state.status = SessionStatus.ERROR
            state.log("session_error", str(e))
            result.status = SessionStatus.ERROR
            result.error = str(e)
            logger.error(f"Session error: {e}", exc_info=True)

        finally:
            self._active_session = None
            await self.event_bus.publish(SessionEvent(
                channel=EventChannel.AUDIT,
                event_type="session_end",
                session_id=state.session_id,
                data={"status": result.status},
            ))

        return result

    async def _emergency_stop_all(self, adapters: dict[str, DeviceAdapter]):
        """Emergency stop all connected devices."""
        for adapter in adapters.values():
            try:
                await adapter.emergency_stop()
            except Exception as e:
                logger.error(f"Emergency stop failed on {adapter.device_id}: {e}")

        await self.event_bus.publish(SessionEvent(
            channel=EventChannel.SAFETY,
            event_type="emergency_stop",
            severity="critical",
        ))
