"""Tests for the composable protocol engine, device adapters, and session manager."""
import asyncio
import pytest


# ── Protocol Model Tests ─────────────────────────────────────────────────


class TestProtocolModels:
    def test_protocol_step_creation(self):
        from sozo_protocol.models import ProtocolStep, StepType, Modality
        step = ProtocolStep(
            step_type=StepType.PULSE,
            modality=Modality.TDCS,
            label="Motor cortex tDCS",
            electrodes_source=["C3", "C4"],
            electrodes_sink=["Fp1", "Fp2"],
            intensity_ma=2.0,
            duration_min=20.0,
        )
        assert step.step_id.startswith("step-")
        assert step.modality == Modality.TDCS
        assert step.intensity_ma == 2.0

    def test_protocol_phase(self):
        from sozo_protocol.models import ProtocolPhase, ProtocolStep, StepType, Modality, SOZOPhase
        phase = ProtocolPhase(
            sozo_phase=SOZOPhase.OPTIMIZE,
            label="O — Optimize",
            steps=[
                ProtocolStep(step_type=StepType.PULSE, modality=Modality.TDCS, duration_ms=1200000),
            ],
        )
        assert phase.sozo_phase == SOZOPhase.OPTIMIZE
        assert phase.modalities_used == ["tdcs"]
        assert phase.total_duration_ms == 1200000

    def test_protocol_sequence(self):
        from sozo_protocol.models import (
            ProtocolSequence, ProtocolPhase, ProtocolStep, StepType, Modality, SOZOPhase
        )
        seq = ProtocolSequence(
            name="PD SOZO Session",
            condition_slug="parkinsons",
            phases=[
                ProtocolPhase(sozo_phase=SOZOPhase.STABILIZE, steps=[
                    ProtocolStep(step_type=StepType.PULSE, modality=Modality.TAVNS, duration_ms=900000),
                ]),
                ProtocolPhase(sozo_phase=SOZOPhase.OPTIMIZE, steps=[
                    ProtocolStep(step_type=StepType.PULSE, modality=Modality.TDCS, duration_ms=1200000),
                ]),
                ProtocolPhase(sozo_phase=SOZOPhase.ZONE, steps=[
                    ProtocolStep(step_type=StepType.PULSE, modality=Modality.TPS, duration_ms=1500000),
                ]),
            ],
        )
        assert len(seq.phases) == 3
        assert set(seq.all_modalities) == {"tavns", "tdcs", "tps"}
        assert seq.total_duration_min == 60.0  # 15 + 20 + 25 minutes

    def test_personalized_protocol(self):
        from sozo_protocol.models import PersonalizedProtocol, FilterCoefficients
        pp = PersonalizedProtocol(
            base_sequence_id="seq-abc",
            patient_id="patient-001",
            eeg_filter=FilterCoefficients(
                b=[0.0009, 0, -0.0019, 0, 0.0009],
                a=[1, -3.86, 5.64, -3.69, 0.92],
                filter_type="bandpass",
                frequency_band="beta",
            ),
            target_phase_degrees=210.0,
            phenotype_slug="tremor_dominant",
        )
        assert pp.eeg_filter.frequency_band == "beta"
        assert len(pp.eeg_filter.b) == 5


# ── Protocol Builder Tests ───────────────────────────────────────────────


