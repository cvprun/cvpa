# -*- coding: utf-8 -*-

from asyncio import Event, Queue
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuntimeContext:
    stop_event: Event = field(default_factory=Event)
    command_queue: Queue[Any] = field(default_factory=Queue)
