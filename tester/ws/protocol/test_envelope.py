# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.ws.protocol.envelope import Envelope


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