class TestProtocolBuilder:
    def test_build_sozo_sequence_from_knowledge(self):
        from sozo_protocol.builder import build_sozo_sequence
        seq = build_sozo_sequence("parkinsons", "fellow")
        assert seq.condition_slug == "parkinsons"
        assert len(seq.phases) >= 3  # pre + at least S/O/Z + post
        assert seq.total_duration_min > 0

    def test_sozo_phases_ordered(self):
        from sozo_protocol.builder import build_sozo_sequence
        from sozo_protocol.models import SOZOPhase
        seq = build_sozo_sequence("parkinsons", "fellow")
        phase_order = [p.sozo_phase for p in seq.phases]
        # PRE should come before STABILIZE/OPTIMIZE/ZONE
        if SOZOPhase.PRE in phase_order and SOZOPhase.ZONE in phase_order:
            assert phase_order.index(SOZOPhase.PRE) < phase_order.index(SOZOPhase.ZONE)

    def test_build_for_depression(self):
        from sozo_protocol.builder import build_sozo_sequence
        seq = build_sozo_sequence("depression", "fellow")
        assert seq.condition_slug == "depression"
        assert len(seq.all_steps) >= 3

    def test_build_includes_pre_post(self):
        from sozo_protocol.builder import build_sozo_sequence
        from sozo_protocol.models import SOZOPhase
        seq = build_sozo_sequence("parkinsons", "fellow")
        phases = [p.sozo_phase for p in seq.phases]
        assert SOZOPhase.PRE in phases
        assert SOZOPhase.POST in phases


# ── Device Adapter Tests ─────────────────────────────────────────────────


class TestDeviceAdapters:
    def test_simulator_capabilities(self):
        from sozo_device.adapters.simulator import SimulatorAdapter
        adapter = SimulatorAdapter()
        caps = adapter.get_capabilities()
        assert caps.device_type == "simulator"
        assert caps.intensity_max == 5.0
        assert caps.supports_impedance is True

    def test_neurolith_capabilities(self):
        from sozo_device.adapters.neurolith import NeurolithAdapter
        adapter = NeurolithAdapter()
        caps = adapter.get_capabilities()
        assert caps.modality == "tps"
        assert "OFF-LABEL" in caps.regulatory_status

    def test_hdckit_capabilities(self):
        from sozo_device.adapters.hdckit import HDCkitAdapter
        adapter = HDCkitAdapter()
        caps = adapter.get_capabilities()
        assert caps.modality == "tdcs"
        assert caps.intensity_max == 2.0

    def test_alpha_stim_capabilities(self):
        from sozo_device.adapters.alpha_stim import AlphaStimAdapter
        adapter = AlphaStimAdapter()
        caps = adapter.get_capabilities()
        assert caps.modality == "ces"
        assert "FDA-cleared" in caps.regulatory_status

    def test_capability_validation_pass(self):
        from sozo_device.adapters.simulator import SimulatorAdapter
        from sozo_protocol.models import ProtocolStep, StepType, Modality
        adapter = SimulatorAdapter()
        step = ProtocolStep(step_type=StepType.PULSE, modality=Modality.TDCS, intensity_ma=2.0)
        violations = adapter.validate_step(step)
        assert len(violations) == 0

    def test_capability_validation_fail(self):
        from sozo_device.adapters.simulator import SimulatorAdapter
        from sozo_protocol.models import ProtocolStep, StepType, Modality
        adapter = SimulatorAdapter()
        step = ProtocolStep(step_type=StepType.PULSE, modality=Modality.TDCS, intensity_ma=10.0)
        violations = adapter.validate_step(step)
        assert len(violations) > 0
        assert "outside range" in violations[0]


# ── Device Registry Tests ────────────────────────────────────────────────


class TestDeviceRegistry:
    def test_create_simulator(self):
        from sozo_device.registry import DeviceAdapterRegistry
        reg = DeviceAdapterRegistry()
        adapter = reg.create("simulator")
        assert adapter.device_type == "simulator"

    def test_create_by_modality(self):
        from sozo_device.registry import DeviceAdapterRegistry
        reg = DeviceAdapterRegistry()
        adapter = reg.create_for_modality("tps")
        assert adapter.device_type == "neurolith"

    def test_list_devices(self):
        from sozo_device.registry import DeviceAdapterRegistry
        reg = DeviceAdapterRegistry()
        devices = reg.list_devices()
        assert "simulator" in devices
        assert "neurolith" in devices
        assert "hdckit" in devices

    def test_unknown_device_raises(self):
        from sozo_device.registry import DeviceAdapterRegistry
        reg = DeviceAdapterRegistry()
        with pytest.raises(ValueError, match="Unknown device type"):
            reg.create("nonexistent")


