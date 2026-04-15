# -*- coding: utf-8 -*-

from unittest import TestCase, main
from unittest.mock import AsyncMock, patch


class AgentClientSyncTestCase(TestCase):
    @patch("cvpa.apps.agent.client.WebSocketClient")
    @patch("cvpa.apps.agent.client.ServiceManager")
    @patch("cvpa.apps.agent.client.MessageDispatcher")
    def test_init(self, mock_disp, mock_mgr, mock_ws):
        from cvpa.apps.agent.client import AgentClient

        client = AgentClient("ws://test", "slug", "token")
        self.assertIsNotNone(client.services)


@patch("cvpa.apps.agent.client.WebSocketClient")
@patch("cvpa.apps.agent.client.ServiceManager")
@patch("cvpa.apps.agent.client.MessageDispatcher")
async def test_start(mock_disp, mock_mgr_cls, mock_ws_cls):
    from cvpa.apps.agent.client import AgentClient

    mock_mgr = AsyncMock()
    mock_ws = AsyncMock()
    mock_mgr_cls.return_value = mock_mgr
    mock_ws_cls.return_value = mock_ws

    client = AgentClient("ws://test", "slug", "token")
    client._services = mock_mgr
    client._client = mock_ws
    await client.start()
    mock_mgr.start_all.assert_awaited_once()
    mock_ws.start.assert_awaited_once()


@patch("cvpa.apps.agent.client.WebSocketClient")
@patch("cvpa.apps.agent.client.ServiceManager")
@patch("cvpa.apps.agent.client.MessageDispatcher")
async def test_stop(mock_disp, mock_mgr_cls, mock_ws_cls):
    from cvpa.apps.agent.client import AgentClient

    mock_mgr = AsyncMock()
    mock_ws = AsyncMock()
    mock_mgr_cls.return_value = mock_mgr
    mock_ws_cls.return_value = mock_ws

    client = AgentClient("ws://test", "slug", "token")
    client._services = mock_mgr
    client._client = mock_ws
    await client.stop()
    mock_mgr.stop_all.assert_awaited_once()
    mock_ws.stop.assert_awaited_once()


@patch("cvpa.apps.agent.client.WebSocketClient")
@patch("cvpa.apps.agent.client.ServiceManager")
@patch("cvpa.apps.agent.client.MessageDispatcher")
async def test_request_ticket(mock_disp, mock_mgr, mock_ws):
    from cvpa.apps.agent.client import AgentClient

    client = AgentClient("ws://test", "slug", "token")
    with patch("cvpa.apps.agent.client.request_ticket", return_value="ws://url"):
        result = await client._request_ticket()
        assert result == "ws://url"


if __name__ == "__main__":
    main()
