"""
Simulator Device Adapter — test/development adapter that simulates hardware.

Produces realistic-looking data without requiring physical devices.
Used for protocol development, testing, and demonstration.
"""
from __future__ import annotations

import asyncio
import math
import random
from typing import AsyncIterator

from sozo_protocol.models import ProtocolStep
from .base import (
    DeviceAdapter,
    DeviceCapabilities,
    DeviceSample,
    DeviceState,
    StepResult,
)


class SimulatorAdapter(DeviceAdapter):
    """Simulates a neuromodulation device for testing."""

    @property
    def device_type(self) -> str:
        return "simulator"

    async def connect(self) -> bool:
        self.state = DeviceState.CONNECTED
        return True

    async def disconnect(self) -> bool:
        self.state = DeviceState.DISCONNECTED
        return True

    async def execute_step(self, step: ProtocolStep) -> StepResult:
        """Simulate step execution with realistic timing."""
        self.state = DeviceState.STIMULATING

        # Simulate step duration (capped at 100ms for testing)
        duration_ms = min(step.duration_total_ms, 100)
        if duration_ms > 0:
            await asyncio.sleep(duration_ms / 1000.0)

        self.state = DeviceState.CONNECTED
        return StepResult(
            step_id=step.step_id,
            success=True,
            actual_duration_ms=duration_ms,
            actual_intensity=step.intensity_ma or step.intensity_mj or 0.0,
            samples_collected=int(duration_ms / 10),
        )

    async def emergency_stop(self) -> bool:
        self.state = DeviceState.CONNECTED
        return True

    async def get_impedance(self) -> dict[str, float]:
        """Simulate impedance readings (1-8 kΩ typical)."""
        return {
            f"ch{i}": round(random.uniform(1.0, 8.0), 1)
            for i in range(1, 9)
        }

    def get_capabilities(self) -> DeviceCapabilities:
        return DeviceCapabilities(
            device_type="simulator",
            modality="multimodal",
            manufacturer="SOZO Brain Center",
            model="Simulator v1",
            channel_count=8,
            stimulation_channels=4,
            measurement_channels=8,
            sampling_rate_hz=1000,
            intensity_min=0.0,
            intensity_max=5.0,
            intensity_unit="mA",
            frequency_min_hz=0.1,
            frequency_max_hz=100.0,
            max_duration_min=60.0,
            supports_impedance=True,
            supports_streaming=True,
            supports_closed_loop=True,
        )

    async def stream_data(self) -> AsyncIterator[DeviceSample]:
        """Simulate neural data stream with synthetic oscillations."""
        counter = 0
        while self.state in (DeviceState.CONNECTED, DeviceState.STIMULATING):
            t = counter / 1000.0  # seconds
            # Simulate multi-channel neural data with beta oscillation
            values = [
                round(math.sin(2 * math.pi * 20 * t + i * 0.5) * 50
                       + random.gauss(0, 10), 2)
                for i in range(8)
            ]
            yield DeviceSample(
                sample_type="neural",
                channel=0,
                values=values,
                is_stimulating=self.state == DeviceState.STIMULATING,
                sample_counter=counter,
            )
            counter += 1
            await asyncio.sleep(0.001)  # 1kHz sampling