# ── Event Bus Tests ──────────────────────────────────────────────────────


class TestEventBus:
    def test_publish_and_drain(self):
        from sozo_device.streaming.event_bus import SessionEventBus, SessionEvent, EventChannel
        bus = SessionEventBus()

        async def _test():
            await bus.publish(SessionEvent(channel=EventChannel.AUDIT, event_type="test"))
            await bus.publish(SessionEvent(channel=EventChannel.SAFETY, event_type="alert"))
            audits = await bus.drain(EventChannel.AUDIT)
            assert len(audits) == 1
            assert audits[0].event_type == "test"

        asyncio.run(_test())

    def test_channel_isolation(self):
        from sozo_device.streaming.event_bus import SessionEventBus, SessionEvent, EventChannel
        bus = SessionEventBus()

        async def _test():
            await bus.publish(SessionEvent(channel=EventChannel.NEURAL, event_type="data"))
            safety = await bus.drain(EventChannel.SAFETY)
            neural = await bus.drain(EventChannel.NEURAL)
            assert len(safety) == 0
            assert len(neural) == 1

        asyncio.run(_test())

    def test_total_pending(self):
        from sozo_device.streaming.event_bus import SessionEventBus, SessionEvent, EventChannel
        bus = SessionEventBus()

        async def _test():
            await bus.publish(SessionEvent(channel=EventChannel.AUDIT, event_type="a"))
            await bus.publish(SessionEvent(channel=EventChannel.AUDIT, event_type="b"))
            counts = bus.total_pending()
            assert counts["audit"] == 2
            assert counts["neural"] == 0

        asyncio.run(_test())


# ── Session Manager Tests ────────────────────────────────────────────────


class TestSessionManager:
    def test_run_session_with_simulator(self):
        from sozo_session.manager import SessionManager
        from sozo_protocol.builder import build_sozo_sequence

        async def _test():
            mgr = SessionManager()
            seq = build_sozo_sequence("parkinsons", "fellow")
            result = await mgr.run_session("patient-001", seq, use_simulator=True)
            assert result.success
            assert result.status == "completed"
            assert result.steps_completed > 0
            assert len(result.audit_log) > 0

        asyncio.run(_test())

    def test_session_has_impedance(self):
        from sozo_session.manager import SessionManager
        from sozo_protocol.builder import build_sozo_sequence

        async def _test():
            mgr = SessionManager()
            seq = build_sozo_sequence("parkinsons", "fellow")
            result = await mgr.run_session("patient-002", seq, use_simulator=True)
            assert len(result.impedance_pre) > 0

        asyncio.run(_test())

    def test_session_audit_trail(self):
        from sozo_session.manager import SessionManager
        from sozo_protocol.builder import build_sozo_sequence

        async def _test():
            mgr = SessionManager()
            seq = build_sozo_sequence("depression", "fellow")
            result = await mgr.run_session("patient-003", seq, use_simulator=True)
            assert result.success
            # Audit should include session_start, device_connected, phase/step events
            event_types = [e["event"] for e in result.audit_log]
            assert "session_start" in event_types
            assert "session_complete" in event_types

        asyncio.run(_test())


# ── Safety Monitor Tests ─────────────────────────────────────────────────


class TestSafetyMonitor:
    def test_impedance_check_pass(self):
        from sozo_session.manager import SafetyMonitor
        monitor = SafetyMonitor(max_impedance_kohm=10.0)
        assert monitor.check_impedance({"ch1": 3.0, "ch2": 5.0}) is True

    def test_impedance_check_fail(self):
        from sozo_session.manager import SafetyMonitor
        monitor = SafetyMonitor(max_impedance_kohm=5.0)
        assert monitor.check_impedance({"ch1": 3.0, "ch2": 8.0}) is False
        assert len(monitor.adverse_events) == 1
