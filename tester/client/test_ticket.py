# -*- coding: utf-8 -*-

import json
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from cvpa.client.ticket import request_ticket


class RequestTicketTestCase(TestCase):
    @patch("cvpa.client.ticket.HTTPSConnection")
    def test_https(self, mock_conn_cls):
        mock_conn = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"url": "wss://ws"}).encode()
        mock_conn.getresponse.return_value = mock_resp
        mock_conn_cls.return_value = mock_conn

        result = request_ticket("https://example.com", "slug1", "token1")
        self.assertEqual(result, "wss://ws")
        mock_conn_cls.assert_called_once_with("example.com")
        mock_conn.close.assert_called_once()

    @patch("cvpa.client.ticket.HTTPConnection")
    def test_http(self, mock_conn_cls):
        mock_conn = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"url": "ws://ws"}).encode()
        mock_conn.getresponse.return_value = mock_resp
        mock_conn_cls.return_value = mock_conn

        result = request_ticket("http://example.com", "slug1", "token1")
        self.assertEqual(result, "ws://ws")
        mock_conn_cls.assert_called_once_with("example.com")

    @patch("cvpa.client.ticket.HTTPConnection")
    def test_error_status(self, mock_conn_cls):
        mock_conn = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status = 403
        mock_resp.read.return_value = b"Forbidden"
        mock_conn.getresponse.return_value = mock_resp
        mock_conn_cls.return_value = mock_conn

        with self.assertRaises(RuntimeError):
            request_ticket("http://example.com", "slug1", "token1")
        mock_conn.close.assert_called_once()


if __name__ == "__main__":
    main()
