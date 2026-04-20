# -*- coding: utf-8 -*-

import json
from logging import DEBUG, getLogger
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from cvpa.client.ticket import TicketError, _mask_token, _truncate, request_ticket
from cvpa.ws.protocol import ErrorCode


def _make_resp(status, body, content_type="application/json"):
    mock_resp = MagicMock()
    mock_resp.status = status
    mock_resp.read.return_value = body
    mock_resp.getheader.return_value = content_type
    return mock_resp


class RequestTicketTestCase(TestCase):
    @patch("cvpa.client.ticket.HTTPSConnection")
    def test_https(self, mock_conn_cls):
        mock_conn = MagicMock()
        mock_conn.getresponse.return_value = _make_resp(
            200, json.dumps({"url": "wss://ws"}).encode()
        )
        mock_conn_cls.return_value = mock_conn

        result = request_ticket("https://example.com", "slug1", "token1")
        self.assertEqual(result, "wss://ws")
        mock_conn_cls.assert_called_once_with("example.com")
        mock_conn.close.assert_called_once()

    @patch("cvpa.client.ticket.HTTPConnection")
    def test_http(self, mock_conn_cls):
        mock_conn = MagicMock()
        mock_conn.getresponse.return_value = _make_resp(
            200, json.dumps({"url": "ws://ws"}).encode()
        )
        mock_conn_cls.return_value = mock_conn

        result = request_ticket("http://example.com", "slug1", "token1")
        self.assertEqual(result, "ws://ws")
        mock_conn_cls.assert_called_once_with("example.com")

    @patch("cvpa.client.ticket.HTTPConnection")
    def test_error_status_plain(self, mock_conn_cls):
        mock_conn = MagicMock()
        mock_conn.getresponse.return_value = _make_resp(
            403, b"Forbidden", content_type="text/plain"
        )
        mock_conn_cls.return_value = mock_conn

        with self.assertRaises(TicketError) as ctx:
            request_ticket("http://example.com", "slug1", "token1")
        self.assertEqual(ctx.exception.status, 403)
        self.assertIsNone(ctx.exception.code)
        self.assertIn("Forbidden", ctx.exception.message)

    @patch("cvpa.client.ticket.HTTPConnection")
    def test_error_status_json_code(self, mock_conn_cls):
        mock_conn = MagicMock()
        body = json.dumps(
            {"code": ErrorCode.AGENT_SUSPENDED, "message": "suspended"}
        ).encode()
        mock_conn.getresponse.return_value = _make_resp(
            403, body, content_type="application/json"
        )
        mock_conn_cls.return_value = mock_conn

        with self.assertRaises(TicketError) as ctx:
            request_ticket("http://example.com", "slug1", "token1")
        self.assertEqual(ctx.exception.status, 403)
        self.assertEqual(ctx.exception.code, ErrorCode.AGENT_SUSPENDED)
        self.assertTrue(ctx.exception.is_suspended)
        self.assertFalse(ctx.exception.is_terminating)

    @patch("cvpa.client.ticket.HTTPConnection")
    def test_error_status_json_terminating(self, mock_conn_cls):
        mock_conn = MagicMock()
        body = json.dumps(
            {"code": ErrorCode.AGENT_TERMINATING, "message": "bye"}
        ).encode()
        mock_conn.getresponse.return_value = _make_resp(
            403, body, content_type="application/json"
        )
        mock_conn_cls.return_value = mock_conn

        with self.assertRaises(TicketError) as ctx:
            request_ticket("http://example.com", "slug1", "token1")
        self.assertTrue(ctx.exception.is_terminating)

    @patch("cvpa.client.ticket.HTTPConnection")
    def test_error_status_auth(self, mock_conn_cls):
        mock_conn = MagicMock()
        mock_conn.getresponse.return_value = _make_resp(
            401, b"nope", content_type="text/plain"
        )
        mock_conn_cls.return_value = mock_conn

        with self.assertRaises(TicketError) as ctx:
            request_ticket("http://example.com", "slug1", "token1")
        self.assertTrue(ctx.exception.is_auth_failure)

    @patch("cvpa.client.ticket.HTTPConnection")
    def test_error_status_not_found(self, mock_conn_cls):
        mock_conn = MagicMock()
        mock_conn.getresponse.return_value = _make_resp(
            404, b"gone", content_type="text/plain"
        )
        mock_conn_cls.return_value = mock_conn

        with self.assertRaises(TicketError) as ctx:
            request_ticket("http://example.com", "slug1", "token1")
        self.assertTrue(ctx.exception.is_not_found)

    @patch("cvpa.client.ticket.HTTPConnection")
    def test_error_status_retryable(self, mock_conn_cls):
        mock_conn = MagicMock()
        mock_conn.getresponse.return_value = _make_resp(
            503, b"busy", content_type="text/plain"
        )
        mock_conn_cls.return_value = mock_conn

        with self.assertRaises(TicketError) as ctx:
            request_ticket("http://example.com", "slug1", "token1")
        self.assertTrue(ctx.exception.is_retryable)

    @patch("cvpa.client.ticket.HTTPConnection")
    def test_custom_logger_debug(self, mock_conn_cls):
        mock_conn = MagicMock()
        mock_conn.getresponse.return_value = _make_resp(
            200, json.dumps({"url": "ws://ws"}).encode()
        )
        mock_conn_cls.return_value = mock_conn

        logger = getLogger("test.cvpa.ticket")
        logger.setLevel(DEBUG)
        with self.assertLogs(logger, level="DEBUG") as cm:
            request_ticket(
                "http://example.com",
                "slug1",
                "abcd1234efgh5678",
                logger=logger,
            )
        joined = "\n".join(cm.output)
        self.assertIn("POST http://example.com/api/agents/slug1/connect", joined)
        self.assertIn("abcd...5678", joined)
        self.assertNotIn("abcd1234efgh5678", joined)
        self.assertIn("status=200", joined)

    @patch("cvpa.client.ticket.HTTPConnection")
    def test_error_truncates_large_body(self, mock_conn_cls):
        mock_conn = MagicMock()
        large_body = ("X" * 2000).encode()
        mock_conn.getresponse.return_value = _make_resp(
            500, large_body, content_type="text/html"
        )
        mock_conn_cls.return_value = mock_conn

        with self.assertRaises(TicketError) as ctx:
            request_ticket("http://example.com", "slug1", "token1")
        self.assertIn("truncated", ctx.exception.message)


class MaskTokenTestCase(TestCase):
    def test_short_token_masked_entirely(self):
        self.assertEqual(_mask_token("abc"), "***")
        self.assertEqual(_mask_token("12345678"), "***")

    def test_long_token_keeps_edges(self):
        self.assertEqual(_mask_token("abcdefghij"), "abcd...ghij")


class TruncateTestCase(TestCase):
    def test_short_unchanged(self):
        self.assertEqual(_truncate("hello", limit=10), "hello")

    def test_long_truncated(self):
        result = _truncate("x" * 20, limit=5)
        self.assertTrue(result.startswith("xxxxx"))
        self.assertIn("truncated", result)


class TicketErrorStrTestCase(TestCase):
    def test_str_with_code(self):
        err = TicketError(403, "agent_suspended", "suspended")
        self.assertIn("403", str(err))
        self.assertIn("agent_suspended", str(err))

    def test_str_without_code(self):
        err = TicketError(500, None, "boom")
        self.assertIn("500", str(err))
        self.assertIn("boom", str(err))


if __name__ == "__main__":
    main()
