# -*- coding: utf-8 -*-

from unittest import TestCase, main

from pydantic import ValidationError

from cvpa.ws.protocol.messages.control import (
    AgentRotate,
    AgentShutdown,
    AgentSuspend,
)
from cvpa.ws.protocol.messages.error import ServerError
from cvpa.ws.protocol.messages.handshake import AgentHello, ServerHello
from cvpa.ws.protocol.messages.heartbeat import HeartbeatPing, HeartbeatPong


class HandshakeMessagesTestCase(TestCase):
    def test_server_hello_all_optional(self):
        msg = ServerHello.model_validate({})
        self.assertIsNone(msg.session_id)
        self.assertIsNone(msg.heartbeat_interval_ms)
        self.assertIsNone(msg.heartbeat_timeout_ms)

    def test_server_hello_full_payload(self):
        msg = ServerHello.model_validate(
            {
                "session_id": "s1",
                "heartbeat_interval_ms": 15000,
                "heartbeat_timeout_ms": 45000,
            }
        )
        self.assertEqual(msg.session_id, "s1")
        self.assertEqual(msg.heartbeat_interval_ms, 15000)
        self.assertEqual(msg.heartbeat_timeout_ms, 45000)

    def test_agent_hello_required_fields(self):
        msg = AgentHello.model_validate(
            {"version": "1.0", "capabilities": ["a", "b"], "pid": 42}
        )
        self.assertEqual(msg.version, "1.0")
        self.assertEqual(msg.capabilities, ["a", "b"])
        self.assertEqual(msg.pid, 42)

    def test_agent_hello_missing_version_raises(self):
        with self.assertRaises(ValidationError):
            AgentHello.model_validate({"capabilities": [], "pid": 1})


class HeartbeatMessagesTestCase(TestCase):
    def test_heartbeat_ping_requires_seq(self):
        msg = HeartbeatPing.model_validate({"seq": 7})
        self.assertEqual(msg.seq, 7)
        with self.assertRaises(ValidationError):
            HeartbeatPing.model_validate({})

    def test_heartbeat_pong_seq_optional(self):
        self.assertIsNone(HeartbeatPong.model_validate({}).seq)
        self.assertEqual(HeartbeatPong.model_validate({"seq": 3}).seq, 3)


class ControlMessagesTestCase(TestCase):
    def test_agent_shutdown_deadline_optional(self):
        self.assertIsNone(AgentShutdown.model_validate({}).deadline_ms)
        self.assertEqual(
            AgentShutdown.model_validate({"deadline_ms": 5000}).deadline_ms,
            5000,
        )

    def test_agent_suspend_empty(self):
        AgentSuspend.model_validate({})

    def test_agent_rotate_empty(self):
        AgentRotate.model_validate({})


class ErrorMessageTestCase(TestCase):
    def test_server_error_required_fields(self):
        msg = ServerError.model_validate({"code": "x", "message": "boom"})
        self.assertEqual(msg.code, "x")
        self.assertEqual(msg.message, "boom")

    def test_server_error_missing_field_raises(self):
        with self.assertRaises(ValidationError):
            ServerError.model_validate({"code": "x"})


if __name__ == "__main__":
    main()
