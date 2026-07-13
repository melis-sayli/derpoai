from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from enum import Enum
from typing import Any, Awaitable, Callable

logger = logging.getLogger("derpoai.events")


class Event(str, Enum):
    SENSOR_READING = "sensor.reading"
    RISK_DETECTED = "ai.risk_detected"
    MOVEMENT_DETECTED = "ai.movement_detected"
    FORECAST_READY = "ai.forecast_ready"
    STOCK_CHANGED = "supply.stock_changed"
    SECURITY_ALERT = "security.alert"


Handler = Callable[[dict[str, Any]], Awaitable[None] | None]


class EventBus:
    def __init__(self) -> None:
        self._subs: dict[Event, list[Handler]] = defaultdict(list)

    def subscribe(self, event: Event, handler: Handler) -> None:
        """Bir modül, ilgilendiği olaya kaydolur."""
        self._subs[event].append(handler)
        logger.debug("abone: %s -> %s", event, handler.__name__)

    async def publish(self, event: Event, payload: dict[str, Any]) -> None:
        """Olayı tüm abonelere dağıtır."""
        for handler in self._subs[event]:
            try:
                result = handler(payload)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                logger.exception("olay işleyici hatası: %s", event)


bus = EventBus()