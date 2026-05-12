# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.ws.protocol.error_code import ErrorCode


class ErrorCodeTestCase(TestCase):
    def test_values(self):
        self.assertEqual(ErrorCode.AGENT_SUSPENDED, "agent_suspended")
        self.assertEqual(ErrorCode.AGENT_TERMINATING, "agent_terminating")
        self.assertEqual(ErrorCode.INVALID_TOKEN, "invalid_token")


if __name__ == "__main__":
    main()
