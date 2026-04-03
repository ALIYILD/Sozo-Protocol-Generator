"""
Device Adapter Registry — factory pattern for creating device adapters.

Inspired by OMNI-BIC's IImplantFactory which is created at startup
and distributed to services. In Sozo, the registry maps modality/device
types to concrete adapter classes.

Usage:
    from sozo_device.registry import DeviceAdapterRegistry

    registry = DeviceAdapterRegistry()
    adapter = registry.create("neurolith", device_id="NL-001")
    adapter = registry.create_for_modality("tps")
"""
from __future__ import annotations

import logging
from typing import Optional

from .adapters.base import DeviceAdapter

logger = logging.getLogger(__name__)

# Lazy import mapping to avoid loading all vendor SDKs at startup
_ADAPTER_CLASSES = {
    "simulator": "sozo_device.adapters.simulator.SimulatorAdapter",
    "neurolith": "sozo_device.adapters.neurolith.NeurolithAdapter",
    "hdckit": "sozo_device.adapters.hdckit.HDCkitAdapter",
    "alpha_stim": "sozo_device.adapters.alpha_stim.AlphaStimAdapter",
}

# Modality → default device type mapping
_MODALITY_DEVICES = {
    "tps": "neurolith",
    "tdcs": "hdckit",
    "ces": "alpha_stim",
    "tavns": "simulator",  # No dedicated adapter yet
    "eeg": "simulator",
}


class DeviceAdapterRegistry:
    """Factory for creating device adapters by type or modality."""

    def __init__(self):
        self._instances: dict[str, DeviceAdapter] = {}

    def create(self, device_type: str, device_id: str = "") -> DeviceAdapter:
        """Create a device adapter by device type."""
        class_path = _ADAPTER_CLASSES.get(device_type)
        if not class_path:
            raise ValueError(f"Unknown device type: {device_type}. Available: {list(_ADAPTER_CLASSES.keys())}")

        module_path, class_name = class_path.rsplit(".", 1)
        import importlib
        module = importlib.import_module(module_path)
        adapter_class = getattr(module, class_name)

        adapter = adapter_class(device_id=device_id)
        self._instances[adapter.device_id] = adapter
        logger.info(f"Created adapter: {device_type} ({adapter.device_id})")
        return adapter

    def create_for_modality(self, modality: str, device_id: str = "") -> DeviceAdapter:
        """Create the default device adapter for a modality."""
        device_type = _MODALITY_DEVICES.get(modality)
        if not device_type:
            raise ValueError(f"No default device for modality: {modality}")
        return self.create(device_type, device_id)

    def get(self, device_id: str) -> Optional[DeviceAdapter]:
        """Get an existing adapter instance by device ID."""
        return self._instances.get(device_id)

    def list_devices(self) -> list[str]:
        """List all available device types."""
        return list(_ADAPTER_CLASSES.keys())

    def list_connected(self) -> list[str]:
        """List all connected device IDs."""
        from .adapters.base import DeviceState
        return [
            did for did, adapter in self._instances.items()
            if adapter.state in (DeviceState.CONNECTED, DeviceState.STIMULATING)
        ]
