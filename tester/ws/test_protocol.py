# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.ws.protocol import (
    GRACEFUL_SHUTDOWN_MS,
    HEARTBEAT_INTERVAL_MS,
    HEARTBEAT_TIMEOUT_MS,
    RECONNECT_INITIAL_MS,
    RECONNECT_JITTER_RATIO,
    RECONNECT_MAX_MS,
    TICKET_TTL_MS,
    CloseCode,
    Envelope,
    ErrorCode,
)


class ConstantsTestCase(TestCase):
    def test_heartbeat_values(self):
        self.assertEqual(HEARTBEAT_INTERVAL_MS, 15_000)
        self.assertEqual(HEARTBEAT_TIMEOUT_MS, 45_000)
        self.assertEqual(HEARTBEAT_TIMEOUT_MS, HEARTBEAT_INTERVAL_MS * 3)

    def test_reconnect_values(self):
        self.assertEqual(RECONNECT_INITIAL_MS, 1_000)
        self.assertEqual(RECONNECT_MAX_MS, 60_000)
        self.assertAlmostEqual(RECONNECT_JITTER_RATIO, 0.2)

    def test_ticket_and_shutdown(self):
        self.assertEqual(TICKET_TTL_MS, 30_000)
        self.assertEqual(GRACEFUL_SHUTDOWN_MS, 10_000)


class CloseCodeTestCase(TestCase):
    def test_values(self):
        self.assertEqual(int(CloseCode.NORMAL), 1000)
        self.assertEqual(int(CloseCode.HEARTBEAT_TIMEOUT), 4001)
        self.assertEqual(int(CloseCode.SHUTDOWN_REQUESTED), 4002)
        self.assertEqual(int(CloseCode.SHUTDOWN_FORCED), 4003)
        self.assertEqual(int(CloseCode.SUSPENDED), 4010)
        self.assertEqual(int(CloseCode.TOKEN_ROTATED), 4011)
        self.assertEqual(int(CloseCode.TOKEN_INVALID), 4012)
        self.assertEqual(int(CloseCode.TERMINATING), 4020)
        self.assertEqual(int(CloseCode.DUPLICATE_SESSION), 4030)


class ErrorCodeTestCase(TestCase):
    def test_values(self):
        self.assertEqual(ErrorCode.AGENT_SUSPENDED, "agent_suspended")
        self.assertEqual(ErrorCode.AGENT_TERMINATING, "agent_terminating")
        self.assertEqual(ErrorCode.INVALID_TOKEN, "invalid_token")


class EnvelopeTestCase(TestCase):
    def test_to_dict_minimal(self):
        env = Envelope(type="agent.hello")
        self.assertEqual(env.to_dict(), {"type": "agent.hello"})

    def test_to_dict_with_data(self):
        env = Envelope(type="agent.hello", data={"version": "1.0"})
        self.assertEqual(
            env.to_dict(),
            {"type": "agent.hello", "data": {"version": "1.0"}},
        )

    def test_to_dict_with_id_and_ts(self):
        env = Envelope(
            type="heartbeat.ping",
            data={"seq": 1},
            id="abc",
            ts="2026-04-19T10:15:30Z",
        )
        out = env.to_dict()
        self.assertEqual(out["id"], "abc")
        self.assertEqual(out["ts"], "2026-04-19T10:15:30Z")

    def test_from_dict(self):
        env = Envelope.from_dict(
            {"type": "x", "data": {"a": 1}, "id": "id1", "ts": "t1"}
        )
        self.assertEqual(env.type, "x")
        self.assertEqual(env.data, {"a": 1})
        self.assertEqual(env.id, "id1")
        self.assertEqual(env.ts, "t1")

    def test_from_dict_missing_optional(self):
        env = Envelope.from_dict({"type": "x"})
        self.assertEqual(env.type, "x")
        self.assertEqual(env.data, {})
        self.assertIsNone(env.id)
        self.assertIsNone(env.ts)


if __name__ == "__main__":
    main()
