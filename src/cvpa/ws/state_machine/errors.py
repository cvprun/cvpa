# -*- coding: utf-8 -*-

from cvpa.ws.state_machine.event import AgentEvent
from cvpa.ws.state_machine.state import AgentState


class InvalidTransitionError(Exception):
    def __init__(self, state: AgentState, event: AgentEvent) -> None:
        super().__init__(f"Invalid transition: {state.value} -{event.value}->")
        self.state = state
        self.event = event
