"""
Alpha-Stim CES Device Adapter — interface for Alpha-Stim AID.

FDA-cleared for anxiety, depression, insomnia.
NOTE: Structural stub — real implementation requires Alpha-Stim SDK/API.
"""
from __future__ import annotations

from sozo_protocol.models import ProtocolStep
from .base import DeviceAdapter, DeviceCapabilities, DeviceState, StepResult


class AlphaStimAdapter(DeviceAdapter):

    @property
    def device_type(self) -> str:
        return "alpha_stim"

    async def connect(self) -> bool:
        self.state = DeviceState.CONNECTED
        return True

    async def disconnect(self) -> bool:
        self.state = DeviceState.DISCONNECTED
        return True

    async def execute_step(self, step: ProtocolStep) -> StepResult:
        return StepResult(step_id=step.step_id, success=False, error="Alpha-Stim not connected — stub adapter")

    async def emergency_stop(self) -> bool:
        self.state = DeviceState.CONNECTED
        return True

    async def get_impedance(self) -> dict[str, float]:
        return {}

    def get_capabilities(self) -> DeviceCapabilities:
        return DeviceCapabilities(
            device_type="alpha_stim", modality="ces", manufacturer="Electromedical Products International",
            model="Alpha-Stim AID", regulatory_status="FDA-cleared (anxiety, depression, insomnia)",
            stimulation_channels=1, intensity_min=0.01, intensity_max=0.6,
            intensity_unit="mA", frequency_min_hz=0.5, frequency_max_hz=100.0,
            max_duration_min=60.0, supports_impedance=False,
        )
