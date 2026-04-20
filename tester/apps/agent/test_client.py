# -*- coding: utf-8 -*-

from unittest import TestCase, main
from unittest.mock import AsyncMock, patch


class AgentClientSyncTestCase(TestCase):
    @patch("cvpa.apps.agent.client.AgentConnection")
    @patch("cvpa.apps.agent.client.ServiceManager")
    def test_init_default(self, mock_mgr, mock_conn):
        from cvpa.apps.agent.client import AgentClient

        client = AgentClient("http://test", "slug", "token")
        self.assertIsNotNone(client.services)
        self.assertIsNotNone(client.connection)
        mock_conn.assert_called_once()
        kwargs = mock_conn.call_args.kwargs
        self.assertEqual(kwargs["uri"], "http://test")
        self.assertEqual(kwargs["slug"], "slug")
        self.assertEqual(kwargs["token"], "token")
        self.assertFalse(kwargs["legacy_protocol"])

    @patch("cvpa.apps.agent.client.AgentConnection")
    @patch("cvpa.apps.agent.client.ServiceManager")
    def test_init_legacy(self, mock_mgr, mock_conn):
        from cvpa.apps.agent.client import AgentClient

        AgentClient("http://test", "slug", "token", legacy_protocol=True)
        kwargs = mock_conn.call_args.kwargs
        self.assertTrue(kwargs["legacy_protocol"])


@patch("cvpa.apps.agent.client.AgentConnection")
@patch("cvpa.apps.agent.client.ServiceManager")
async def test_start(mock_mgr_cls, mock_conn_cls):
    from cvpa.apps.agent.client import AgentClient

    mock_mgr = AsyncMock()
    mock_conn = AsyncMock()
    mock_mgr_cls.return_value = mock_mgr
    mock_conn_cls.return_value = mock_conn

    client = AgentClient("http://test", "slug", "token")
    await client.start()
    mock_conn.start.assert_awaited_once()


@patch("cvpa.apps.agent.client.AgentConnection")
@patch("cvpa.apps.agent.client.ServiceManager")
async def test_stop(mock_mgr_cls, mock_conn_cls):
    from cvpa.apps.agent.client import AgentClient

    mock_mgr = AsyncMock()
    mock_conn = AsyncMock()
    mock_mgr_cls.return_value = mock_mgr
    mock_conn_cls.return_value = mock_conn

    client = AgentClient("http://test", "slug", "token")
    await client.stop()
    mock_conn.stop.assert_awaited_once()
    mock_mgr.stop_all.assert_awaited_once()


if __name__ == "__main__":
    main()
