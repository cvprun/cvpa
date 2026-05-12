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


if __name__ == "__main__":
    main()
