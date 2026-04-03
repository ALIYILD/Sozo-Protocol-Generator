"""
NEUROLITH TPS Device Adapter — interface for Storz Medical NEUROLITH.

CE-marked for Alzheimer's disease. OFF-LABEL for all other conditions.
This adapter translates Sozo ProtocolSteps into NEUROLITH SDK commands.

NOTE: This is a structural stub. Real implementation requires the
NEUROLITH SDK and device hardware. The adapter pattern is ready for
vendor integration.
"""
from __future__ import annotations

from typing import AsyncIterator

from sozo_protocol.models import ProtocolStep
from .base import (
    DeviceAdapter,
    DeviceCapabilities,
    DeviceSample,
    DeviceState,
    StepResult,
)


class NeurolithAdapter(DeviceAdapter):
    """Adapter for NEUROLITH TPS (Transcranial Pulse Stimulation)."""

    @property
    def device_type(self) -> str:
        return "neurolith"

    async def connect(self) -> bool:
        # TODO: Initialize NEUROLITH SDK connection
        self.state = DeviceState.CONNECTED
        return True

    async def disconnect(self) -> bool:
        self.state = DeviceState.DISCONNECTED
        return True

    async def execute_step(self, step: ProtocolStep) -> StepResult:
        # TODO: Translate ProtocolStep → NEUROLITH SDK commands
        # Pulse parameters: energy_mj, frequency_hz, pulse_count, target ROI
        return StepResult(
            step_id=step.step_id,
            success=False,
            error="NEUROLITH SDK not connected — stub adapter",
        )

    async def emergency_stop(self) -> bool:
        self.state = DeviceState.CONNECTED
        return True

    async def get_impedance(self) -> dict[str, float]:
        return {}  # TPS does not use electrode impedance

    def get_capabilities(self) -> DeviceCapabilities:
        return DeviceCapabilities(
            device_type="neurolith",
            modality="tps",
            manufacturer="Storz Medical",
            model="NEUROLITH",
            regulatory_status="CE-marked for Alzheimer's; OFF-LABEL for all other conditions",
            intensity_min=0.1,
            intensity_max=0.3,
            intensity_unit="mJ/mm²",
            frequency_min_hz=1.0,
            frequency_max_hz=10.0,
            max_duration_min=30.0,
            supports_impedance=False,
            supports_streaming=False,
            supports_closed_loop=False,
        )
