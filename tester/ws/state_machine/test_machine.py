# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.ws.state_machine import (
    AgentEvent,
    AgentState,
    ConnectionStateMachine,
    InvalidTransitionError,
)


class TransitionTableTestCase(TestCase):
    """§12.2 전이표를 모두 검증한다."""

    CASES = [
        (AgentState.IDLE, AgentEvent.START, AgentState.CONNECTING),
        (AgentState.CONNECTING, AgentEvent.TICKET_OK, AgentState.HANDSHAKING),
        (
            AgentState.CONNECTING,
            AgentEvent.TICKET_AUTH_FAIL,
            AgentState.TERMINATED,
        ),
        (
            AgentState.CONNECTING,
            AgentEvent.TICKET_SUSPENDED,
            AgentState.SUSPENDED,
        ),
        (
            AgentState.CONNECTING,
            AgentEvent.TICKET_TERMINATING,
            AgentState.TERMINATED,
        ),
        (
            AgentState.CONNECTING,
            AgentEvent.TICKET_NOT_FOUND,
            AgentState.TERMINATED,
        ),
        (
            AgentState.CONNECTING,
            AgentEvent.TICKET_RETRYABLE,
            AgentState.BACKOFF,
        ),
        (AgentState.CONNECTING, AgentEvent.WS_CLOSED, AgentState.BACKOFF),
        (AgentState.HANDSHAKING, AgentEvent.SERVER_HELLO, AgentState.ACTIVE),
        (
            AgentState.HANDSHAKING,
            AgentEvent.HANDSHAKE_TIMEOUT,
            AgentState.BACKOFF,
        ),
        (AgentState.HANDSHAKING, AgentEvent.WS_CLOSED, AgentState.BACKOFF),
        (AgentState.ACTIVE, AgentEvent.HEARTBEAT_PONG, AgentState.ACTIVE),
        (AgentState.ACTIVE, AgentEvent.HEARTBEAT_TIMEOUT, AgentState.BACKOFF),
        (AgentState.ACTIVE, AgentEvent.AGENT_SHUTDOWN, AgentState.STOPPING),
        (AgentState.ACTIVE, AgentEvent.AGENT_SUSPEND, AgentState.SUSPENDED),
        (AgentState.ACTIVE, AgentEvent.AGENT_ROTATE, AgentState.TERMINATED),
        (AgentState.ACTIVE, AgentEvent.WS_CLOSED, AgentState.BACKOFF),
        (AgentState.STOPPING, AgentEvent.CLEANUP_DONE, AgentState.STOPPED),
        (AgentState.STOPPING, AgentEvent.CLEANUP_DEADLINE, AgentState.STOPPED),
        (AgentState.BACKOFF, AgentEvent.BACKOFF_EXPIRED, AgentState.CONNECTING),
    ]

    def test_all_transitions(self):
        for src, event, dst in self.CASES:
            with self.subTest(src=src, event=event):
                sm = ConnectionStateMachine(initial=src)
                self.assertTrue(sm.can(event))
                self.assertEqual(sm.fire(event), dst)
                self.assertEqual(sm.state, dst)

    def test_peek_without_firing(self):
        self.assertEqual(
            ConnectionStateMachine.peek(AgentState.ACTIVE, AgentEvent.AGENT_SHUTDOWN),
            AgentState.STOPPING,
        )
        self.assertIsNone(
            ConnectionStateMachine.peek(AgentState.STOPPED, AgentEvent.HEARTBEAT_PONG)
        )


class InvalidTransitionTestCase(TestCase):
    def test_raises_for_unknown(self):
        sm = ConnectionStateMachine(initial=AgentState.IDLE)
        with self.assertRaises(InvalidTransitionError) as ctx:
            sm.fire(AgentEvent.SERVER_HELLO)
        self.assertEqual(ctx.exception.state, AgentState.IDLE)
        self.assertEqual(ctx.exception.event, AgentEvent.SERVER_HELLO)

    def test_can_false_for_unknown(self):
        sm = ConnectionStateMachine(initial=AgentState.STOPPED)
        self.assertFalse(sm.can(AgentEvent.HEARTBEAT_PONG))

    def test_stopped_has_no_auto_transition(self):
        sm = ConnectionStateMachine(initial=AgentState.STOPPED)
        # STOPPED는 외부 재시작 신호 대기. 내부 이벤트로 전이 불가.
        for event in AgentEvent:
            self.assertFalse(sm.can(event), f"{event} should not fire from STOPPED")

    def test_suspended_has_no_auto_transition(self):
        sm = ConnectionStateMachine(initial=AgentState.SUSPENDED)
        for event in AgentEvent:
            self.assertFalse(sm.can(event))

    def test_terminated_is_terminal(self):
        sm = ConnectionStateMachine(initial=AgentState.TERMINATED)
        self.assertTrue(sm.is_terminal())
        for event in AgentEvent:
            self.assertFalse(sm.can(event))


class ResetTestCase(TestCase):
    def test_reset_defaults_to_idle(self):
        sm = ConnectionStateMachine(initial=AgentState.ACTIVE)
        sm.reset()
        self.assertIs(sm.state, AgentState.IDLE)

    def test_reset_custom(self):
        sm = ConnectionStateMachine()
        sm.reset(AgentState.BACKOFF)
        self.assertIs(sm.state, AgentState.BACKOFF)


class LoggerTestCase(TestCase):
    def test_logger_records_transition(self):
        from logging import DEBUG, getLogger

        logger = getLogger("test.cvpa.state_machine")
        logger.setLevel(DEBUG)
        sm = ConnectionStateMachine(initial=AgentState.IDLE, logger=logger)
        with self.assertLogs(logger, level="INFO") as cm:
            sm.fire(AgentEvent.START)
        self.assertTrue(any("agent.transition" in line for line in cm.output))


if __name__ == "__main__":
    main()
