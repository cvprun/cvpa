# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.ws.protocol import CloseCode


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


if __name__ == "__main__":
    main()
