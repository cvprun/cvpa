# -*- coding: utf-8 -*-

from unittest.mock import AsyncMock, MagicMock, patch

from cvpa.ws.client import WebSocketClient


def _make_client(**kwargs):
    get_url = kwargs.get("get_url", AsyncMock(return_value="ws://test"))
    on_message = kwargs.get("on_message", AsyncMock())
    logger = kwargs.get("logger", MagicMock())
    return WebSocketClient(get_url=get_url, on_message=on_message, logger=logger)


@patch("cvpa.ws.client.connect", new_callable=AsyncMock)
async def test_connect(mock_connect):
    mock_ws = MagicMock()
    mock_connect.return_value = mock_ws
    client = _make_client()
    await client._connect()
    assert client._ws is mock_ws


async def test_send():
    client = _make_client()
    client._ws = AsyncMock()
    await client.send("hello")
    client._ws.send.assert_awaited_once_with("hello")


async def test_send_json():
    client = _make_client()
    client._ws = AsyncMock()
    await client.send_json({"type": "x"})
    client._ws.send.assert_awaited_once()
    payload = client._ws.send.await_args.args[0]
    assert '"type"' in payload


async def test_listen():
    client = _make_client()
    on_message = AsyncMock()
    client._on_message = on_message

    messages = ["msg1", "msg2"]

    class FakeWs:
        def __aiter__(self):
            return self

        def __init__(self):
            self._iter = iter(messages)

        async def __anext__(self):
            try:
                return next(self._iter)
            except StopIteration:
                raise StopAsyncIteration

    client._ws = FakeWs()
    await client._listen()
    assert on_message.await_count == 2


@patch("cvpa.ws.client.connect", new_callable=AsyncMock)
async def test_start_single_connect_and_exit(mock_connect):
    """start() 는 1회 연결 후 리슨 종료 시 반환한다 (재연결 없음)."""
    client = _make_client()

    class FakeWs:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise StopAsyncIteration

        async def close(self, code=1000, reason=""):
            return None

    mock_connect.return_value = FakeWs()
    await client.start()
    # No reconnect attempted.
    assert mock_connect.await_count == 1


async def test_close():
    client = _make_client()
    ws = AsyncMock()
    client._ws = ws
    await client.close(code=4001, reason="heartbeat_timeout")
    ws.close.assert_awaited_once_with(code=4001, reason="heartbeat_timeout")
    assert client._ws is None


async def test_close_no_ws():
    client = _make_client()
    await client.close()
    assert client._ws is None


async def test_close_swallows_exception():
    client = _make_client()
    ws = AsyncMock()
    ws.close.side_effect = RuntimeError("boom")
    client._ws = ws
    await client.close()
    assert client._ws is None


async def test_stop():
    client = _make_client()
    client._ws = AsyncMock()
    await client.stop()
    assert client._stop_event.is_set()
    assert client._ws is None


async def test_stop_no_ws():
    client = _make_client()
    await client.stop()
    assert client._stop_event.is_set()


@patch("cvpa.ws.client.connect", new_callable=AsyncMock)
async def test_connect_no_logger(mock_connect):
    mock_connect.return_value = MagicMock()
    client = WebSocketClient(
        get_url=AsyncMock(return_value="ws://test"),
        on_message=AsyncMock(),
    )
    await client._connect()
