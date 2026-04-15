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
@patch("cvpa.ws.client.sleep", new_callable=AsyncMock)
async def test_start_reconnect(mock_sleep, mock_connect):
    call_count = 0

    async def connect_side_effect(url):
        nonlocal call_count
        call_count += 1
        raise ConnectionError("fail")

    mock_connect.side_effect = connect_side_effect
    client = _make_client()

    async def stop_after_delay(*args):
        if call_count >= 2:
            client._stop_event.set()

    mock_sleep.side_effect = stop_after_delay
    await client.start()
    assert call_count >= 2


@patch("cvpa.ws.client.connect", new_callable=AsyncMock)
async def test_start_stop_during_exception(mock_connect):
    client = _make_client()
    client._stop_event.set()
    mock_connect.side_effect = ConnectionError("fail")
    await client.start()


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


@patch("cvpa.ws.client.connect", new_callable=AsyncMock)
async def test_start_success_then_stop(mock_connect):
    """Test successful connect + listen path (covers backoff reset line 52-53)."""
    client = _make_client()

    class FakeWs:
        def __aiter__(self):
            return self

        async def __anext__(self):
            client._stop_event.set()
            raise StopAsyncIteration

    mock_connect.return_value = FakeWs()
    await client.start()
    assert client._stop_event.is_set()


@patch("cvpa.ws.client.connect", new_callable=AsyncMock)
async def test_start_exception_with_stop_event(mock_connect):
    """Exception raised while stop_event is already set -> break at line 56."""
    client = _make_client()

    async def fail_and_stop(url):
        client._stop_event.set()
        raise ConnectionError("fail")

    mock_connect.side_effect = fail_and_stop
    await client.start()
    assert client._stop_event.is_set()


@patch("cvpa.ws.client.connect", new_callable=AsyncMock)
@patch("cvpa.ws.client.sleep", new_callable=AsyncMock)
async def test_start_exception_no_logger(mock_sleep, mock_connect):
    """Covers exception path without logger."""
    client = WebSocketClient(
        get_url=AsyncMock(return_value="ws://test"),
        on_message=AsyncMock(),
    )
    call_count = 0

    async def fail(url):
        nonlocal call_count
        call_count += 1
        raise ConnectionError("fail")

    mock_connect.side_effect = fail

    async def stop(*args):
        if call_count >= 1:
            client._stop_event.set()

    mock_sleep.side_effect = stop
    await client.start()
