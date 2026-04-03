"""
Session Event Bus — typed streaming channels for session telemetry.

Inspired by OMNI-BIC's 6 independent producer-consumer queues
(neural, temperature, humidity, connection, error, power).

For Sozo, we have typed channels that decouple data production
from consumption, with backpressure-aware bounded queues.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class EventChannel(str, Enum):
    NEURAL = "neural"
    IMPEDANCE = "impedance"
    STIMULATION = "stimulation"
    SAFETY = "safety"
    AUDIT = "audit"
    OUTCOME = "outcome"


@dataclass
class SessionEvent:
    """One event on the session event bus."""
    channel: EventChannel
    event_type: str = ""
    timestamp: str = ""
    session_id: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info, warning, critical

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class SessionEventBus:
    """Typed event bus with bounded async queues per channel.

    Each channel has an independent asyncio.Queue so consumers
    on one channel don't block others.
    """

    def __init__(self, max_queue_size: int = 1000):
        self._queues: dict[EventChannel, asyncio.Queue] = {}
        self._subscribers: dict[EventChannel, list[Callable]] = {}
        self._max_size = max_queue_size
        self._running = False

        for ch in EventChannel:
            self._queues[ch] = asyncio.Queue(maxsize=max_queue_size)
            self._subscribers[ch] = []

    async def publish(self, event: SessionEvent):
        """Publish an event to its channel queue."""
        queue = self._queues.get(event.channel)
        if queue is None:
            return
        try:
            queue.put_nowait(event)
        except asyncio.QueueFull:
            logger.warning(f"Event bus queue full on {event.channel.value} — dropping event")

    async def subscribe(self, channel: EventChannel) -> SessionEvent:
        """Wait for and return the next event on a channel."""
        return await self._queues[channel].get()

    def register_handler(self, channel: EventChannel, handler: Callable):
        """Register a synchronous handler for events on a channel."""
        self._subscribers[channel].append(handler)

    async def drain(self, channel: EventChannel, max_items: int = 100) -> list[SessionEvent]:
        """Drain up to max_items from a channel queue."""
        events = []
        queue = self._queues[channel]
        while not queue.empty() and len(events) < max_items:
            events.append(queue.get_nowait())
        return events

    def pending_count(self, channel: EventChannel) -> int:
        return self._queues[channel].qsize()

    def total_pending(self) -> dict[str, int]:
        return {ch.value: self._queues[ch].qsize() for ch in EventChannel}
