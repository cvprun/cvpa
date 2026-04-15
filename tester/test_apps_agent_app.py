# -*- coding: utf-8 -*-

from unittest import TestCase, main
from unittest.mock import AsyncMock, patch


class AgentApplicationSyncTestCase(TestCase):
    @patch("cvpa.apps.agent.app.AgentClient")
    def test_init(self, mock_client_cls):
        from cvpa.apps.agent.app import AgentApplication

        app = AgentApplication("ws://test", "slug", "token")
        self.assertEqual(app._uri, "ws://test")
        self.assertEqual(app._slug, "slug")
        mock_client_cls.assert_called_once()

    @patch("cvpa.apps.agent.app.aio_run")
    @patch("cvpa.apps.agent.app.AgentClient")
    def test_start(self, mock_client_cls, mock_aio_run):
        from cvpa.apps.agent.app import AgentApplication

        app = AgentApplication("ws://test", "slug", "token")
        app.start()
        mock_aio_run.assert_called_once()

    @patch("cvpa.apps.agent.app.aio_run", side_effect=KeyboardInterrupt)
    @patch("cvpa.apps.agent.app.AgentClient")
    def test_start_keyboard_interrupt(self, mock_client_cls, mock_aio_run):
        from cvpa.apps.agent.app import AgentApplication

        app = AgentApplication("ws://test", "slug", "token")
        app.start()


@patch("cvpa.apps.agent.app.AgentClient")
async def test_on_main(mock_client_cls):
    from cvpa.apps.agent.app import AgentApplication

    mock_client = AsyncMock()
    mock_client_cls.return_value = mock_client

    app = AgentApplication("ws://test", "slug", "token")
    await app.on_main()
    mock_client.start.assert_awaited_once()
    mock_client.stop.assert_awaited_once()


@patch("cvpa.apps.agent.app.AgentClient")
async def test_on_main_error(mock_client_cls):
    import pytest

    from cvpa.apps.agent.app import AgentApplication

    mock_client = AsyncMock()
    mock_client.start.side_effect = RuntimeError("boom")
    mock_client_cls.return_value = mock_client

    app = AgentApplication("ws://test", "slug", "token")
    with pytest.raises(RuntimeError):
        await app.on_main()
    mock_client.stop.assert_awaited_once()


if __name__ == "__main__":
    main()
