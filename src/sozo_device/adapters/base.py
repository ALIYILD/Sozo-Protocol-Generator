"""
Device Adapter ABC — the hardware abstraction boundary.

Inspired by OMNI-BIC's BICListener which translates vendor SDK callbacks
into gRPC-compatible data. In Sozo, DeviceAdapter is the seam between
vendor SDKs (NEUROLITH, HDCkit, Alpha-Stim) and the platform.

Everything ABOVE this boundary speaks Sozo types (ProtocolStep, DeviceSample).
Everything BELOW speaks vendor SDK types.

Usage:
    adapter = DeviceAdapterRegistry.create("neurolith", device_id="NL-001")
    await adapter.connect()
    caps = adapter.get_capabilities()
    result = await adapter.execute_step(step)
    async for sample in adapter.stream_data():
        process(sample)
"""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, AsyncIterator, Optional

from sozo_protocol.models import ProtocolStep


# ── Device Data Models ────────────────────────────────────────────────────


class DeviceState(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    STIMULATING = "stimulating"
    ERROR = "error"
    DISPOSED = "disposed"


@dataclass
class DeviceCapabilities:
    """Self-describing device capabilities (like OMNI-BIC's bicChannelInfo).

    Each device adapter reports what it can do, with safe parameter ranges.
    Clients and safety monitors use this to validate protocol steps.
    """
    device_type: str = ""
    modality: str = ""
    manufacturer: str = ""
    model: str = ""
    firmware_version: str = ""
    regulatory_status: str = ""

    # Channels
    channel_count: int = 0
    stimulation_channels: int = 0
    measurement_channels: int = 0
    sampling_rate_hz: int = 0

    # Parameter ranges (safe operating envelope)
    intensity_min: float = 0.0
    intensity_max: float = 0.0
    intensity_unit: str = "mA"  # mA, mJ/mm², µA
    frequency_min_hz: float = 0.0
    frequency_max_hz: float = 0.0
    pulse_width_min_us: int = 0
    pulse_width_max_us: int = 0
    max_duration_min: float = 60.0

    # Capabilities
    supports_impedance: bool = False
    supports_streaming: bool = False
    supports_closed_loop: bool = False
    supports_ramp: bool = True

    def validate_step(self, step: ProtocolStep) -> list[str]:
        """Validate a protocol step against device capabilities. Returns list of violations."""
        violations = []
        if step.intensity_ma is not None:
            if step.intensity_ma < self.intensity_min or step.intensity_ma > self.intensity_max:
                violations.append(
                    f"Intensity {step.intensity_ma} {self.intensity_unit} outside range "
                    f"[{self.intensity_min}, {self.intensity_max}]"
                )
        if step.frequency_hz is not None:
            if self.frequency_max_hz > 0 and step.frequency_hz > self.frequency_max_hz:
                violations.append(f"Frequency {step.frequency_hz} Hz exceeds max {self.frequency_max_hz}")
        if step.duration_min is not None and isinstance(step.duration_min, (int, float)) and step.duration_min > self.max_duration_min:
            violations.append(f"Duration {step.duration_min} min exceeds max {self.max_duration_min}")
        return violations


@dataclass
class DeviceSample:
    """One data sample from a device (neural, impedance, temperature, etc.)."""
    sample_type: str = "neural"  # neural, impedance, temperature, humidity, status
    timestamp: str = ""
    channel: int = 0
    value: float = 0.0
    values: list[float] = field(default_factory=list)  # Multi-channel
    unit: str = ""
    is_stimulating: bool = False
    sample_counter: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


@dataclass
class StepResult:
    """Result of executing one protocol step on a device."""
    step_id: str = ""
    success: bool = False
    actual_duration_ms: int = 0
    actual_intensity: float = 0.0
    impedance_before: dict[str, float] = field(default_factory=dict)
    impedance_after: dict[str, float] = field(default_factory=dict)
    samples_collected: int = 0
    adverse_events: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: str = ""


# ── Device Adapter ABC ───────────────────────────────────────────────────


class DeviceAdapter(ABC):
    """Abstract boundary between vendor SDK and Sozo platform.

    Concrete implementations exist for each hardware vendor:
    - NeurolithAdapter (TPS)
    - HDCkitAdapter (tDCS)
    - AlphaStimAdapter (CES)
    - SimulatorAdapter (testing)
    """

    def __init__(self, device_id: str = ""):
        self.device_id = device_id or f"dev-{uuid.uuid4().hex[:8]}"
        self.state = DeviceState.DISCONNECTED
        self._capabilities: Optional[DeviceCapabilities] = None

    @property
    @abstractmethod
    def device_type(self) -> str:
        """Device type identifier (e.g., 'neurolith', 'hdckit')."""
        ...

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the device. Returns True on success."""
        ...

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the device."""
        ...

    @abstractmethod
    async def execute_step(self, step: ProtocolStep) -> StepResult:
        """Execute a single protocol step."""
        ...

    @abstractmethod
    async def emergency_stop(self) -> bool:
        """Immediately stop all stimulation. Safety-critical."""
        ...

    @abstractmethod
    async def get_impedance(self) -> dict[str, float]:
        """Get electrode impedance readings (electrode → kΩ)."""
        ...

    @abstractmethod
    def get_capabilities(self) -> DeviceCapabilities:
        """Get device capabilities and safe parameter ranges."""
        ...

    async def stream_data(self) -> AsyncIterator[DeviceSample]:
        """Stream real-time data from the device. Override in subclasses."""
        return
        yield  # Make it a generator

    def validate_step(self, step: ProtocolStep) -> list[str]:
        """Validate a protocol step against this device's capabilities."""
        caps = self.get_capabilities()
        return caps.validate_step(step)
