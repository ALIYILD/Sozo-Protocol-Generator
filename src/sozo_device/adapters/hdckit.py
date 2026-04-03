"""
HDCkit tDCS Device Adapter — interface for Newronika HDCkit.

CE Class IIa multi-channel HD-tDCS system.
This adapter translates Sozo ProtocolSteps into HDCkit SDK commands.

NOTE: Structural stub — real implementation requires Newronika SDK.
"""
from __future__ import annotations

from sozo_protocol.models import ProtocolStep
from .base import DeviceAdapter, DeviceCapabilities, DeviceState, StepResult


class HDCkitAdapter(DeviceAdapter):

    @property
    def device_type(self) -> str:
        return "hdckit"

    async def connect(self) -> bool:
        self.state = DeviceState.CONNECTED
        return True

    async def disconnect(self) -> bool:
        self.state = DeviceState.DISCONNECTED
        return True

    async def execute_step(self, step: ProtocolStep) -> StepResult:
        return StepResult(step_id=step.step_id, success=False, error="HDCkit SDK not connected — stub adapter")

    async def emergency_stop(self) -> bool:
        self.state = DeviceState.CONNECTED
        return True

    async def get_impedance(self) -> dict[str, float]:
        return {}

    def get_capabilities(self) -> DeviceCapabilities:
        return DeviceCapabilities(
            device_type="hdckit", modality="tdcs", manufacturer="Newronika",
            model="HDCkit", regulatory_status="CE Class IIa",
            channel_count=16, stimulation_channels=2, measurement_channels=16,
            intensity_min=0.0, intensity_max=2.0, intensity_unit="mA",
            max_duration_min=40.0, supports_impedance=True, supports_ramp=True,
        )
